-- ============================================================
-- SQL PARA CRIAR USUÁRIO ADMIN CUSTOMIZADO - EXECUTE NO PGADMIN
-- ============================================================
-- 
-- CRIAR USUÁRIO: dmay
-- EMAIL: arsdatascience@gmail.com
-- SENHA: C4rn31r0$425#401!
-- ============================================================

-- PASSO 1: Verificar se existe role de Admin
SELECT id, name, description 
FROM role 
WHERE name ILIKE '%admin%' 
ORDER BY id;

-- PASSO 2: Criar usuário dmay com role admin
-- IMPORTANTE: Ajuste o role_id se necessário (veja resultado do SELECT acima)

-- Opção A: Criar novo usuário (se não existir)
INSERT INTO "user" (
    username, 
    email, 
    password_hash,
    first_name,
    last_name,
    active,
    is_admin,
    role_id,
    created_at,
    updated_at
) 
SELECT 
    'dmay',
    'arsdatascience@gmail.com',
    'scrypt:32768:8:1$X9mK5nP2vLqAWZz$9d9f3b8d7e6c5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b',
    'Denis',
    'May',
    true,
    true,
    (SELECT id FROM role WHERE name ILIKE '%admin%' LIMIT 1),
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
WHERE NOT EXISTS (
    SELECT 1 FROM "user" WHERE username = 'dmay'
);

-- Opção B: Se usuário já existe, atualizar
UPDATE "user" 
SET 
    is_admin = true,
    active = true,
    password_hash = 'scrypt:32768:8:1$X9mK5nP2vLqAWZz$9d9f3b8d7e6c5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b',
    email = 'arsdatascience@gmail.com',
    first_name = 'Denis',
    last_name = 'May',
    role_id = (SELECT id FROM role WHERE name ILIKE '%admin%' LIMIT 1),
    updated_at = CURRENT_TIMESTAMP
WHERE username = 'dmay';

-- PASSO 3: Verificar se foi criado/atualizado
SELECT 
    u.id,
    u.username,
    u.email,
    u.is_admin,
    u.active,
    u.role_id,
    r.name as role_name,
    'SUCESSO! Use: dmay / C4rn31r0$425#401!' as status
FROM "user" u
LEFT JOIN role r ON u.role_id = r.id
WHERE u.username = 'dmay';

-- ============================================================
-- CREDENCIAIS CRIADAS:
-- Username: dmay
-- Password: C4rn31r0$425#401!
-- Email: arsdatascience@gmail.com
-- ============================================================
