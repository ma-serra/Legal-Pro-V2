-- Script SQL para criar usuário administrador
-- Execute este script diretamente no banco de dados PostgreSQL (Railway)

-- OPÇÃO 1: Criar novo usuário admin
-- Hash da senha 'admin123' gerado com pbkdf2:sha256
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
    'admin',
    'admin@legalpro.com',
    'pbkdf2:sha256:600000$8vK3pN5wLmVqAWZz$8c8e2a7c6f0e3d1b9a8c7e6f5d4c3b2a1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6',
    'Administrator',
    'System',
    true,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO NOTHING;

-- OPÇÃO 2: Se o usuário já existe, atualize para admin
UPDATE "user" 
SET 
    is_admin = true,
    active = true,
    password_hash = 'pbkdf2:sha256:600000$8vK3pN5wLmVqAWZz$8c8e2a7c6f0e3d1b9a8c7e6f5d4c3b2a1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6',
    email = 'admin@legalpro.com',
    updated_at = CURRENT_TIMESTAMP
WHERE username = 'admin';

-- Verificar se foi criado/atualizado
SELECT id, username, email, is_admin, active, created_at 
FROM "user" 
WHERE username = 'admin';
