-- Migration: Add all BACEN indices to database
-- Adds 17 monetary indices from BACEN SGS API

-- Taxas de Juros
INSERT INTO indice_monetario (nome, codigo, descricao, fonte_oficial, ativo) 
VALUES 
    ('SELIC', 'SELIC', 'Taxa básica de juros - Meta COPOM', 'Banco Central do Brasil', true),
    ('SELIC-EFETIVA', 'SELIC-EFETIVA', 'Taxa SELIC Efetiva', 'Banco Central do Brasil', true),
    ('CDI', 'CDI', 'Certificado de Depósito Interbancário', 'B3/CETIP', true),
    ('TJLP', 'TJLP', 'Taxa de Juros de Longo Prazo', 'Banco Central do Brasil', true),
    ('TR', 'TR', 'Taxa Referencial', 'Banco Central do Brasil', true)
ON CONFLICT (nome) DO NOTHING;

-- Índices de Preços
INSERT INTO indice_monetario (nome, codigo, descricao, fonte_oficial, ativo) 
VALUES 
    ('IPCA', 'IPCA', 'Índice de Preços ao Consumidor Amplo', 'IBGE', true),
    ('IPCA-E', 'IPCA-E', 'IPCA Especial - prévia do IPCA', 'IBGE', true),
    ('INPC', 'INPC', 'Índice Nacional de Preços ao Consumidor', 'IBGE', true),
    ('IGP-M', 'IGP-M', 'Índice Geral de Preços do Mercado', 'FGV', true),
    ('IGP-DI', 'IGP-DI', 'Índice Geral de Preços - Disponibilidade Interna', 'FGV', true),
    ('IPC-FIPE', 'IPC-FIPE', 'Índice de Preços ao Consumidor FIPE', 'FIPE/USP', true)
ON CONFLICT (nome) DO NOTHING;

-- Poupança
INSERT INTO indice_monetario (nome, codigo, descricao, fonte_oficial, ativo) 
VALUES 
    ('POUPANCA', 'POUPANCA', 'Rentabilidade da Poupança', 'Banco Central do Brasil', true),
    ('POUPANCA-NOVA', 'POUPANCA-NOVA', 'Poupança Nova Regra (após 2012)', 'Banco Central do Brasil', true)
ON CONFLICT (nome) DO NOTHING;

-- Câmbio
INSERT INTO indice_monetario (nome, codigo, descricao, fonte_oficial, ativo) 
VALUES 
    ('DOLAR-PTAX', 'DOLAR-PTAX', 'Dólar PTAX - Taxa de câmbio', 'Banco Central do Brasil', true),
    ('EURO-PTAX', 'EURO-PTAX', 'Euro PTAX - Taxa de câmbio', 'Banco Central do Brasil', true)
ON CONFLICT (nome) DO NOTHING;

-- Especiais Tributários
INSERT INTO indice_monetario (nome, codigo, descricao, fonte_oficial, ativo) 
VALUES 
    ('UFIR', 'UFIR', 'Unidade Fiscal de Referência (até 2000)', 'Receita Federal', true)
ON CONFLICT (nome) DO NOTHING;

-- Índices Estaduais SP (não disponíveis no BACEN, atualizados manualmente)
INSERT INTO indice_monetario (nome, codigo, descricao, fonte_oficial, ativo) 
VALUES 
    ('UFESP', 'UFESP', 'Unidade Fiscal do Estado de São Paulo', 'SEFAZ-SP', true),
    ('LEI-13918', 'LEI-13918', 'Juros Lei 13.918/09 SP (SELIC + 1%)', 'SEFAZ-SP', true)
ON CONFLICT (nome) DO NOTHING;
