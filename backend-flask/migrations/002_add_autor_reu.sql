-- ============================================================================
-- CORREÇÃO: Adicionar colunas autor e réu na tabela processos
-- Data: 15 Dezembro 2025
-- ============================================================================

ALTER TABLE processos ADD COLUMN IF NOT EXISTS autor VARCHAR(255);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS reu VARCHAR(255);

-- Índices opcionais para busca
CREATE INDEX IF NOT EXISTS idx_processos_autor ON processos(autor);
CREATE INDEX IF NOT EXISTS idx_processos_reu ON processos(reu);
