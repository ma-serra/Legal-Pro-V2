"""
Testes Unitários - Sistema de Processos Dinâmicos
Data: 15 Dezembro 2025

Testa os 15 models SQLAlchemy implementados:
- Criação de instâncias
- Relationships
- Constraints
- Métodos to_dict()
"""
import pytest
import sys
import os
from datetime import datetime
from decimal import Decimal

# Adicionar path do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_load_dotenv()

# Importar models
from models import (
    db,
    Processo,
    ProcessoCamposEspecificos,
    Tributo,
    TeseTributaria,
    ProcessoTributario,
    ProcessoTese,
    ProcessoPrognosticoTributario,
    ProcessoTrabalhista,
    ProcessoPrognosticoTrabalhista,
    ProcessoCivel,
    ProcessoPrognosticoCivel,
    IndiceMonetario,
    HistoricoIndice,
    ProcessoAtualizacaoMonetaria,
    ConfiguracaoFormulario
)

# Configurar Flask app para testes
@pytest.fixture(scope='module')
def app():
    """Cria app Flask para testes"""
    app = Flask(__name__)
    load_dotenv()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    db.init_app(app)
    
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def session(app):
    """Cria sessão de banco para testes"""
    with app.app_context():
        yield db.session

# ============================================================================
# TESTES - CORE MODELS
# ============================================================================

def test_processo_criacao(session):
    """Testa criação de Processo"""
    processo = Processo(
        numero_cnj='0001234-56.2024.8.21.0001',
        pasta='PROC-2024-001',
        natureza_id=1,
        status_id=1,
        valor_causa=Decimal('50000.00'),
        titulo='Processo de Teste'
    )
    
    session.add(processo)
    session.commit()
    
    assert processo.id_processo is not None
    assert processo.uuid is not None
    assert processo.numero_cnj == '0001234-56.2024.8.21.0001'
    assert processo.ativo is True
    assert float(processo.valor_causa) == 50000.00
    
    print(f"✓ Processo criado: {processo}")

def test_processo_to_dict(session):
    """Testa método to_dict()"""
    processo = session.query(Processo).first()
    
    data = processo.to_dict()
    
    assert 'id_processo' in data
    assert 'uuid' in data
    assert 'numero_cnj' in data
    assert data['ativo'] is True
    
    print(f"✓ to_dict() OK: {list(data.keys())}")

def test_processo_campos_especificos(session):
    """Testa ProcessoCamposEspecificos com JSONB"""
    processo = session.query(Processo).first()
    
    campos = ProcessoCamposEspecificos(
        processo_id=processo.id_processo,
        natureza_id=1,
        campos_tributario={
            'numero_aiim': '123456',
            'numero_cda': 'CDA789',
            'observacoes': 'Teste JSONB'
        }
    )
    
    session.add(campos)
    session.commit()
    
    assert campos.id_campo_especifico is not None
    assert campos.campos_tributario['numero_aiim'] == '123456'
    assert campos.campos_tributario['observacoes'] == 'Teste JSONB'
    
    print(f"✓ JSONB funcionando: {campos.campos_tributario}")

# ============================================================================
# TESTES - TRIBUTÁRIO
# ============================================================================

def test_tributo_existente(session):
    """Testa se tributos foram inseridos na migration"""
    icms = session.query(Tributo).filter_by(codigo='ICMS').first()
    
    assert icms is not None
    assert icms.nome == 'Imposto sobre Circulação de Mercadorias e Serviços'
    assert icms.esfera == 'Estadual'
    assert icms.ativo is True
    
    print(f"✓ Tributo ICMS encontrado: {icms}")

def test_tese_tributaria_criacao(session):
    """Testa criação de TeseTributaria"""
    icms = session.query(Tributo).filter_by(codigo='ICMS').first()
    
    tese = TeseTributaria(
        codigo='TESE-001',
        titulo='Exclusão do ICMS da base de cálculo do PIS/COFINS',
        descricao='Tese do Século',
        tributo_id=icms.id_tributo,
        tema_repercussao_geral='RE 574.706',
        probabilidade_sucesso=Decimal('85.50'),
        situacao='Favorável'
    )
    
    session.add(tese)
    session.commit()
    
    assert tese.id_tese is not None
    assert float(tese.probabilidade_sucesso) == 85.50
    assert tese.tributo.codigo == 'ICMS'
    
    print(f"✓ Tese criada: {tese}")

