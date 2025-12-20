-- Migration: Create Simulacoes Tributarias Table
-- Description: Stores history of tax simulations (Simples, Presumido, Recovery Thesis)
-- Date: 2025-12-19

CREATE TABLE IF NOT EXISTS simulacoes_tributarias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_nome VARCHAR(255),
    tipo_simulacao VARCHAR(50) NOT NULL, -- 'COMPARATIVO_REGIME', 'RECUPERACAO_ICMS'
    parametros_input JSONB NOT NULL,
    resultado_output JSONB NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER, -- Optional link to User table
    status VARCHAR(20) DEFAULT 'SALVO'
);

CREATE INDEX idx_simulacoes_cliente ON simulacoes_tributarias(cliente_nome);
CREATE INDEX idx_simulacoes_tipo ON simulacoes_tributarias(tipo_simulacao);
CREATE INDEX idx_simulacoes_data ON simulacoes_tributarias(data_criacao DESC);
