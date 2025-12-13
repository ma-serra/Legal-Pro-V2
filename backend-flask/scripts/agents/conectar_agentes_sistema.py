#!/usr/bin/env python3
"""
Script para conectar todos os agentes jurídicos ao sistema de análise
e verificar suas bases vetoriais.
"""

import os
import sys
sys.path.append('.')

from main import app, db
from models import AgenteJuridico

# Mapeamento de classes para tipos de agentes
AGENTES_MAPPING = {
    # Agentes criminais especializados
    'EspecialistaDireitoCriminalAgent': 'direito_criminal',
    'AnalistaEvidenciasCriminaisAgent': 'direito_criminal', 
    'EspecialistaExecucaoPenalAgent': 'direito_criminal',
    'AssessorSustentacaoJuriAgent': 'direito_criminal',
    
    # Agentes bancários
    'EspecialistaDireitoBancarioAgent': 'direito_bancario',
    
    # Agentes trabalhistas
    'EspecialistaDireitoTrabalhistaAgent': 'direito_trabalhista',
    
    # Agentes empresariais
    'EspecialistaDireitoEmpresarialAgent': 'direito_empresarial',
    
    # Agentes tributários
    'EspecialistaDireitoTributarioAgent': 'direito_tributario',
    
    # Agentes previdenciários
    'ConsultorDireitoPrevidenciarioAgent': 'direito_previdenciario',
    
    # Agentes securitários
    'EspecialistaDireitoSecuritarioAgent': 'direito_securitario',
    
    # Agentes imobiliários
    'EspecialistaDireitoImobiliarioAgent': 'direito_imobiliario',
    
    # Agentes digitais
    'EspecialistaDireitoDigitalAgent': 'direito_digital',
    
    # Agentes de riscos
    'AnalistaRiscosJuridicosAgent': 'direito_empresarial',
    
    # Agentes padrão por base vetorial
    'AgentePadrao': {
        'embeddings_direito_penal': 'direito_criminal',
        'embeddings_direito_bancario': 'direito_bancario',
        'embeddings_direito_trabalhista': 'direito_trabalhista',
        'embeddings_direito_empresarial': 'direito_empresarial',
        'embeddings_direito_tributario': 'direito_tributario',
        'embeddings_direito_previdenciario': 'direito_previdenciario',
        'embeddings_direito_securitario': 'direito_securitario',
        'embeddings_direito_imobiliario': 'direito_imobiliario',
        'embeddings_direito_digital': 'direito_digital',
        'embeddings_direito_consumidor': 'direito_consumidor',
        'embeddings_direito_agrario': 'direito_agrario',
        'embeddings_recuperacao_credito': 'recuperacao_credito',
        'embeddings_negociacao_conflitos': 'negociacao_conflitos'
    }
}

def conectar_agentes():
    """Conecta todos os agentes ao sistema de análise."""
    with app.app_context():
        print("🔗 Conectando agentes ao sistema de análise...")
        
        # Buscar todos os agentes ativos
        agentes = AgenteJuridico.query.filter_by(ativo=True).all()
        print(f"📊 Encontrados {len(agentes)} agentes ativos")
        
        agentes_conectados = 0
        agentes_com_problema = 0
        
        for agente in agentes:
            try:
                # Determinar o tipo do agente
                tipo_agente = None
                
                if agente.classe in AGENTES_MAPPING:
                    if isinstance(AGENTES_MAPPING[agente.classe], str):
                        tipo_agente = AGENTES_MAPPING[agente.classe]
                    elif isinstance(AGENTES_MAPPING[agente.classe], dict):
                        # AgentePadrao - verificar base vetorial
                        if agente.base_vetorial in AGENTES_MAPPING[agente.classe]:
                            tipo_agente = AGENTES_MAPPING[agente.classe][agente.base_vetorial]
                
                if not tipo_agente:
                    print(f"⚠️  Agente {agente.nome} (ID: {agente.id}) - Tipo não mapeado: {agente.classe}, Base: {agente.base_vetorial}")
                    agentes_com_problema += 1
                    continue
                
                # Verificar se a base vetorial existe
                base_vetorial = agente.base_vetorial or f'embeddings_{tipo_agente}'
                
                # Atualizar agente se necessário
                atualizado = False
                if not agente.base_vetorial:
                    agente.base_vetorial = base_vetorial
                    atualizado = True
                
                if atualizado:
                    db.session.add(agente)
                    print(f"✅ Agente {agente.nome} (ID: {agente.id}) - Conectado ao tipo: {tipo_agente}")
                else:
                    print(f"✅ Agente {agente.nome} (ID: {agente.id}) - Já conectado ao tipo: {tipo_agente}")
                
                agentes_conectados += 1
                
            except Exception as e:
                print(f"❌ Erro ao processar agente {agente.nome} (ID: {agente.id}): {str(e)}")
                agentes_com_problema += 1
        
        # Salvar alterações
        try:
            db.session.commit()
            print(f"\n📈 Resumo:")
            print(f"   ✅ Agentes conectados: {agentes_conectados}")
            print(f"   ⚠️  Agentes com problema: {agentes_com_problema}")
            print(f"   💾 Alterações salvas no banco de dados")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao salvar alterações: {str(e)}")

