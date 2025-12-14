-- =====================================================
-- LEGAL PRO SAAS - DATABASE SCHEMA V2
-- Arquitetura: USER → TENANCY → CLIENT
-- Multi-tenant SaaS Architecture (REFATORADO)
-- =====================================================

-- =====================================================
-- 1. SUBSCRIPTION PLANS (mantém igual)
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

-- Insert default plans
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
-- 2. TENANCY (Instância multi-tenant)
-- =====================================================
CREATE TABLE IF NOT EXISTS tenancy (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    plan_id INTEGER REFERENCES subscription_plans(id),
    status VARCHAR(50) DEFAULT 'trial',
    trial_ends_at TIMESTAMP,
    
    -- Branding
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#2563eb',
    
    -- Settings
    settings JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 3. CLIENT (Clientes/Empresas atendidas pela Tenancy)
-- =====================================================
CREATE TABLE IF NOT EXISTS client (
    id SERIAL PRIMARY KEY,
    tenancy_id INTEGER REFERENCES tenancy(id) ON DELETE CASCADE,
    
    -- Informações do Cliente
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    document_number VARCHAR(50),  -- CNPJ/CPF
    document_type VARCHAR(20),    -- cnpj, cpf
    
    -- Contato
    email VARCHAR(255),
    phone VARCHAR(50),
    
    -- Endereço
    address_street VARCHAR(255),
    address_number VARCHAR(50),
    address_complement VARCHAR(100),
    address_neighborhood VARCHAR(100),
    address_city VARCHAR(100),
    address_state VARCHAR(2),
    address_zip VARCHAR(20),
    address_country VARCHAR(50) DEFAULT 'Brasil',
    
    -- Informações comerciais
    industry VARCHAR(100),
    size VARCHAR(50),  -- startup, small, medium, large, enterprise
    
    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, inactive, suspended
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 4. SUBSCRIPTIONS (vinculada à Tenancy)
-- =====================================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    tenancy_id INTEGER REFERENCES tenancy(id) ON DELETE CASCADE,
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
    
    UNIQUE(tenancy_id)
);

-- =====================================================
-- 5. INVOICES
-- =====================================================
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    tenancy_id INTEGER REFERENCES tenancy(id) ON DELETE CASCADE,
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
-- 6. MODIFY EXISTING USER TABLE
-- USER está ligado a TENANCY (não a CLIENT)
-- =====================================================
DO $$ 
BEGIN
    -- Rename role_in_tenant to role_in_tenancy if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='user' AND column_name='role_in_tenant') THEN
        ALTER TABLE "user" RENAME COLUMN role_in_tenant TO role_in_tenancy;
    END IF;
    
    -- Add role_in_tenancy if it doesn't exist yet
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user' AND column_name='role_in_tenancy') THEN
        ALTER TABLE "user" ADD COLUMN role_in_tenancy VARCHAR(50) DEFAULT 'member';
    END IF;
    
    -- Remove old tenant_id constraint if exists
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints 
               WHERE table_name='user' AND constraint_name='fk_user_tenant') THEN
        ALTER TABLE "user" DROP CONSTRAINT fk_user_tenant;
    END IF;
    
    -- Rename tenant_id to tenancy_id if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='user' AND column_name='tenant_id') THEN
        ALTER TABLE "user" RENAME COLUMN tenant_id TO tenancy_id;
    END IF;
    
    -- Add tenancy_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user' AND column_name='tenancy_id') THEN
        ALTER TABLE "user" ADD COLUMN tenancy_id INTEGER;
    END IF;
    
    -- Add FK constraint to tenancy if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE table_name='user' AND constraint_name='fk_user_tenancy') THEN
        ALTER TABLE "user" ADD CONSTRAINT fk_user_tenancy 
            FOREIGN KEY (tenancy_id) REFERENCES tenancy(id);
    END IF;
END $$;
-- Roles: 'owner', 'admin', 'member', 'viewer'


-- =====================================================
-- 7. USER_CLIENT_ACCESS
-- Tabela de relacionamento: quais USERs acessam quais CLIENTs
-- (FK para user será adicionada depois)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_client_access (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    client_id INTEGER REFERENCES client(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'viewer',  -- owner, editor, viewer
    granted_at TIMESTAMP DEFAULT NOW(),
    granted_by INTEGER,
    
    UNIQUE(user_id, client_id)
);

-- =====================================================
-- 8. USAGE TRACKING
-- =====================================================
CREATE TABLE IF NOT EXISTS usage_records (
    id SERIAL PRIMARY KEY,
    tenancy_id INTEGER REFERENCES tenancy(id) ON DELETE CASCADE,
    user_id INTEGER,
    client_id INTEGER REFERENCES client(id),
    
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    action VARCHAR(50) NOT NULL,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 9. TENANT INVITATIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS tenancy_invitations (
    id SERIAL PRIMARY KEY,
    tenancy_id INTEGER REFERENCES tenancy(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    token VARCHAR(255) UNIQUE NOT NULL,
    invited_by INTEGER,
    accepted_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 10. ADD TENANCY_ID & CLIENT_ID TO EXISTING TABLES
-- =====================================================
DO $$
BEGIN
    -- Add tenancy_id and client_id to processo_juridico
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'processo_juridico') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='processo_juridico' AND column_name='tenancy_id') THEN
            ALTER TABLE processo_juridico ADD COLUMN tenancy_id INTEGER;
            ALTER TABLE processo_juridico ADD CONSTRAINT fk_processo_tenancy 
                FOREIGN KEY (tenancy_id) REFERENCES tenancy(id);
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='processo_juridico' AND column_name='client_id') THEN
            ALTER TABLE processo_juridico ADD COLUMN client_id INTEGER;
            ALTER TABLE processo_juridico ADD CONSTRAINT fk_processo_client 
                FOREIGN KEY (client_id) REFERENCES client(id);
        END IF;
        
        -- Remove old tenant_id if exists
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='processo_juridico' AND column_name='tenant_id') THEN
            ALTER TABLE processo_juridico DROP COLUMN IF EXISTS tenant_id CASCADE;
        END IF;
    END IF;
END $$;

-- =====================================================
-- 11. INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_tenancy_slug ON tenancy(slug);
CREATE INDEX IF NOT EXISTS idx_tenancy_status ON tenancy(status);
CREATE INDEX IF NOT EXISTS idx_client_tenancy ON client(tenancy_id);
CREATE INDEX IF NOT EXISTS idx_client_document ON client(document_number);
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenancy ON subscriptions(tenancy_id);
CREATE INDEX IF NOT EXISTS idx_invoices_tenancy ON invoices(tenancy_id);
CREATE INDEX IF NOT EXISTS idx_usage_tenancy_date ON usage_records(tenancy_id, created_at);
CREATE INDEX IF NOT EXISTS idx_user_client_access_user ON user_client_access(user_id);
CREATE INDEX IF NOT EXISTS idx_user_client_access_client ON user_client_access(client_id);

-- Try to create user tenancy index
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_user_tenancy ON "user"(tenancy_id);
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

-- Index for processo_juridico if exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'processo_juridico') THEN
        CREATE INDEX IF NOT EXISTS idx_processo_tenancy ON processo_juridico(tenancy_id);
        CREATE INDEX IF NOT EXISTS idx_processo_client ON processo_juridico(client_id);
    END IF;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

-- =====================================================
-- COMPLETE! Arquitetura: USER → TENANCY → CLIENT
-- =====================================================
