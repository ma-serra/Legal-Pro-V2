-- =============================================
-- LEGAL PRO HUB - SCHEMA PROCESSOS DINÂMICOS
-- Versão: 2.0
-- Data: 15 Dezembro 2025
-- =============================================

-- =============================================
-- 1. TABELA PRINCIPAL: processos (MODIFICADA)
-- =============================================

-- Adicionar novas colunas à tabela existente
ALTER TABLE processos ADD COLUMN IF NOT EXISTS uuid UUID DEFAULT gen_random_uuid() UNIQUE;
ALTER TABLE processos ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id_tenant) ON DELETE CASCADE;
ALTER TABLE processos ADD COLUMN IF NOT EXISTS titulo TEXT;
ALTER TABLE processos ADD COLUMN IF NOT EXISTS observacao_pasta TEXT;
ALTER TABLE processos ADD COLUMN IF NOT EXISTS natureza_id INTEGER REFERENCES natureza_processo(id_natureza);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS posicao_cliente_id INTEGER REFERENCES posicao_cliente(id_posicao);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS acao_id INTEGER REFERENCES acao(id_acao);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS procedimento_id INTEGER REFERENCES procedimento(id_procedimento);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS fase_id INTEGER REFERENCES fase_processual(id_fase);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS orgao_id INTEGER REFERENCES orgao(id_orgao);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS comarca_id INTEGER REFERENCES comarca(id_comarca);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS vara_turma_id INTEGER REFERENCES vara_turma(id_vara_turma);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS justica_cnj_id INTEGER REFERENCES justica_cnj(id_justica);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS instancia_cnj_id INTEGER REFERENCES instancia_cnj(id_instancia);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS classe_cnj_id INTEGER REFERENCES classe_cnj(id_classe);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS valor_causa_atualizado NUMERIC(18,2);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS valor_envolvido_atualizado NUMERIC(18,2);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS tipo_probabilidade_id INTEGER REFERENCES tipo_probabilidade(id_tipo_probabilidade);
ALTER TABLE processos ADD COLUMN IF NOT EXISTS risco_id INTEGER REFERENCES nivel_risco(id_risco);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_processos_tenant ON processos(tenant_id);
CREATE INDEX IF NOT EXISTS idx_processos_natureza ON processos(natureza_id);
CREATE INDEX IF NOT EXISTS idx_processos_ativo ON processos(ativo) WHERE ativo = TRUE;

-- =============================================
-- 2. CAMPOS ESPECÍFICOS POR NATUREZA
-- =============================================

CREATE TABLE IF NOT EXISTS processo_campos_especificos (
    id_campo_especifico BIGSERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    natureza_id INTEGER NOT NULL REFERENCES natureza_processo(id_natureza),
    
    -- Campos específicos armazenados como JSONB para flexibilidade
    campos_tributario JSONB,
    campos_trabalhista JSONB,
    campos_civel JSONB,
    
    -- Auditoria
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT uk_processo_natureza UNIQUE(processo_id, natureza_id)
);

CREATE INDEX idx_campos_processo ON processo_campos_especificos(processo_id);
CREATE INDEX idx_campos_natureza ON processo_campos_especificos(natureza_id);
CREATE INDEX idx_campos_tributario ON processo_campos_especificos USING GIN(campos_tributario);
CREATE INDEX idx_campos_trabalhista ON processo_campos_especificos USING GIN(campos_trabalhista);
CREATE INDEX idx_campos_civel ON processo_campos_especificos USING GIN(campos_civel);

-- =============================================
-- 3. MÓDULO TRIBUTÁRIO
-- =============================================

