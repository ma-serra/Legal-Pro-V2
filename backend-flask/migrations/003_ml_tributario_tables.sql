-- Migration: ML Tributário Tables
-- Cria tabelas para armazenar modelos ML e predições

-- Tabela de modelos treinados
CREATE TABLE IF NOT EXISTS ml_modelo_tributario (
    id_modelo SERIAL PRIMARY KEY,
    versao VARCHAR(50) UNIQUE NOT NULL,
    algoritmo VARCHAR(100) NOT NULL, -- 'ridge', 'xgboost_regressor', 'xgboost_classifier'
    tipo VARCHAR(50) NOT NULL, -- 'regressao' ou 'classificacao'
    data_treinamento TIMESTAMP NOT NULL DEFAULT NOW(),
    total_amostras_treino INTEGER,
    total_amostras_teste INTEGER,
    
    -- Métricas Regressão
    r2_score DECIMAL(5,4),
    mae DECIMAL(15,2),
    rmse DECIMAL(15,2),
    
    -- Métricas Classificação
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc_roc DECIMAL(5,4),
    
    -- Hiperparâmetros e metadados
    hiperparametros JSONB,
    features_utilizadas JSONB,
    path_arquivo VARCHAR(500),
    
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT check_versao_format CHECK (versao ~ '^v[0-9]+\.[0-9]+\.[0-9]+$')
);

-- Índices
CREATE INDEX idx_ml_modelo_trib_ativo ON ml_modelo_tributario(ativo);
CREATE INDEX idx_ml_modelo_trib_versao ON ml_modelo_tributario(versao);

-- Tabela de predições
CREATE TABLE IF NOT EXISTS ml_predicao_tributario (
    id_predicao SERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    modelo_id INTEGER NOT NULL REFERENCES ml_modelo_tributario(id_modelo),
    
    -- Predições de Valor (Regressão)
    valor_contingencia_predito DECIMAL(15,2),
    valor_confianca DECIMAL(5,4), -- 0.0 a 1.0
    
    -- Predições de Risco (Classificação)
    risco_predito VARCHAR(50), -- 'Baixo', 'Médio', 'Alto'
    risco_probabilidade_baixo DECIMAL(5,4),
    risco_probabilidade_medio DECIMAL(5,4),
    risco_probabilidade_alto DECIMAL(5,4),
    
    -- Prognóstico Êxito
    probabilidade_exito DECIMAL(5,4), -- 0.0 a 1.0 (% vitória)
    
    -- Features utilizadas (snapshot)
    features_snapshot JSONB,
    
    -- Metadados
    data_predicao TIMESTAMP DEFAULT NOW(),
    usuario_id INTEGER,
    
    CONSTRAINT check_confianca_range CHECK (valor_confianca >= 0 AND valor_confianca <= 1),
    CONSTRAINT check_prob_exito_range CHECK (probabilidade_exito >= 0 AND probabilidade_exito <= 1)
);

-- Índices
CREATE INDEX idx_ml_pred_trib_processo ON ml_predicao_tributario(processo_id);
CREATE INDEX idx_ml_pred_trib_modelo ON ml_predicao_tributario(modelo_id);
CREATE INDEX idx_ml_pred_trib_data ON ml_predicao_tributario(data_predicao);

-- Comentários
COMMENT ON TABLE ml_modelo_tributario IS 'Armazena modelos ML treinados para processos tributários';
COMMENT ON TABLE ml_predicao_tributario IS 'Histórico de predições ML para processos tributários';

COMMENT ON COLUMN ml_modelo_tributario.versao IS 'Versão semântica: v1.0.0, v1.1.0, etc';
COMMENT ON COLUMN ml_modelo_tributario.algoritmo IS 'Algoritmo ML: ridge, xgboost_regressor, xgboost_classifier';
COMMENT ON COLUMN ml_predicao_tributario.features_snapshot IS 'Snapshot das features utilizadas na predição';
