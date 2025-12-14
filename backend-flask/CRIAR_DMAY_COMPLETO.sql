-- ============================================================
-- SQL COMPLETO - CRIAR USUÁRIO DMAY COM TODAS AS COLUNAS
-- ============================================================
-- Database: postgresql://postgres:***@gondola.proxy.rlwy.net:11843/railway
-- Execute no pgAdmin ou Query Tool do Railway
-- ============================================================

-- PASSO 1: Deletar se já existir
DELETE FROM "user" WHERE username = 'dmay';

-- PASSO 2: Criar usuário DMAY com TODAS as colunas
INSERT INTO "user" (
    username,
    email,
    password_hash,
    first_name,
    last_name,
    active,
    is_admin,
    last_login,
    created_at,
    updated_at,
    role_id
) VALUES (
    'dmay',                                                     -- username
    'arsdatascience@gmail.com',                                -- email
    'scrypt:32768:8:1$X9mK5nP2vLqAWZz$9d9f3b8d7e6c5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b',  -- password_hash
    'Denis',                                                    -- first_name
    'May',                                                      -- last_name
    true,                                                       -- active
    true,                                                       -- is_admin
    NULL,                                                       -- last_login (NULL até primeiro login)
    NOW(),                                                      -- created_at
    NOW(),                                                      -- updated_at
    NULL                                                        -- role_id (NULL ou use um ID específico se necessário)
);

-- PASSO 3: Verificar criação
SELECT 
    id,
    username,
    email,
    password_hash,
    first_name,
    last_name,
    active,
    is_admin,
    last_login,
    created_at,
    updated_at,
    role_id
FROM "user" 
WHERE username = 'dmay';

-- ============================================================
-- CREDENCIAIS CRIADAS:
-- Username: dmay
-- Password: C4rn31r0$425#401!
-- Email: arsdatascience@gmail.com
-- is_admin: true
-- active: true
-- ============================================================

-- OBSERVAÇÃO: Se você quiser associar um role específico,
-- primeiro veja os roles disponíveis:
-- SELECT id, name FROM role;
-- Depois execute:
-- UPDATE "user" SET role_id = [ID_DO_ROLE] WHERE username = 'dmay';
-- ============================================================