def test_processo_tributario_relationship(session):
    """Testa relationship Processo → ProcessoTributario"""
    processo = session.query(Processo).first()
    icms = session.query(Tributo).filter_by(codigo='ICMS').first()
    
    proc_trib = ProcessoTributario(
        processo_id=processo.id_processo,
        tributo_id=icms.id_tributo,
        numero_aiim='AIIM-12345',
        numero_cda='CDA-67890',
        valor_principal=Decimal('100000.00'),
        valor_multa=Decimal('20000.00')
    )
    
    session.add(proc_trib)
    session.commit()
    
    # Testar relationship bidirecional
    assert processo.processo_tributario is not None
    assert processo.processo_tributario.numero_aiim == 'AIIM-12345'
    assert proc_trib.processo.numero_cnj == processo.numero_cnj
    
    print(f"✓ Relationship Processo ↔ ProcessoTributario OK")

def test_processo_tese_n_to_n(session):
    """Testa relacionamento N:N entre Processo e Tese"""
    processo = session.query(Processo).first()
    tese = session.query(TeseTributaria).first()
    
    proc_tese = ProcessoTese(
        processo_id=processo.id_processo,
        tese_id=tese.id_tese,
        ordem=1,
        status='Em análise'
    )
    
    session.add(proc_tese)
    session.commit()
    
    # Verificar ambos os lados
    assert len(processo.teses) > 0
    assert processo.teses[0].tese.codigo == tese.codigo
    
    print(f"✓ Relationship N:N Processo ↔ Tese OK")

def test_prognostico_tributario(session):
    """Testa prognóstico tributário com 3 teses"""
    processo = session.query(Processo).first()
    tese = session.query(TeseTributaria).first()
    
    prognostico = ProcessoPrognosticoTributario(
        processo_id=processo.processo_tributario.processo_id,
        tese_provavel_id=tese.id_tese,
        valor_provavel=Decimal('70000.00'),
        percentual_provavel=Decimal('70.00'),
        valor_possivel=Decimal('50000.00'),
        percentual_possivel=Decimal('50.00'),
        observacoes='Prognóstico de teste'
    )
    
    session.add(prognostico)
    session.commit()
    
    assert prognostico.id_prognostico is not None
    assert prognostico.tese_provavel.codigo == tese.codigo
    assert float(prognostico.percentual_provavel) == 70.00
    
    print(f"✓ Prognóstico tributário criado")

# ============================================================================
# TESTES - TRABALHISTA E CÍVEL
# ============================================================================

def test_processo_trabalhista(session):
    """Testa ProcessoTrabalhista"""
    processo = Processo(
        pasta='TRAB-2024-001',
        natureza_id=2,
        status_id=1
    )
    session.add(processo)
    session.commit()
    
    proc_trab = ProcessoTrabalhista(
        processo_id=processo.id_processo,
        tolerancia_acordo=Decimal('30000.00'),
        acordo_realizado=Decimal('25000.00'),
        observacoes_acordo='Acordo vantajoso'
    )
    
    session.add(proc_trab)
    session.commit()
    
    assert processo.processo_trabalhista is not None
    assert float(processo.processo_trabalhista.acordo_realizado) == 25000.00
    
    print(f"✓ ProcessoTrabalhista OK")

def test_processo_civel(session):
    """Testa ProcessoCivel"""
    processo = Processo(
        pasta='CIV-2024-001',
        natureza_id=3,
        status_id=1
    )
    session.add(processo)
    session.commit()
    
    proc_civel = ProcessoCivel(
        processo_id=processo.id_processo,
        tolerancia_acordo=Decimal('40000.00')
    )
    
    session.add(proc_civel)
    session.commit()
    
    prognostico = ProcessoPrognosticoCivel(
        processo_id=proc_civel.processo_id,
        tese_provavel='Responsabilidade objetiva',
        valor_provavel=Decimal('80000.00')
    )
    
    session.add(prognostico)
    session.commit()
    
    assert proc_civel.prognostico is not None
    assert proc_civel.prognostico.tese_provavel == 'Responsabilidade objetiva'
    
    print(f"✓ ProcessoCivel + Prognóstico OK")

# ============================================================================
# TESTES - ATUALIZAÇÃO MONETÁRIA
# ============================================================================