-- 3.1 Tributos
CREATE TABLE IF NOT EXISTS tributos (
    id_tributo SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    esfera VARCHAR(20) CHECK (esfera IN ('Federal', 'Estadual', 'Municipal')),
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir tributos principais
INSERT INTO tributos (codigo, nome, esfera) VALUES
('ICMS', 'Imposto sobre Circulação de Mercadorias e Serviços', 'Estadual'),
('ISS', 'Imposto sobre Serviços', 'Municipal'),
('IRPJ', 'Imposto de Renda Pessoa Jurídica', 'Federal'),
('CSLL', 'Contribuição Social sobre Lucro Líquido', 'Federal'),
('PIS', 'Programa de Integração Social', 'Federal'),
('COFINS', 'Contribuição para Financiamento da Seguridade Social', 'Federal'),
('IPI', 'Imposto sobre Produtos Industrializados', 'Federal'),
('IPTU', 'Imposto Predial e Territorial Urbano', 'Municipal'),
('IPVA', 'Imposto sobre Propriedade de Veículos Automotores', 'Estadual')
ON CONFLICT (codigo) DO NOTHING;

-- 3.2 Teses Tributárias
CREATE TABLE IF NOT EXISTS teses_tributarias (
    id_tese SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id_tenant) ON DELETE CASCADE,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    titulo VARCHAR(500) NOT NULL,
    descricao TEXT,
    tributo_id INTEGER REFERENCES tributos(id_tributo),
    
    -- Jurisprudência
    tema_repercussao_geral VARCHAR(50),
    tema_repetitivo VARCHAR(50),
    tribunal_origem VARCHAR(100),
    
    -- Prognóstico padrão
    probabilidade_sucesso NUMERIC(5,2) CHECK (probabilidade_sucesso BETWEEN 0 AND 100),
    fundamentacao TEXT,
    
    -- Status
    situacao VARCHAR(50) CHECK (situacao IN ('Favorável', 'Desfavorável', 'Pendente', 'Superada')),
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- Auditoria
    criado_por INTEGER REFERENCES "user"(id),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_teses_tenant ON teses_tributarias(tenant_id);
CREATE INDEX idx_teses_tributo ON teses_tributarias(tributo_id);
CREATE INDEX idx_teses_ativo ON teses_tributarias(ativo) WHERE ativo = TRUE;

-- 3.3 Processo Tributário
CREATE TABLE IF NOT EXISTS processo_tributario (
    id_processo_tributario BIGSERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    
    -- Tributo
    tributo_id INTEGER REFERENCES tributos(id_tributo),
    
    -- Documentos Fiscais
    numero_aiim VARCHAR(100),
    numero_cda VARCHAR(100),
    data_lancamento DATE,
    
    -- Valores Específicos
    valor_inscrito_cda NUMERIC(18,2),
    valor_principal NUMERIC(18,2),
    valor_multa NUMERIC(18,2),
    percentual_multa NUMERIC(5,2),
    base_calculo_multa VARCHAR(100),
    
    -- Juros
    valor_juros NUMERIC(18,2),
    indice_juros VARCHAR(50) CHECK (indice_juros IN ('SELIC', 'Lei 13918', 'IPCA', 'CDI', 'Outro')),
    descricao_indice_juros TEXT,
    
    -- Vara/Turma Específicas
    vara_primeira_instancia_id INTEGER REFERENCES vara_turma(id_vara_turma),
    turma_segunda_instancia_id INTEGER REFERENCES vara_turma(id_vara_turma),
    
    -- Auditoria
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_processo_tributario UNIQUE(processo_id),
    CONSTRAINT chk_valores_tributario CHECK (
        valor_inscrito_cda >= 0 AND
        valor_principal >= 0 AND
        valor_multa >= 0 AND
        valor_juros >= 0 AND
        (percentual_multa IS NULL OR percentual_multa >= 0)
    )
);

CREATE INDEX idx_proc_trib_processo ON processo_tributario(processo_id);
CREATE INDEX idx_proc_trib_tributo ON processo_tributario(tributo_id);

-- 3.4 Processo-Tese (N:N)
CREATE TABLE IF NOT EXISTS processo_tese (
    id_processo_tese BIGSERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    tese_id INTEGER NOT NULL REFERENCES teses_tributarias(id_tese) ON DELETE CASCADE,
    
    -- Ordem de importância
    ordem INTEGER DEFAULT 1,
    
    -- Status específico desta tese no processo
    status VARCHAR(50) CHECK (status IN ('Aguardando', 'Em análise', 'Aceita', 'Rejeitada')),
    
    -- Auditoria
    data_vinculacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_processo_tese UNIQUE(processo_id, tese_id)
);

CREATE INDEX idx_proc_tese_processo ON processo_tese(processo_id);
CREATE INDEX idx_proc_tese_tese ON processo_tese(tese_id);

-- 3.5 Prognóstico Tributário Detalhado
CREATE TABLE IF NOT EXISTS processo_prognostico_tributario (
    id_prognostico BIGSERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    
    -- Êxito Provável
    tese_provavel_id INTEGER REFERENCES teses_tributarias(id_tese),
    valor_provavel NUMERIC(18,2),
    percentual_provavel NUMERIC(5,2) DEFAULT 70.00,
    
    -- Êxito Possível
    tese_possivel_id INTEGER REFERENCES teses_tributarias(id_tese),
    valor_possivel NUMERIC(18,2),
    percentual_possivel NUMERIC(5,2) DEFAULT 50.00,
    
    -- Êxito Remoto
    tese_remota_id INTEGER REFERENCES teses_tributarias(id_tese),
    valor_remoto NUMERIC(18,2),
    percentual_remoto NUMERIC(5,2) DEFAULT 25.00,
    
    -- Metadados
    observacoes TEXT,
    data_avaliacao DATE DEFAULT CURRENT_DATE,
    avaliado_por INTEGER REFERENCES "user"(id),
    
    -- Auditoria
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_prognostico_processo UNIQUE(processo_id)
);

CREATE INDEX idx_prognostico_processo ON processo_prognostico_tributario(processo_id);

-- =============================================
-- 4. MÓDULO TRABALHISTA
-- =============================================

CREATE TABLE IF NOT EXISTS processo_trabalhista (
    id_processo_trabalhista BIGSERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    
    -- Acordo
    tolerancia_acordo NUMERIC(18,2),
    acordo_realizado NUMERIC(18,2),
    data_acordo DATE,
    observacoes_acordo TEXT,
    
    -- Auditoria
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_processo_trabalhista UNIQUE(processo_id)
);

CREATE INDEX idx_proc_trab_processo ON processo_trabalhista(processo_id);

CREATE TABLE IF NOT EXISTS processo_prognostico_trabalhista (
    id_prognostico BIGSERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    
    -- Êxito Provável
    tese_provavel TEXT,
    valor_provavel NUMERIC(18,2),
    percentual_provavel NUMERIC(5,2) DEFAULT 70.00,
    
    -- Êxito Possível
    tese_possivel TEXT,
    valor_possivel NUMERIC(18,2),
    percentual_possivel NUMERIC(5,2) DEFAULT 50.00,
    
    -- Êxito Remoto
    tese_remota TEXT,
    valor_remoto NUMERIC(18,2),
    percentual_remoto NUMERIC(5,2) DEFAULT 25.00,
    
    -- Metadados
    observacoes TEXT,
    data_avaliacao DATE DEFAULT CURRENT_DATE,
    avaliado_por INTEGER REFERENCES "user"(id),
    
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_prognostico_trab_processo UNIQUE(processo_id)
);

CREATE INDEX idx_prognostico_trab_processo ON processo_prognostico_trabalhista(processo_id);

-- =============================================
-- 5. MÓDULO CÍVEL
-- =============================================

CREATE TABLE IF NOT EXISTS processo_civel (
    id_processo_civel BIGSERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    
    -- Acordo
    tolerancia_acordo NUMERIC(18,2),
    acordo_realizado NUMERIC(18,2),
    data_acordo DATE,
    observacoes_acordo TEXT,
    
    -- Auditoria
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_processo_civel UNIQUE(processo_id)
);

CREATE INDEX idx_proc_civel_processo ON processo_civel(processo_id);

CREATE TABLE IF NOT EXISTS processo_prognostico_civel (
    id_prognostico BIGSERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    
    -- Êxito Provável
    tese_provavel TEXT,
    valor_provavel NUMERIC(18,2),
    percentual_provavel NUMERIC(5,2) DEFAULT 70.00,
    
    -- Êxito Possível
    tese_possivel TEXT,
    valor_possivel NUMERIC(18,2),
    percentual_possivel NUMERIC(5,2) DEFAULT 50.00,
    
    -- Êxito Remoto
    tese_remota TEXT,
    valor_remoto NUMERIC(18,2),
    percentual_remoto NUMERIC(5,2) DEFAULT 25.00,
    
    -- Metadados
    observacoes TEXT,
    data_avaliacao DATE DEFAULT CURRENT_DATE,
    avaliado_por INTEGER REFERENCES "user"(id),
    
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_prognostico_civ_processo UNIQUE(processo_id)
);

CREATE INDEX idx_prognostico_civ_processo ON processo_prognostico_civel(processo_id);

-- =============================================
-- 6. ATUALIZAÇÃO MONETÁRIA
-- =============================================

CREATE TABLE IF NOT EXISTS indices_monetarios (
    id_indice SERIAL PRIMARY KEY,
    nome VARCHAR(50) UNIQUE NOT NULL,
    descricao TEXT,
    fonte_oficial VARCHAR(200),
    ativo BOOLEAN DEFAULT TRUE NOT NULL
);

INSERT INTO indices_monetarios (nome, descricao, fonte_oficial) VALUES
('SELIC', 'Sistema Especial de Liquidação e Custódia', 'Banco Central do Brasil'),
('IPCA', 'Índice de Preços ao Consumidor Amplo', 'IBGE'),
('INPC', 'Índice Nacional de Preços ao Consumidor', 'IBGE'),
('IGP-M', 'Índice Geral de Preços do Mercado', 'FGV'),
('CDI', 'Certificado de Depósito Interbancário', 'CETIP'),
('TR', 'Taxa Referencial', 'Banco Central do Brasil')
ON CONFLICT (nome) DO NOTHING;

CREATE TABLE IF NOT EXISTS historico_indices (
    id_historico BIGSERIAL PRIMARY KEY,
    indice_id INTEGER NOT NULL REFERENCES indices_monetarios(id_indice),
    data_referencia DATE NOT NULL,
    valor NUMERIC(10,6) NOT NULL,
    
    -- Auditoria
    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_indice_data UNIQUE(indice_id, data_referencia)
);

CREATE INDEX idx_hist_indice ON historico_indices(indice_id);
CREATE INDEX idx_hist_data ON historico_indices(data_referencia);

CREATE TABLE IF NOT EXISTS processo_atualizacao_monetaria (
    id_atualizacao BIGSERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
    
    -- Configuração
    indice_id INTEGER NOT NULL REFERENCES indices_monetarios(id_indice),
    data_base DATE NOT NULL,
    valor_base NUMERIC(18,2) NOT NULL,
    
    -- Resultado
    data_atualizacao DATE NOT NULL DEFAULT CURRENT_DATE,
    valor_atualizado NUMERIC(18,2),
    percentual_correcao NUMERIC(10,6),
    
    -- Auditoria
    calculado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_datas_atualizacao CHECK (data_atualizacao >= data_base)
);

CREATE INDEX idx_atualizacao_processo ON processo_atualizacao_monetaria(processo_id);

-- =============================================
-- 7. CONFIGURAÇÃO DINÂMICA
-- =============================================

CREATE TABLE IF NOT EXISTS configuracao_formulario (
    id_configuracao SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id_tenant) ON DELETE CASCADE,
    natureza_id INTEGER NOT NULL REFERENCES natureza_processo(id_natureza),
    
    -- Estrutura do formulário em JSON
    campos_obrigatorios JSONB NOT NULL DEFAULT '[]',
    campos_opcionais JSONB NOT NULL DEFAULT '[]',
    validacoes JSONB NOT NULL DEFAULT '{}',
    layout JSONB NOT NULL DEFAULT '{}',
    
    -- Versão
    versao INTEGER DEFAULT 1,
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- Auditoria
    criado_por INTEGER REFERENCES "user"(id),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_tenant_natureza_versao UNIQUE(tenant_id, natureza_id, versao)
);

