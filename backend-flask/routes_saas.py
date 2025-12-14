"""
SaaS API Routes - Tenants, Subscriptions, and Billing
"""
from flask import Blueprint, request, jsonify, current_app
from models_saas import Tenant, SubscriptionPlan, Subscription, Invoice, TenantInvitation
from models import User
from main import db
from datetime import datetime, timedelta
import secrets
import re

saas_bp = Blueprint('saas', __name__, url_prefix='/api/saas')

# ============================================
# SUBSCRIPTION PLANS
# ============================================

@saas_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get all active subscription plans"""
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    return jsonify([plan.to_dict() for plan in plans])

@saas_bp.route('/plans/<slug>', methods=['GET'])
def get_plan(slug):
    """Get specific plan by slug"""
    plan = SubscriptionPlan.query.filter_by(slug=slug).first_or_404()
    return jsonify(plan.to_dict())

# ============================================
# TENANT MANAGEMENT
# ============================================

@saas_bp.route('/tenants', methods=['POST'])
def create_tenant():
    """Create new tenant (organization signup)"""
    data = request.get_json()
    
    # Validate required fields
    required = ['name', 'owner_email', 'owner_password']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Generate slug from name
    slug = re.sub(r'[^a-z0-9]+', '-', data['name'].lower()).strip('-')
    
    # Check if slug already exists
    if Tenant.query.filter_by(slug=slug).first():
        slug = f"{slug}-{secrets.token_hex(3)}"
    
    # Get starter plan (trial)
    starter_plan = SubscriptionPlan.query.filter_by(slug='starter').first()
    
    try:
        # Create tenant
        tenant = Tenant(
            name=data['name'],
            slug=slug,
            plan_id=starter_plan.id if starter_plan else None,
            status='trial',
            trial_ends_at=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(tenant)
        db.session.flush()  # Get tenant.id
        
        # Create owner user
        from werkzeug.security import generate_password_hash
        owner = User(
            username=data['owner_email'].split('@')[0],
            email=data['owner_email'],
            password_hash=generate_password_hash(data['owner_password']),
            tenant_id=tenant.id,
            role_in_tenant='owner',
            is_admin=False,
            active=True
        )
        db.session.add(owner)
        
        # Create subscription
        subscription = Subscription(
            tenant_id=tenant.id,
            plan_id=starter_plan.id if starter_plan else None,
            status='trialing',
            current_period_start=datetime.utcnow(),
            current_period_end=tenant.trial_ends_at
        )
        db.session.add(subscription)
        
        tenant.current_users = 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'tenant': tenant.to_dict(),
            'message': 'Tenant criado com sucesso! Trial de 14 dias iniciado.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating tenant: {e}")
        return jsonify({'error': 'Erro ao criar tenant'}), 500

@saas_bp.route('/tenants/<slug>', methods=['GET'])
def get_tenant(slug):
    """Get tenant by slug"""
    tenant = Tenant.query.filter_by(slug=slug).first_or_404()
    return jsonify(tenant.to_dict())

@saas_bp.route('/tenants/<slug>', methods=['PATCH'])
def update_tenant(slug):
    """Update tenant settings"""
    tenant = Tenant.query.filter_by(slug=slug).first_or_404()
    data = request.get_json()
    
    # Updatable fields
    if 'name' in data:
        tenant.name = data['name']
    if 'domain' in data:
        tenant.domain = data['domain']
    if 'logo_url' in data:
        tenant.logo_url = data['logo_url']
    if 'primary_color' in data:
        tenant.primary_color = data['primary_color']
    if 'metadata' in data:
        tenant.metadata = data['metadata']
    
    tenant.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(tenant.to_dict())

# ============================================
# TENANT USERS
# ============================================

@saas_bp.route('/tenants/<slug>/users', methods=['GET'])
def get_tenant_users(slug):
    """Get all users in a tenant"""
    tenant = Tenant.query.filter_by(slug=slug).first_or_404()
    users = User.query.filter_by(tenant_id=tenant.id).all()
    
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role_in_tenant,
        'active': u.active,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in users])

@saas_bp.route('/tenants/<slug>/users/invite', methods=['POST'])
def invite_user(slug):
    """Invite user to tenant"""
    tenant = Tenant.query.filter_by(slug=slug).first_or_404()
    data = request.get_json()
    
    email = data.get('email')
    role = data.get('role', 'member')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email, tenant_id=tenant.id).first()
    if existing_user:
        return jsonify({'error': 'User already exists in this tenant'}), 400
    
    # Check limits
    if not tenant.is_within_limits('users'):
        return jsonify({'error': 'User limit reached for current plan'}), 403
    
    # Create invitation
    token = secrets.token_urlsafe(32)
    invitation = TenantInvitation(
        tenant_id=tenant.id,
        email=email,
        role=role,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.session.add(invitation)
    db.session.commit()
    
    # TODO: Send email with invitation link
    invitation_link = f"https://legalpro.com/accept-invite/{token}"
    
    return jsonify({
        'success': True,
        'invitation_link': invitation_link,
        'message': f'Convite enviado para {email}'
    })

# ============================================
# SUBSCRIPTIONS & BILLING
# ============================================

@saas_bp.route('/tenants/<slug>/subscription', methods=['GET'])
def get_subscription(slug):
    """Get tenant's current subscription"""
    tenant = Tenant.query.filter_by(slug=slug).first_or_404()
    
    if not tenant.subscription:
        return jsonify({'error': 'No subscription found'}), 404
    
    return jsonify(tenant.subscription.to_dict())