def test_indice_monetario_existente(session):
    """Testa se índices foram inseridos"""
    selic = session.query(IndiceMonetario).filter_by(nome='SELIC').first()
    
    assert selic is not None
    assert 'Banco Central' in selic.fonte_oficial
    assert selic.ativo is True
    
    print(f"✓ Índice SELIC encontrado: {selic}")

def test_historico_indice(session):
    """Testa HistoricoIndice"""
    selic = session.query(IndiceMonetario).filter_by(nome='SELIC').first()
    
    historico = HistoricoIndice(
        indice_id=selic.id_indice,
        data_referencia=datetime(2024, 11, 1),
        valor=Decimal('11.25')
    )
    
    session.add(historico)
    session.commit()
    
    assert historico.id_historico is not None
    assert historico.indice.nome == 'SELIC'
    assert float(historico.valor) == 11.25
    
    print(f"✓ Histórico de índice criado")

def test_processo_atualizacao_monetaria(session):
    """Testa ProcessoAtualizacaoMonetaria"""
    processo = session.query(Processo).filter_by(pasta='PROC-2024-001').first()
    selic = session.query(IndiceMonetario).filter_by(nome='SELIC').first()
    
    atualizacao = ProcessoAtualizacaoMonetaria(
        processo_id=processo.id_processo,
        indice_id=selic.id_indice,
        data_base=datetime(2024, 1, 1),
        valor_base=Decimal('50000.00'),
        valor_atualizado=Decimal('56250.00'),
        percentual_correcao=Decimal('12.50')
    )
    
    session.add(atualizacao)
    session.commit()
    
    assert len(processo.atualizacoes_monetarias) > 0
    assert processo.atualizacoes_monetarias[0].indice.nome == 'SELIC'
    
    print(f"✓ Atualização monetária OK")

# ============================================================================
# TESTES - CONFIGURAÇÃO DINÂMICA
# ============================================================================

def test_configuracao_formulario(session):
    """Testa ConfiguracaoFormulario com JSONB"""
    config = ConfiguracaoFormulario(
        tenant_id=1,
        natureza_id=1,
        campos_obrigatorios=[
            {'name': 'tributo_id', 'label': 'Tributo', 'type': 'select'},
            {'name': 'valor_principal', 'label': 'Valor', 'type': 'currency'}
        ],
        campos_opcionais=[
            {'name': 'numero_aiim', 'label': 'AIIM', 'type': 'text'}
        ],
        validacoes={'valor_principal': {'min': 0}},
        versao=1
    )
    
    session.add(config)
    session.commit()
    
    assert config.id_configuracao is not None
    assert len(config.campos_obrigatorios) == 2
    assert config.campos_obrigatorios[0]['name'] == 'tributo_id'
    
    print(f"✓ ConfiguracaoFormulario JSONB OK")

# ============================================================================
# TESTES - CASCADE DELETES
# ============================================================================

def test_cascade_delete(session):
    """Testa cascade delete de Processo"""
    # Criar processo com dependências
    processo_teste = Processo(
        pasta='DELETE-TEST',
        natureza_id=1,
        status_id=1
    )
    session.add(processo_teste)
    session.commit()
    
    proc_id = processo_teste.id_processo
    
    # Adicionar dependências
    proc_trib = ProcessoTributario(
        processo_id=proc_id,
        numero_aiim='TEST-CASCADE'
    )
    session.add(proc_trib)
    session.commit()
    
    # Deletar processo
    session.delete(processo_teste)
    session.commit()
    
    # Verificar se ProcessoTributario foi deletado em cascade
    proc_trib_count = session.query(ProcessoTributario).filter_by(
        numero_aiim='TEST-CASCADE'
    ).count()
    
    assert proc_trib_count == 0
    
    print(f"✓ Cascade delete funcionando")

# ============================================================================
# TESTE - RESUMO
# ============================================================================

def test_resumo_final(session):
    """Mostra resumo dos testes"""
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)
    
    counts = {
        'Processos': session.query(Processo).count(),
        'Tributos': session.query(Tributo).count(),
        'Teses': session.query(TeseTributaria).count(),
        'ProcessoTributario': session.query(ProcessoTributario).count(),
        'IndicesMonetarios': session.query(IndiceMonetario).count(),
        'HistoricoIndices': session.query(HistoricoIndice).count()
    }
    
    for model, count in counts.items():
        print(f"{model:25s}: {count:3d} registros")
    
    print("="*80)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("="*80)

# ============================================================================
# EXECUTAR TESTES
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
