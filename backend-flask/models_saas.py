"""
SaaS Models V2 for Legal Pro
Arquitetura: USER → TENANCY → CLIENT
Multi-tenant SaaS with client management
"""
from main import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class SubscriptionPlan(db.Model):
    """Subscription plans available"""
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    price_monthly = db.Column(db.Numeric(10, 2), default=0)
    price_yearly = db.Column(db.Numeric(10, 2), default=0)
    features = db.Column(JSONB, default=[])
    limits = db.Column(JSONB, default={})
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenancies = db.relationship('Tenancy', backref='plan', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price_monthly': float(self.price_monthly),
            'price_yearly': float(self.price_yearly),
            'features': self.features,
            'limits': self.limits,
            'is_active': self.is_active
        }


class Tenancy(db.Model):
    """Tenancy - Instância multi-tenant do SaaS"""
    __tablename__ = 'tenancy'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    domain = db.Column(db.String(255))
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'))
    status = db.Column(db.String(50), default='trial')
    trial_ends_at = db.Column(db.DateTime)
    
    # Branding
    logo_url = db.Column(db.String(500))
    primary_color = db.Column(db.String(7), default='#2563eb')
    
    # Settings
    settings = db.Column(JSONB, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clients = db.relationship('Client', backref='tenancy', lazy='dynamic', cascade='all, delete-orphan')
    users = db.relationship('User', backref='tenancy', lazy='dynamic')
    subscription = db.relationship('Subscription', backref='tenancy', uselist=False)
    
    def get_stats(self):
        """Get tenancy statistics"""
        return {
            'total_clients': self.clients.count(),
            'active_clients': self.clients.filter_by(status='active').count(),
            'total_users': self.users.count(),
        }
    
    def is_within_limits(self, resource_type):
        """Check if tenancy is within plan limits"""
        if not self.plan:
            return False
            
        limits = self.plan.limits
        stats = self.get_stats()
        
        if resource_type == 'users':
            max_users = limits.get('max_users', 0)
            return max_users == -1 or stats['total_users'] < max_users
            
        elif resource_type == 'clients':
            max_clients = limits.get('max_clients', -1)
            return max_clients == -1 or stats['total_clients'] < max_clients
            
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'domain': self.domain,
            'status': self.status,
            'plan': self.plan.to_dict() if self.plan else None,
            'trial_ends_at': self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'stats': self.get_stats(),
            'created_at': self.created_at.isoformat()
        }


class Client(db.Model):
    """Client - Clientes/Empresas atendidas pela Tenancy"""
    __tablename__ = 'client'
    
    id = db.Column(db.Integer, primary_key=True)
    tenancy_id = db.Column(db.Integer, db.ForeignKey('tenancy.id'), nullable=False)
    
    # Informações básicas
    name = db.Column(db.String(255), nullable=False)
    legal_name = db.Column(db.String(255))
    document_number = db.Column(db.String(50))  # CNPJ/CPF
    document_type = db.Column(db.String(20))    # cnpj, cpf
    
    # Contato
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    
    # Endereço
    address_street = db.Column(db.String(255))
    address_number = db.Column(db.String(50))
    address_complement = db.Column(db.String(100))
    address_neighborhood = db.Column(db.String(100))
    address_city = db.Column(db.String(100))
    address_state = db.Column(db.String(2))
    address_zip = db.Column(db.String(20))
    address_country = db.Column(db.String(50), default='Brasil')
    
    # Informações comerciais
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))  # startup, small, medium, large, enterprise
    
    # Status
    status = db.Column(db.String(50), default='active')  # active, inactive, suspended
    
    # Metadata
    client_metadata = db.Column(JSONB, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_accesses = db.relationship('UserClientAccess', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenancy_id': self.tenancy_id,
            'name': self.name,
            'legal_name': self.legal_name,
            'document_number': self.document_number,
            'document_type': self.document_type,
            'email': self.email,
            'phone': self.phone,
            'address': {
                'street': self.address_street,
                'number': self.address_number,
                'complement': self.address_complement,
                'neighborhood': self.address_neighborhood,
                'city': self.address_city,
                'state': self.address_state,
                'zip': self.address_zip,
                'country': self.address_country
            },
            'industry': self.industry,
            'size': self.size,
            'status': self.status,
            'metadata': self.client_metadata,
            'created_at': self.created_at.isoformat()
        }


class UserClientAccess(db.Model):
    """Relacionamento N:N entre Users e Clients"""
    __tablename__ = 'user_client_access'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    role = db.Column(db.String(50), default='viewer')  # owner, editor, viewer
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    granted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='client_accesses')
    granter = db.relationship('User', foreign_keys=[granted_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'client_id': self.client_id,
            'role': self.role,
            'granted_at': self.granted_at.isoformat(),
            'granted_by': self.granted_by
        }


class Subscription(db.Model):
    """Tenancy subscriptions"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    tenancy_id = db.Column(db.Integer, db.ForeignKey('tenancy.id'), unique=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'))
    status = db.Column(db.String(50), default='active')
    
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenancy_id': self.tenancy_id,
            'plan_id': self.plan_id,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None
        }


class Invoice(db.Model):
    """Billing invoices"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    tenancy_id = db.Column(db.Integer, db.ForeignKey('tenancy.id'))
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'))
    
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    
    status = db.Column(db.String(50), default='pending')
    
    stripe_invoice_id = db.Column(db.String(255))
    stripe_charge_id = db.Column(db.String(255))
    payment_method = db.Column(db.String(100))
    
    paid_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tenancy_rel = db.relationship('Tenancy', backref='invoices')
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount),
            'tax': float(self.tax),
            'total': float(self.total),
            'status': self.status,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat()
        }


class TenancyInvitation(db.Model):
    """Invitations to join a tenancy"""
    __tablename__ = 'tenancy_invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    tenancy_id = db.Column(db.Integer, db.ForeignKey('tenancy.id'))
    email = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='member')
    token = db.Column(db.String(255), unique=True, nullable=False)
    invited_by = db.Column(db.Integer)
    accepted_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tenancy_rel = db.relationship('Tenancy', backref='invitations')
    
    def is_valid(self):
        """Check if invitation is still valid"""
        if self.accepted_at:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
