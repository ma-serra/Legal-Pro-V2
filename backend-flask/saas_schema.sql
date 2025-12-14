-- =====================================================
-- LEGAL PRO SAAS - DATABASE SCHEMA (SAFE VERSION)
-- Multi-tenant SaaS Architecture
-- Creates tables without user FK dependencies first
-- =====================================================

-- =====================================================
-- 1. SUBSCRIPTION PLANS
-- =====================================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2) NOT NULL DEFAULT 0,
    price_yearly DECIMAL(10,2) NOT NULL DEFAULT 0,
    features JSONB DEFAULT '[]'::jsonb,
    limits JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default plans (only if not already present)
INSERT INTO subscription_plans (name, slug, description, price_monthly, price_yearly, features, limits)
SELECT * FROM (VALUES
    ('Starter', 'starter', 'Perfeito para começar - Trial gratuito de 14 dias', 0.00, 0.00, 
     '["1 usuário", "10 processos", "50 análises/mês", "10 agentes básicos", "Suporte por email"]'::jsonb,
     '{"max_users": 1, "max_processes": 10, "max_analyses_month": 50, "max_agents": 10, "max_storage_gb": 1}'::jsonb),
    ('Professional', 'professional', 'Para escritórios em crescimento', 99.00, 990.00,
     '["10 usuários", "500 processos", "1.000 análises/mês", "100 agentes premium", "Suporte prioritário", "Templates customizados", "Acesso à API"]'::jsonb,
     '{"max_users": 10, "max_processes": 500, "max_analyses_month": 1000, "max_agents": 100, "max_storage_gb": 50}'::jsonb),
    ('Enterprise', 'enterprise', 'Para grandes operações jurídicas', 499.00, 4990.00,
     '["Usuários ilimitados", "Processos ilimitados", "Análises ilimitadas", "Todos os 368 agentes", "Suporte dedicado", "Integrações customizadas", "White-label", "SLA garantido"]'::jsonb,
     '{"max_users": -1, "max_processes": -1, "max_analyses_month": -1, "max_agents": 368, "max_storage_gb": 500}'::jsonb)
) AS v(name, slug, description, price_monthly, price_yearly, features, limits)
WHERE NOT EXISTS (SELECT 1 FROM subscription_plans WHERE slug = v.slug);

-- =====================================================
-- 2. TENANTS (Organizations)
-- =====================================================
CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    plan_id INTEGER REFERENCES subscription_plans(id),
    status VARCHAR(50) DEFAULT 'trial',
    trial_ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Branding
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#2563eb',
    
    -- Current usage
    current_users INTEGER DEFAULT 0,
    current_processes INTEGER DEFAULT 0,
    current_storage_gb DECIMAL(10,2) DEFAULT 0,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- =====================================================
-- 3. SUBSCRIPTIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    plan_id INTEGER REFERENCES subscription_plans(id),
    status VARCHAR(50) DEFAULT 'active',
    
    -- Billing cycle
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    
    -- Payment gateway
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    cancelled_at TIMESTAMP,
    
    UNIQUE(tenant_id)
);

-- =====================================================
-- 4. INVOICES
-- =====================================================
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    subscription_id INTEGER REFERENCES subscriptions(id),
    
    amount DECIMAL(10,2) NOT NULL,
    tax DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    
    status VARCHAR(50) DEFAULT 'pending',
    
    -- Payment details
    stripe_invoice_id VARCHAR(255),
    stripe_charge_id VARCHAR(255),
    payment_method VARCHAR(100),
    
    -- Dates
    paid_at TIMESTAMP,
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 5. MODIFY EXISTING USER TABLE
-- =====================================================
DO $$ 
BEGIN
    -- Add tenant_id column only if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user' AND column_name='tenant_id') THEN
        ALTER TABLE "user" ADD COLUMN tenant_id INTEGER;
        -- Add FK constraint separately
        ALTER TABLE "user" ADD CONSTRAINT fk_user_tenant 
            FOREIGN KEY (tenant_id) REFERENCES tenants(id);
    END IF;
    
    -- Add role_in_tenant column only if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user' AND column_name='role_in_tenant') THEN
        ALTER TABLE "user" ADD COLUMN role_in_tenant VARCHAR(50) DEFAULT 'member';
    END IF;
END $$;

-- =====================================================
-- 6. USAGE TRACKING (without user FK initially)
-- =====================================================
CREATE TABLE IF NOT EXISTS usage_records (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    user_id INTEGER,  -- Will be linked later
    
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    action VARCHAR(50) NOT NULL,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 7. TENANT INVITATIONS (without user FK initially)
-- =====================================================
CREATE TABLE IF NOT EXISTS tenant_invitations (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    token VARCHAR(255) UNIQUE NOT NULL,
    invited_by INTEGER,  -- Will be linked later
    accepted_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 8. ADD TENANT_ID TO EXISTING TABLES
-- =====================================================
DO $$
BEGIN
    -- Add tenant_id to processo_juridico if exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'processo_juridico') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='processo_juridico' AND column_name='tenant_id') THEN
            ALTER TABLE processo_juridico ADD COLUMN tenant_id INTEGER;
            ALTER TABLE processo_juridico ADD CONSTRAINT fk_processo_tenant 
                FOREIGN KEY (tenant_id) REFERENCES tenants(id);
            CREATE INDEX idx_processo_tenant ON processo_juridico(tenant_id);
        END IF;
    END IF;
END $$;

-- =====================================================
-- 9. INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant ON subscriptions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_tenant ON invoices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_usage_tenant_date ON usage_records(tenant_id, created_at);

-- Try to create user tenant index (may fail if user table doesn't exist yet)
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_user_tenant ON "user"(tenant_id);
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

-- =====================================================
-- COMPLETE! Ready for SaaS multi-tenancy
-- =====================================================
