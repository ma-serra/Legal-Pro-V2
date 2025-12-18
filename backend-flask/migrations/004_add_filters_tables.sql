
-- Migration: Add tables for filters (fases, comarcas, advogados) and update processos table
-- Date: 2025-12-18

-- 1. Create Fases table
CREATE TABLE IF NOT EXISTS fases (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    ativo BOOLEAN DEFAULT TRUE
);

-- 2. Create Comarcas table
CREATE TABLE IF NOT EXISTS comarcas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    uf VARCHAR(2) NOT NULL,
    ativo BOOLEAN DEFAULT TRUE
);

-- 3. Create Advogados table
CREATE TABLE IF NOT EXISTS advogados (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    oab VARCHAR(20),
    email VARCHAR(255),
    ativo BOOLEAN DEFAULT TRUE
);

-- 4. Add advogado_id to processos if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processos' AND column_name='advogado_id') THEN
        ALTER TABLE processos ADD COLUMN advogado_id INTEGER REFERENCES advogados(id);
    END IF;
END $$;

-- 5. Add Foreign Key constraints for existing columns if missing (fase_id, comarca_id)
-- Note: processos table already has fase_id and comarca_id, we just ensure they point to new tables if desired.
-- Since current schema might have them as simple integers without FK constraint, let's add FKs safely.

DO $$
BEGIN
    -- Check if constraint exists, if not add it
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name='fk_processos_fase') THEN
        -- We might need to clean up data first if IDs don't match, but assuming empty or compatible
        ALTER TABLE processos ADD CONSTRAINT fk_processos_fase FOREIGN KEY (fase_id) REFERENCES fases(id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name='fk_processos_comarca') THEN
        ALTER TABLE processos ADD CONSTRAINT fk_processos_comarca FOREIGN KEY (comarca_id) REFERENCES comarcas(id);
    END IF;
END $$;

-- 6. Insert default data
INSERT INTO fases (nome, descricao) VALUES 
('Inicial', 'Fase inicial do processo'),
('Instrução', 'Fase de coleta de provas'),
('Decisória', 'Aguardando decisão'),
('Recursal', 'Em grau de recurso'),
('Execução', 'Cumprimento de sentença'),
('Arquivado', 'Processo finalizado')
ON CONFLICT DO NOTHING;

INSERT INTO comarcas (nome, uf) VALUES
('São Paulo', 'SP'),
('Rio de Janeiro', 'RJ'),
('Brasília', 'DF'),
('Campinas', 'SP'),
('Belo Horizonte', 'MG')
ON CONFLICT DO NOTHING;

INSERT INTO advogados (nome, oab) VALUES
('Dr. João Silva', 'SP12345'),
('Dra. Maria Santos', 'RJ54321')
ON CONFLICT DO NOTHING;