def verificar_bases_vetoriais():
    """Verifica se todas as bases vetoriais necessárias existem."""
    with app.app_context():
        print("\n🔍 Verificando bases vetoriais...")
        
        from sqlalchemy import text
        
        # Listar todas as tabelas de embeddings
        result = db.session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'embeddings_%'
            ORDER BY table_name
        """))
        
        bases_existentes = [row[0] for row in result.fetchall()]
        
        print(f"📊 Bases vetoriais encontradas: {len(bases_existentes)}")
        for base in bases_existentes:
            print(f"   📁 {base}")
        
        # Verificar agentes sem base vetorial
        agentes_sem_base = AgenteJuridico.query.filter(
            AgenteJuridico.ativo == True,
            AgenteJuridico.base_vetorial.is_(None)
        ).all()
        
        if agentes_sem_base:
            print(f"\n⚠️  Agentes sem base vetorial: {len(agentes_sem_base)}")
            for agente in agentes_sem_base:
                print(f"   - {agente.nome} (ID: {agente.id}, Classe: {agente.classe})")

def criar_agentes_especializados_faltantes():
    """Cria entradas para agentes especializados que podem estar faltando."""
    with app.app_context():
        print("\n🛠️  Verificando agentes especializados...")
        
        agentes_especializados = [
            {
                'nome': 'Especialista em Direito Criminal',
                'classe': 'EspecialistaDireitoCriminalAgent',
                'descricao': 'Analisa casos criminais, fornecendo análise técnica sobre tipos penais, procedimentos, jurisprudência e estratégias de defesa ou acusação.',
                'base_vetorial': 'embeddings_direito_penal',
                'categoria_id': 1
            },
            {
                'nome': 'Especialista em Direito Bancário',
                'classe': 'EspecialistaDireitoBancarioAgent', 
                'descricao': 'Especializado na análise de contratos bancários, operações financeiras e conformidade regulatória bancária.',
                'base_vetorial': 'embeddings_direito_bancario',
                'categoria_id': 2
            }
        ]
        
        for agente_info in agentes_especializados:
            # Verificar se já existe
            agente_existente = AgenteJuridico.query.filter_by(
                classe=agente_info['classe']
            ).first()
            
            if not agente_existente:
                print(f"➕ Criando agente: {agente_info['nome']}")
                
                novo_agente = AgenteJuridico(
                    nome=agente_info['nome'],
                    classe=agente_info['classe'],
                    descricao=agente_info['descricao'],
                    base_vetorial=agente_info['base_vetorial'],
                    categoria_id=agente_info['categoria_id'],
                    ativo=True,
                    nivel_especializacao=5,
                    top_k=10
                )
                
                db.session.add(novo_agente)
            else:
                print(f"✅ Agente já existe: {agente_info['nome']}")
        
        try:
            db.session.commit()
            print("💾 Agentes especializados verificados e salvos")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao salvar agentes especializados: {str(e)}")

if __name__ == '__main__':
    print("🚀 Iniciando conexão de agentes ao sistema de análise")
    print("=" * 60)
    
    # Executar funções
    verificar_bases_vetoriais()
    conectar_agentes()
    criar_agentes_especializados_faltantes()
    
    print("\n" + "=" * 60)
    print("✨ Processo concluído!")