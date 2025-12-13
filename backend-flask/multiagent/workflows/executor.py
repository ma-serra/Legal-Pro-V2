"""
Executor de fluxos de trabalho.
"""
import time
import datetime
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    """
    Executa fluxos de trabalho com múltiplos agentes.
    """
    
    def __init__(self, fluxo=None):
        self.fluxo = fluxo
        self.log = {
            "inicio": datetime.datetime.now().isoformat(),
            "etapas": [],
            "erros": []
        }
        
    def _registrar_etapa(self, nome, status, dados=None, tempo=0.0, erro=None):
        """Registra uma etapa na execução do fluxo"""
        etapa = {
            "nome": nome,
            "status": status,
            "tempo": tempo,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if dados:
            etapa["dados"] = dados
            
        if erro:
            etapa["erro"] = str(erro)
            
        self.log["etapas"].append(etapa)
        return etapa
        
    def _registrar_erro(self, mensagem, etapa=None, excecao=None):
        """Registra um erro na execução do fluxo"""
        erro = {
            "mensagem": mensagem,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if etapa:
            erro["etapa"] = etapa
            
        if excecao:
            erro["excecao"] = str(excecao)
            
        self.log["erros"].append(erro)
        logger.error(f"Erro no fluxo: {mensagem}")
        return erro
        
    def executar(self, texto_entrada, modo_debug=False, agentes=None):
        """
        Executa o fluxo de trabalho com os dados de entrada fornecidos.
        
        Args:
            texto_entrada: Texto a ser processado
            modo_debug: Se True, habilita logs detalhados
            agentes: Lista opcional de agentes para substituir os agentes do fluxo
            
        Returns:
            Dicionário com o resultado da execução e logs
        """
        if not self.fluxo and not agentes:
            raise ValueError("Fluxo não definido para execução e nenhum agente fornecido")
            
        self.log["modo_debug"] = modo_debug
        self.log["inicio"] = datetime.datetime.now().isoformat()
        
        resultado_final = {}
        tempo_inicio = time.time()
        
        try:
            # Informações do fluxo
            fluxo_nome = "Fluxo sem nome"
            fluxo_id = 0
            
            if isinstance(self.fluxo, dict):
                fluxo_nome = self.fluxo.get('nome', 'Fluxo sem nome')
                fluxo_id = self.fluxo.get('id', 0)
            
            # Se agentes foram fornecidos como parâmetro, use-os
            # Caso contrário, pegue do fluxo
            if agentes is None:
                if isinstance(self.fluxo, dict):
                    agentes = self.fluxo.get('agentes', [])
                else:
                    agentes = []
            
            self.log["fluxo"] = {
                "id": fluxo_id,
                "nome": fluxo_nome,
                "num_agentes": len(agentes)
            }
            
            # Verifica se há agentes no fluxo
            if not agentes:
                erro = "O fluxo não possui agentes configurados"
                self._registrar_erro(erro)
                resultado_final = {
                    "status": "erro",
                    "mensagem": erro,
                    "texto": texto_entrada
                }
                return resultado_final, self.log
            
            # Executa cada agente sequencialmente
            dados_acumulados = {
                "texto": texto_entrada,
                "memoria_compartilhada": {
                    "referencias_legais": [],
                    "entidades_relevantes": [],
                    "insights": [],
                    "riscos_identificados": [],
                    "metricas": {}
                }
            }
            
            for idx, agente_config in enumerate(agentes):
                try:
                    # Informações do agente
                    agente_nome = agente_config.get('nome', f'Agente {idx+1}')
                    agente_tipo = agente_config.get('tipo', 'desconhecido')
                    
                    # Marca o tempo de início para medir duração
                    etapa_inicio = time.time()
                    
                    # Registra início do processamento
                    self._registrar_etapa(
                        nome=agente_nome,
                        status="iniciado",
                        dados={"tipo": agente_tipo}
                    )
                    
                    # Obtém as configurações específicas deste agente
                    configuracoes = agente_config.get('configuracoes', {})
                    
                    if modo_debug:
                        logger.debug(f"Executando agente {agente_nome} com dados: {json.dumps(dados_acumulados)[:100]}...")
                    
                    # Processa com o agente especializado 
                    resultado_agente = self._processar_agente(
                        agente_tipo, 
                        agente_nome,
                        configuracoes,
                        dados_acumulados, 
                        texto_entrada
                    )
                    
                    # Acumula os dados para o próximo agente
                    if resultado_agente:
                        dados_acumulados.update(resultado_agente)
                    
                    etapa_fim = time.time()
                    tempo_etapa = etapa_fim - etapa_inicio
                    
                    self._registrar_etapa(
                        nome=agente_nome,
                        status="concluido",
                        tempo=tempo_etapa,
                        dados={"resumo": str(resultado_agente)[:100] + "..."}
                    )
                    
                except Exception as e:
                    try:
                        # Captura o tempo final para calcular duração
                        etapa_fim = time.time()
                        tempo_etapa = etapa_fim - etapa_inicio
                        
                        # Registra o erro nos logs
                        erro_msg = f"Erro ao executar agente {agente_nome}: {str(e)}"
                        self._registrar_erro(erro_msg, etapa=agente_nome, excecao=e)
                        
                        # Registra a etapa com status de erro
                        self._registrar_etapa(
                            nome=agente_nome,
                            status="erro",
                            tempo=tempo_etapa,
                            erro=str(e)
                        )
                    except NameError:
                        # Se etapa_inicio ou agente_nome não estiverem definidos, registra erro genérico
                        erro_msg = f"Erro no processamento do agente: {str(e)}"
                        self._registrar_erro(erro_msg, excecao=e)
                        
                        # Registra etapa genérica
                        self._registrar_etapa(
                            nome="Agente desconhecido",
                            status="erro",
                            erro=str(e)
                        )
                    
                    # Se não for para continuar em caso de erro, interrompe a execução
                    if not agente_config.get('continuar_em_erro', False):
                        break
            
            # Verifica se algum agente teve erro e se o resultado final foi definido
            if self.log["erros"] and not resultado_final:
                resultado_final = {
                    "status": "erro",
                    "mensagem": f"Ocorreram {len(self.log['erros'])} erros na execução",
                    "texto": texto_entrada
                }
            else:
                # Pega os dados acumulados como resultado final
                resultado_final = {
                    "status": "concluido",
                    "mensagem": "Execução concluída com sucesso",
                    "texto": texto_entrada,
                    **dados_acumulados
                }
                
        except Exception as e:
            erro_geral = f"Erro geral na execução do fluxo: {str(e)}"
            self._registrar_erro(erro_geral, excecao=e)
            
            resultado_final = {
                "status": "erro",
                "mensagem": erro_geral,
                "texto": texto_entrada
            }
            
        finally:
            # Finaliza o log
            tempo_final = time.time()
            tempo_execucao = tempo_final - tempo_inicio
            
            self.log["fim"] = datetime.datetime.now().isoformat()
            self.log["tempo_total"] = tempo_execucao
            self.log["status"] = "concluido" if not self.log["erros"] else "erro"
            
            return resultado_final, self.log
    
    def _processar_agente(self, tipo_agente, nome_agente, configuracoes, dados, texto_entrada):
        """
        Processa os dados usando um agente especializado conforme configuração.
        
        Args:
            tipo_agente: Tipo do agente a ser utilizado
            nome_agente: Nome do agente (para log)
            configuracoes: Configurações específicas do agente
            dados: Dados acumulados até o momento
            texto_entrada: Texto original de entrada
            
        Returns:
            Resultado do processamento do agente
        """
        from multiagent.agents import get_agent_by_type
        from multiagent.utils import get_fallback_manager
        from multiagent.utils import get_contexto_manager
        
        # Obtém os gerenciadores de fallback e contexto
        fallback_manager = get_fallback_manager()
        contexto_manager = get_contexto_manager()
        
        try:
            # Configura o agente usando as configurações fornecidas
            config = configuracoes.copy() if configuracoes else {}
            
            # Adiciona informações contextuais para o agente
            fluxo_id = "fluxo_id"
            fluxo_nome = "fluxo_sem_nome"
            
            if self.fluxo:
                fluxo_id = self.fluxo.get("id", "fluxo_id") 
                fluxo_nome = self.fluxo.get("nome", "fluxo_sem_nome")
                
            config.update({
                "nome": nome_agente,
                "contexto": {
                    "fluxo_id": fluxo_id,
                    "fluxo_nome": fluxo_nome,
                    "modo_debug": self.log.get("modo_debug", False)
                }
            })
            
            # Extrai ou cria o ID de contexto na memória compartilhada
            contexto_id = None
            if "memoria_compartilhada" in dados and "contexto_id" in dados["memoria_compartilhada"]:
                contexto_id = dados["memoria_compartilhada"]["contexto_id"]
            else:
                # Cria novo contexto se não existir
                contexto_inicial = {
                    "texto": texto_entrada,
                    "memoria_compartilhada": dados.get("memoria_compartilhada", {}),
                    "metadados": {
                        "fluxo_id": fluxo_id,
                        "fluxo_nome": fluxo_nome,
                        "modo_debug": self.log.get("modo_debug", False)
                    }
                }
                contexto_id = contexto_manager.criar_contexto(contexto_inicial)
                
                # Armazena o ID de contexto na memória compartilhada
                if "memoria_compartilhada" not in dados:
                    dados["memoria_compartilhada"] = {}
                dados["memoria_compartilhada"]["contexto_id"] = contexto_id
            
            # Instancia o agente especializado
            agente = get_agent_by_type(tipo_agente, config)
            
            # Processa os dados usando o agente especializado
            result = agente.processar(dados)
            
            # Atualiza o contexto com os resultados
            if result:
                contexto_manager.atualizar_contexto(
                    contexto_id, 
                    {"resultado": result}, 
                    agente=nome_agente
                )
            
            return result
            
        except ImportError as e:
            # Usa o sistema de fallback para agentes não encontrados
            logger.warning(f"Agente do tipo {tipo_agente} não encontrado. Usando fallback.")
            
            # Contexto para fallback
            contexto_fallback = {
                "texto": texto_entrada,
                "tipo_agente": tipo_agente,
                "nome_agente": nome_agente,
                "config": configuracoes
            }
            
            # Usa fallback manager para obter resultado de fallback
            return fallback_manager.handle_error(tipo_agente, e, contexto_fallback)
            
        except Exception as e:
            # Captura exceções específicas durante o processamento
            logger.error(f"Erro ao processar com o agente {nome_agente}: {str(e)}")
            
            # Contexto para fallback
            contexto_fallback = {
                "texto": texto_entrada,
                "tipo_agente": tipo_agente,
                "nome_agente": nome_agente,
                "config": configuracoes,
                "dados": dados,
                "resultados_parciais": dados.copy()
            }
            
            # Usa fallback manager para obter resultado de fallback
            return fallback_manager.handle_error(tipo_agente, e, contexto_fallback)