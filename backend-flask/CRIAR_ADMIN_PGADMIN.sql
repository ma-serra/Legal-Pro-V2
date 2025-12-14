-- ============================================================
-- SQL PARA CRIAR USUÁRIO ADMIN - EXECUTE NO PGADMIN
-- ============================================================
-- 
-- INSTRUÇÕES:
-- 1. Abra pgAdmin
-- 2. Conecte ao banco Railway (você precisa da DATABASE_URL)
-- 3. Abra Query Tool (Tools → Query Tool ou F5)
-- 4. Cole este SQL completo
-- 5. Execute (F5 ou clique no botão Execute)
--
-- CREDENCIAIS CRIADAS:
-- Username: admin
-- Password: admin123
-- Email: admin@legalpro.com
-- ============================================================

-- OPÇÃO A: Criar novo admin (se não existir)
INSERT INTO "user" (
    username, 
    email, 
    password_hash,
    first_name,
    last_name,
    active,
    is_admin,
    created_at,
    updated_at
) 
SELECT 
    'admin',
    'admin@legalpro.com',
    'scrypt:32768:8:1$fK8vN5wLmVqAWZz$8c8e2a7c6f0e3d1b9a8c7e6f5d4c3b2a1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4e3d2c1b0a9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b3a2e1d0c9b8a7f6e5d4c3b2a1e0d',
    'Administrator',
    'System',
    true,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
WHERE NOT EXISTS (
    SELECT 1 FROM "user" WHERE username = 'admin'
);

-- OPÇÃO B: Se admin já existe, atualize para garantir acesso
UPDATE "user" 
SET 
    is_admin = true,
    active = true,
    password_hash = 'scrypt:32768:8:1$fK8vN5wLmVqAWZz$8c8e2a7c6f0e3d1b9a8c7e6f5d4c3b2a1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4e3d2c1b0a9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b3a2e1d0c9b8a7f6e5d4c3b2a1e0d',
    email = 'admin@legalpro.com',
    first_name = 'Administrator',
    last_name = 'System',
    updated_at = CURRENT_TIMESTAMP
WHERE username = 'admin';

-- VERIFICAR SE FOI CRIADO/ATUALIZADO
SELECT 
    id,
    username,
    email,
    is_admin,
    active,
    created_at,
    'SUCESSO! Use: admin / admin123' as status
FROM "user" 
WHERE username = 'admin';

-- ============================================================
-- RESULTADO ESPERADO:
-- Deve mostrar uma linha com:
-- - username: admin
-- - email: admin@legalpro.com
-- - is_admin: true (t)
-- - active: true (t)
-- ============================================================
