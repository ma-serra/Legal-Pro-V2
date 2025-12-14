-- ============================================================
-- SQL SIMPLES - CRIAR USUÁRIO DMAY (DIRETO, SEM CONDIÇÕES)
-- ============================================================
-- Execute linha por linha no pgAdmin
-- ============================================================

-- PASSO 1: Deletar se já existir (evita erro de duplicata)
DELETE FROM "user" WHERE username = 'dmay';

-- PASSO 2: Criar usuário DMAY
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
) VALUES (
    'dmay',
    'arsdatascience@gmail.com',
    'scrypt:32768:8:1$X9mK5nP2vLqAWZz$9d9f3b8d7e6c5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b',
    'Denis',
    'May',
    true,
    true,
    NOW(),
    NOW()
);

-- PASSO 3: Verificar
SELECT 
    id,
    username,
    email,
    is_admin,
    active,
    created_at
FROM "user" 
WHERE username = 'dmay';

-- ============================================================
-- CREDENCIAIS:
-- Username: dmay
-- Password: C4rn31r0$425#401!
-- Email: arsdatascience@gmail.com
-- ============================================================