@saas_bp.route('/tenants/<slug>/subscription/upgrade', methods=['POST'])
def upgrade_subscription(slug):
    """Upgrade tenant to a different plan"""
    tenant = Tenant.query.filter_by(slug=slug).first_or_404()
    data = request.get_json()
    
    new_plan_slug = data.get('plan_slug')
    if not new_plan_slug:
        return jsonify({'error': 'plan_slug is required'}), 400
    
    new_plan = SubscriptionPlan.query.filter_by(slug=new_plan_slug).first_or_404()
    
    # Update tenant plan
    tenant.plan_id = new_plan.id
    tenant.status = 'active'
    
    # Update subscription
    if tenant.subscription:
        tenant.subscription.plan_id = new_plan.id
        tenant.subscription.status = 'active'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Plan upgraded to {new_plan.name}',
        'tenant': tenant.to_dict()
    })

@saas_bp.route('/tenants/<slug>/invoices', methods=['GET'])
def get_invoices(slug):
    """Get all invoices for a tenant"""
    tenant = Tenant.query.filter_by(slug=slug).first_or_404()
    invoices = Invoice.query.filter_by(tenant_id=tenant.id).order_by(Invoice.created_at.desc()).all()
    
    return jsonify([inv.to_dict() for inv in invoices])

# ============================================
# SUPER ADMIN ROUTES
# ============================================

@saas_bp.route('/admin/tenants', methods=['GET'])
def admin_list_tenants():
    """List all tenants (Super Admin only)"""
    # TODO: Add super admin authentication check
    
    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tenants])

@saas_bp.route('/admin/stats', methods=['GET'])
def admin_stats():
    """Get platform statistics (Super Admin only)"""
    # TODO: Add super admin authentication check
    
    total_tenants = Tenant.query.count()
    active_tenants = Tenant.query.filter_by(status='active').count()
    trial_tenants = Tenant.query.filter_by(status='trial').count()
    
    # Calculate MRR (Monthly Recurring Revenue)
    active_subs = Subscription.query.filter_by(status='active').all()
    mrr = sum([s.tenant.plan.price_monthly for s in active_subs if s.tenant.plan])
    
    return jsonify({
        'total_tenants': total_tenants,
        'active_tenants': active_tenants,
        'trial_tenants': trial_tenants,
        'mrr': float(mrr),
        'arr': float(mrr * 12)
    })

def register_saas_routes(app):
    """Register SaaS blueprint"""
    app.register_blueprint(saas_bp)
    print("✅ SaaS API routes registered")
