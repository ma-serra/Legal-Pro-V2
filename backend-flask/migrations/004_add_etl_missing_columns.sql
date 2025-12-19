-- Migration: Add missing fields from ETL to processos table
-- Date: 2025-12-19
-- Description: Adds 4 missing columns identified in audit

-- 1. cliente_principal_nome - Nome do cliente principal
ALTER TABLE processos ADD COLUMN IF NOT EXISTS cliente_principal_nome VARCHAR(255);

-- 2. uf - Estado/UF do processo
ALTER TABLE processos ADD COLUMN IF NOT EXISTS uf VARCHAR(2);

-- 3. cidade - Cidade do processo
ALTER TABLE processos ADD COLUMN IF NOT EXISTS cidade VARCHAR(100);

-- 4. uf_vara - UF da vara
ALTER TABLE processos ADD COLUMN IF NOT EXISTS uf_vara VARCHAR(2);

-- Comentários para documentação
COMMENT ON COLUMN processos.cliente_principal_nome IS 'Nome do cliente principal do processo';
COMMENT ON COLUMN processos.uf IS 'Estado/UF do processo';
COMMENT ON COLUMN processos.cidade IS 'Cidade do processo';
COMMENT ON COLUMN processos.uf_vara IS 'UF da vara/tribunal';
