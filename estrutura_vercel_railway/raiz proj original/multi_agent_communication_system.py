"""
Sistema de Comunicação Multi-Agente
Implementa arquitetura de conexão entre agentes para compartilhamento de conhecimento
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TipoConexao(Enum):
    """Tipos de conexão entre agentes"""
    INTRA_AREA = "intra_area"  # Dentro da mesma área jurídica
    INTER_AREA = "inter_area"  # Entre áreas diferentes
    HIERARQUICA = "hierarquica"  # Relação de especialização
    COLABORATIVA = "colaborativa"  # Colaboração específica

@dataclass
class MensagemAgente:
    """Estrutura de mensagem entre agentes"""
    id: str
    agente_origem_id: int
    agente_destino_id: int
    tipo_consulta: str
    conteudo: str
    contexto: Dict[str, Any]
    timestamp: datetime
    prioridade: int = 1  # 1-5, onde 5 é crítico
    status: str = "pendente"  # pendente, processando, concluido, erro

@dataclass
class ConexaoAgente:
    """Definição de conexão entre agentes"""
    agente_primario_id: int
    agente_secundario_id: int
    tipo_conexao: TipoConexao
    peso_confianca: float  # 0.0-1.0
    areas_colaboracao: List[str]
    ativo: bool = True

class MultiAgentCommunicationSystem:
    """Sistema principal de comunicação entre agentes"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.engine = create_engine(self.database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        self.setup_communication_tables()
        
        # Cache de conexões ativas
        self._conexoes_cache = {}
        self._agentes_por_area = {}
        self._hierarquia_especialistas = {}
        
        self._carregar_estrutura_agentes()
    
    def setup_communication_tables(self):
        """Cria tabelas necessárias para comunicação entre agentes"""
        try:
            with self.engine.connect() as conn:
                # Tabela de conexões entre agentes
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS agent_connections (
                        id SERIAL PRIMARY KEY,
                        agente_primario_id INTEGER NOT NULL REFERENCES agente_juridico(id),
                        agente_secundario_id INTEGER NOT NULL REFERENCES agente_juridico(id),
                        tipo_conexao VARCHAR(20) NOT NULL,
                        peso_confianca FLOAT DEFAULT 0.5,
                        areas_colaboracao JSON,
                        ativo BOOLEAN DEFAULT TRUE,
                        criado_em TIMESTAMP DEFAULT NOW(),
                        atualizado_em TIMESTAMP DEFAULT NOW(),
                        UNIQUE(agente_primario_id, agente_secundario_id, tipo_conexao)
                    );
                """))
                
                # Tabela de mensagens entre agentes
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS agent_messages (
                        id SERIAL PRIMARY KEY,
                        agente_origem_id INTEGER NOT NULL REFERENCES agente_juridico(id),
                        agente_destino_id INTEGER NOT NULL REFERENCES agente_juridico(id),
                        tipo_consulta VARCHAR(50) NOT NULL,
                        conteudo TEXT NOT NULL,
                        contexto JSON,
                        prioridade INTEGER DEFAULT 1,
                        status VARCHAR(20) DEFAULT 'pendente',
                        resposta TEXT,
                        processado_em TIMESTAMP,
                        criado_em TIMESTAMP DEFAULT NOW()
                    );
                """))
                
                # Tabela de sessões colaborativas
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS collaborative_sessions (
                        id SERIAL PRIMARY KEY,
                        sessao_id VARCHAR(100) UNIQUE NOT NULL,
                        agentes_participantes JSON NOT NULL,
                        area_principal VARCHAR(100) NOT NULL,
                        objetivo TEXT NOT NULL,
                        status VARCHAR(20) DEFAULT 'ativa',
                        resultado JSON,
                        criado_em TIMESTAMP DEFAULT NOW(),
                        finalizado_em TIMESTAMP
                    );
                """))
                
                # Índices para performance
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_agent_connections_primary ON agent_connections(agente_primario_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_agent_messages_origem ON agent_messages(agente_origem_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_agent_messages_status ON agent_messages(status);"))
                
                conn.commit()
                logger.info("✅ Tabelas de comunicação multi-agente criadas com sucesso")
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas de comunicação: {str(e)}")
            raise
    
    def _carregar_estrutura_agentes(self):
        """Carrega estrutura atual dos agentes do banco"""
        try:
            with self.Session() as session:
                result = session.execute(text("""
                    SELECT a.id, a.nome, a.nivel_especializacao, a.detalhes_tecnicos,
                           c.nome as categoria_nome, c.id as categoria_id
                    FROM agente_juridico a
                    JOIN categoria_juridica c ON a.categoria_id = c.id
                    WHERE a.ativo = true AND c.ativa = true
                    ORDER BY c.nome, a.nivel_especializacao DESC
                """))
                
                agentes = result.fetchall()
                
                # Organizar por área
                for agente in agentes:
                    categoria = agente.categoria_nome
                    if categoria not in self._agentes_por_area:
                        self._agentes_por_area[categoria] = []
                    
                    self._agentes_por_area[categoria].append({
                        'id': agente.id,
                        'nome': agente.nome,
                        'nivel': agente.nivel_especializacao,
                        'detalhes': json.loads(agente.detalhes_tecnicos) if agente.detalhes_tecnicos else {}
                    })
                
                # Criar hierarquia por especialização
                for categoria, agentes_cat in self._agentes_por_area.items():
                    agentes_ordenados = sorted(agentes_cat, key=lambda x: x['nivel'], reverse=True)
                    self._hierarquia_especialistas[categoria] = agentes_ordenados
                
                logger.info(f"✅ Estrutura carregada: {len(self._agentes_por_area)} áreas, total de agentes mapeados")
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar estrutura de agentes: {str(e)}")
    
    def criar_conexoes_automaticas(self):
        """Cria conexões automáticas baseadas na estrutura atual"""
        try:
            conexoes_criadas = 0
            
            # 1. Conexões intra-área (dentro da mesma especialidade)
            for categoria, agentes in self._agentes_por_area.items():
                for i, agente_principal in enumerate(agentes):
                    for agente_secundario in agentes[i+1:]:
                        # Conectar agentes da mesma área
                        conexao = ConexaoAgente(
                            agente_primario_id=agente_principal['id'],
                            agente_secundario_id=agente_secundario['id'],
                            tipo_conexao=TipoConexao.INTRA_AREA,
                            peso_confianca=0.8,  # Alta confiança na mesma área
                            areas_colaboracao=[categoria]
                        )
                        self._salvar_conexao(conexao)
                        conexoes_criadas += 1
            
            # 2. Conexões hierárquicas (especialista principal -> outros)
            for categoria, agentes in self._hierarquia_especialistas.items():
                if len(agentes) > 1:
                    especialista_principal = agentes[0]  # Maior nível
                    for agente_subordinado in agentes[1:]:
                        conexao = ConexaoAgente(
                            agente_primario_id=especialista_principal['id'],
                            agente_secundario_id=agente_subordinado['id'],
                            tipo_conexao=TipoConexao.HIERARQUICA,
                            peso_confianca=0.9,  # Muito alta para hierarquia
                            areas_colaboracao=[categoria]
                        )
                        self._salvar_conexao(conexao)
                        conexoes_criadas += 1
            
            # 3. Conexões inter-área (áreas relacionadas)
            conexoes_inter_area = self._definir_conexoes_inter_areas()
            for conexao_inter in conexoes_inter_area:
                self._salvar_conexao(conexao_inter)
                conexoes_criadas += 1
            
            logger.info(f"✅ {conexoes_criadas} conexões automáticas criadas")
            return conexoes_criadas
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar conexões automáticas: {str(e)}")
            return 0
    
    def _definir_conexoes_inter_areas(self) -> List[ConexaoAgente]:
        """Define conexões lógicas entre áreas jurídicas relacionadas"""
        conexoes = []
        
        # Mapeamento de áreas relacionadas
        areas_relacionadas = {
            'Direito Penal': ['Direito Processual Penal', 'Direito Constitucional'],
            'Direito Civil': ['Direito Processual Civil', 'Direito do Consumidor'],
            'Direito Trabalhista': ['Direito Previdenciário', 'Direito Sindical'],
            'Direito Tributário': ['Direito Financeiro', 'Direito Administrativo'],
            'Direito Empresarial': ['Direito Tributário', 'Direito do Trabalho'],
            'Direito Ambiental': ['Direito Administrativo', 'Direito Agrário'],
            'Direito Digital': ['Direito Civil', 'Direito Penal', 'Direito do Consumidor'],
            'Direito Bancário': ['Direito Civil', 'Direito do Consumidor'],
            'Análise de Riscos Jurídicos': ['Direito Civil', 'Direito Empresarial', 'Direito Penal']
        }
        
        for area_principal, areas_secundarias in areas_relacionadas.items():
            if area_principal in self._agentes_por_area:
                agente_principal = self._hierarquia_especialistas[area_principal][0]  # Especialista principal
                
                for area_secundaria in areas_secundarias:
                    if area_secundaria in self._agentes_por_area:
                        agente_secundario = self._hierarquia_especialistas[area_secundaria][0]
                        
                        conexao = ConexaoAgente(
                            agente_primario_id=agente_principal['id'],
                            agente_secundario_id=agente_secundario['id'],
                            tipo_conexao=TipoConexao.INTER_AREA,
                            peso_confianca=0.7,  # Confiança média entre áreas
                            areas_colaboracao=[area_principal, area_secundaria]
                        )
                        conexoes.append(conexao)
        
        return conexoes
    
    def _salvar_conexao(self, conexao: ConexaoAgente):
        """Salva conexão no banco de dados"""
        try:
            with self.Session() as session:
                session.execute(text("""
                    INSERT INTO agent_connections 
                    (agente_primario_id, agente_secundario_id, tipo_conexao, peso_confianca, areas_colaboracao)
                    VALUES (:primario, :secundario, :tipo, :peso, :areas)
                    ON CONFLICT (agente_primario_id, agente_secundario_id, tipo_conexao) 
                    DO UPDATE SET peso_confianca = :peso, areas_colaboracao = :areas, atualizado_em = NOW()
                """), {
                    'primario': conexao.agente_primario_id,
                    'secundario': conexao.agente_secundario_id,
                    'tipo': conexao.tipo_conexao.value,
                    'peso': conexao.peso_confianca,
                    'areas': json.dumps(conexao.areas_colaboracao)
                })
                session.commit()
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar conexão: {str(e)}")
    
    def enviar_consulta_agente(self, agente_origem_id: int, area_consulta: str, 
                              pergunta: str, contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """Envia consulta para agentes especializados"""
        try:
            # Encontrar melhor agente para responder
            agentes_candidatos = self._encontrar_agentes_especialistas(area_consulta, agente_origem_id)
            
            if not agentes_candidatos:
                return {
                    'success': False,
                    'message': 'Nenhum agente especialista encontrado para esta área',
                    'area_consulta': area_consulta
                }
            
            # Selecionar agente com maior peso de confiança
            melhor_agente = max(agentes_candidatos, key=lambda x: x['peso_confianca'])
            
            # Criar mensagem
            mensagem = MensagemAgente(
                id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agente_origem_id}",
                agente_origem_id=agente_origem_id,
                agente_destino_id=melhor_agente['id'],
                tipo_consulta=area_consulta,
                conteudo=pergunta,
                contexto=contexto or {},
                timestamp=datetime.now()
            )
            
            # Salvar mensagem
            mensagem_id = self._salvar_mensagem(mensagem)
            
            # Processar resposta (simulação - aqui integraria com o agente real)
            resposta = self._processar_consulta_agente(mensagem, melhor_agente)
            
            return {
                'success': True,
                'mensagem_id': mensagem_id,
                'agente_consultor': melhor_agente['nome'],
                'resposta': resposta,
                'peso_confianca': melhor_agente['peso_confianca']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar consulta: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _encontrar_agentes_especialistas(self, area_consulta: str, agente_origem_id: int) -> List[Dict]:
        """Encontra agentes especializados para uma área específica"""
        try:
            with self.Session() as session:
                result = session.execute(text("""
                    SELECT DISTINCT 
                        a.id, a.nome, a.nivel_especializacao,
                        c.nome as categoria_nome,
                        ac.peso_confianca,
                        ac.tipo_conexao
                    FROM agente_juridico a
                    JOIN categoria_juridica c ON a.categoria_id = c.id
                    JOIN agent_connections ac ON (
                        (ac.agente_primario_id = :origem AND ac.agente_secundario_id = a.id) OR
                        (ac.agente_secundario_id = :origem AND ac.agente_primario_id = a.id)
                    )
                    WHERE a.ativo = true 
                    AND c.ativa = true
                    AND ac.ativo = true
                    AND (c.nome ILIKE :area OR ac.areas_colaboracao::text ILIKE :area)
                    ORDER BY ac.peso_confianca DESC, a.nivel_especializacao DESC
                    LIMIT 5
                """), {
                    'origem': agente_origem_id,
                    'area': f'%{area_consulta}%'
                })
                
                return [dict(row) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar especialistas: {str(e)}")
            return []
    
    def _salvar_mensagem(self, mensagem: MensagemAgente) -> int:
        """Salva mensagem no banco de dados"""
        try:
            with self.Session() as session:
                result = session.execute(text("""
                    INSERT INTO agent_messages 
                    (agente_origem_id, agente_destino_id, tipo_consulta, conteudo, contexto, prioridade, status)
                    VALUES (:origem, :destino, :tipo, :conteudo, :contexto, :prioridade, :status)
                    RETURNING id
                """), {
                    'origem': mensagem.agente_origem_id,
                    'destino': mensagem.agente_destino_id,
                    'tipo': mensagem.tipo_consulta,
                    'conteudo': mensagem.conteudo,
                    'contexto': json.dumps(mensagem.contexto),
                    'prioridade': mensagem.prioridade,
                    'status': mensagem.status
                })
                
                mensagem_id = result.fetchone()[0]
                session.commit()
                return mensagem_id
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar mensagem: {str(e)}")
            return None
    
    def _processar_consulta_agente(self, mensagem: MensagemAgente, agente_destino: Dict) -> str:
        """Processa consulta usando o agente especialista (integração futura com IA)"""
        # Esta função seria expandida para integrar com o sistema de IA real
        return f"""
        Resposta do {agente_destino['nome']} (Especialização: {agente_destino['categoria_nome']}):
        
        Com base na consulta sobre "{mensagem.tipo_consulta}", posso fornecer a seguinte análise especializada:
        
        [Aqui seria integrada a resposta real do modelo de IA do agente, usando suas configurações específicas]
        
        Nível de confiança: {agente_destino['peso_confianca']:.1%}
        Área de especialização: {agente_destino['categoria_nome']}
        """
    
    def iniciar_sessao_colaborativa(self, agentes_ids: List[int], area_principal: str, 
                                   objetivo: str) -> str:
        """Inicia uma sessão colaborativa entre múltiplos agentes"""
        try:
            sessao_id = f"collab_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with self.Session() as session:
                session.execute(text("""
                    INSERT INTO collaborative_sessions 
                    (sessao_id, agentes_participantes, area_principal, objetivo)
                    VALUES (:sessao_id, :agentes, :area, :objetivo)
                """), {
                    'sessao_id': sessao_id,
                    'agentes': json.dumps(agentes_ids),
                    'area': area_principal,
                    'objetivo': objetivo
                })
                session.commit()
            
            logger.info(f"✅ Sessão colaborativa {sessao_id} iniciada com {len(agentes_ids)} agentes")
            return sessao_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sessão colaborativa: {str(e)}")
            return None
    
    def obter_estatisticas_comunicacao(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de comunicação"""
        try:
            with self.Session() as session:
                # Estatísticas de conexões
                conexoes_result = session.execute(text("""
                    SELECT tipo_conexao, COUNT(*) as total
                    FROM agent_connections 
                    WHERE ativo = true
                    GROUP BY tipo_conexao
                """))
                
                # Estatísticas de mensagens
                mensagens_result = session.execute(text("""
                    SELECT status, COUNT(*) as total
                    FROM agent_messages 
                    WHERE criado_em >= NOW() - INTERVAL '7 days'
                    GROUP BY status
                """))
                
                # Agentes mais ativos
                agentes_ativos_result = session.execute(text("""
                    SELECT a.nome, COUNT(m.id) as total_mensagens
                    FROM agente_juridico a
                    JOIN agent_messages m ON (m.agente_origem_id = a.id OR m.agente_destino_id = a.id)
                    WHERE m.criado_em >= NOW() - INTERVAL '7 days'
                    GROUP BY a.id, a.nome
                    ORDER BY total_mensagens DESC
                    LIMIT 10
                """))
                
                return {
                    'conexoes_por_tipo': dict(conexoes_result.fetchall()),
                    'mensagens_por_status': dict(mensagens_result.fetchall()),
                    'agentes_mais_ativos': [dict(row) for row in agentes_ativos_result.fetchall()],
                    'total_areas': len(self._agentes_por_area),
                    'total_agentes': sum(len(agentes) for agentes in self._agentes_por_area.values())
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            return {}


# Exemplo de uso
if __name__ == "__main__":
    # Inicializar sistema
    sistema_comunicacao = MultiAgentCommunicationSystem()
    
    # Criar conexões automáticas
    conexoes_criadas = sistema_comunicacao.criar_conexoes_automaticas()
    print(f"Conexões criadas: {conexoes_criadas}")
    
    # Exemplo de consulta entre agentes
    resultado = sistema_comunicacao.enviar_consulta_agente(
        agente_origem_id=1,
        area_consulta="Direito Penal",
        pergunta="Qual é a interpretação atual sobre legítima defesa putativa?",
        contexto={"caso": "homicídio", "urgencia": "alta"}
    )
    
    print("Resultado da consulta:", resultado)
    
    # Estatísticas
    stats = sistema_comunicacao.obter_estatisticas_comunicacao()
    print("Estatísticas:", stats)