CREATE INDEX idx_config_tenant_natureza ON configuracao_formulario(tenant_id, natureza_id);

-- =============================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- =============================================

COMMENT ON TABLE processos IS 'Tabela principal de processos jurídicos com campos dinâmicos por natureza';
COMMENT ON TABLE processo_campos_especificos IS 'Armazena campos específicos em JSONB para cada natureza de processo';
COMMENT ON TABLE tributos IS 'Cadastro de tributos (ICMS, ISS, IRPJ, etc)';
COMMENT ON TABLE teses_tributarias IS 'Teses jurídicas tributárias com jurisprudência e probabilidade de sucesso';
COMMENT ON TABLE processo_tributario IS 'Campos específicos de processos tributários (AIIM, CDA, valores)';
COMMENT ON TABLE processo_tese IS 'Relacionamento N:N entre processos e teses tributárias';
COMMENT ON TABLE processo_prognostico_tributario IS 'Prognóstico detalhado (provável, possível, remoto) para processos tributários';
COMMENT ON TABLE indices_monetarios IS 'Cadastro de índices de correção monetária (SELIC, IPCA, etc)';
COMMENT ON TABLE historico_indices IS 'Histórico de valores dos índices monetários por data';
COMMENT ON TABLE processo_atualizacao_monetaria IS 'Registro de atualizações monetárias realizadas em processos';
COMMENT ON TABLE configuracao_formulario IS 'Configuração dinâmica de formulários por natureza de processo';

-- =============================================
-- FIM DO SCRIPT
-- =============================================
