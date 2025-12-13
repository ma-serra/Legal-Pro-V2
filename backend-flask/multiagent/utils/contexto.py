"""
Sistema de contexto melhorado para o sistema multi-agente.

Este módulo fornece mecanismos para melhorar a passagem de contexto entre
os agentes, permitindo uma comunicação mais eficiente e eficaz.
"""
import logging
import uuid
import json
import os
import pickle
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple

logger = logging.getLogger(__name__)

class ContextoManager:
    """
    Gerenciador de contexto para o sistema multi-agente.
    
    Fornece mecanismos para gerenciar, enriquecer e persistir contextos
    de execução entre os agentes do sistema.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Inicializa o gerenciador de contexto.
        
        Args:
            cache_dir: Diretório para armazenar contextos em cache (opcional)
        """
        self.contextos_ativos = {}
        self.historico_contextos = {}
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), "temp", "contextos")
        
        # Cria o diretório de cache se não existir
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except Exception as e:
                logger.warning(f"Não foi possível criar diretório de cache: {str(e)}")
                
    def criar_contexto(self, dados_iniciais: Optional[Dict[str, Any]] = None) -> str:
        """
        Cria um novo contexto de execução.
        
        Args:
            dados_iniciais: Dados iniciais para o contexto
            
        Returns:
            ID do contexto criado
        """
        contexto_id = str(uuid.uuid4())
        
        # Inicializa o contexto com dados padrão
        contexto = {
            "id": contexto_id,
            "criado_em": self._timestamp(),
            "ultima_atualizacao": self._timestamp(),
            "etapas_executadas": [],
            "variaveis": {},
            "memoria_compartilhada": {
                "referencias_legais": [],
                "entidades_relevantes": [],
                "insights": [],
                "riscos_identificados": [],
                "metricas": {}
            },
            "metadados": {}
        }
        
        # Adiciona dados iniciais se fornecidos
        if dados_iniciais:
            for key, value in dados_iniciais.items():
                if key in ["variaveis", "memoria_compartilhada", "metadados"]:
                    contexto[key].update(value)
                else:
                    contexto[key] = value
                    
        # Registra o contexto
        self.contextos_ativos[contexto_id] = contexto
        
        return contexto_id
        
    def atualizar_contexto(self, contexto_id: str, dados: Dict[str, Any], 
                         agente: Optional[str] = None) -> bool:
        """
        Atualiza um contexto existente com novos dados.
        
        Args:
            contexto_id: ID do contexto a ser atualizado
            dados: Dados para atualizar o contexto
            agente: Nome do agente que está atualizando (opcional)
            
        Returns:
            True se a atualização foi bem-sucedida
        """
        if contexto_id not in self.contextos_ativos:
            logger.warning(f"Tentativa de atualizar contexto inexistente: {contexto_id}")
            return False
            
        contexto = self.contextos_ativos[contexto_id]
        
        # Atualiza timestamp
        contexto["ultima_atualizacao"] = self._timestamp()
        
        # Registra etapa se um agente for especificado
        if agente:
            contexto["etapas_executadas"].append({
                "agente": agente,
                "timestamp": self._timestamp()
            })
            
        # Atualiza dados específicos
        for key, value in dados.items():
            if key in ["variaveis", "memoria_compartilhada", "metadados"]:
                self._atualizar_dicionario_aninhado(contexto[key], value)
            else:
                contexto[key] = value
                
        return True
        
    def obter_contexto(self, contexto_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém um contexto completo.
        
        Args:
            contexto_id: ID do contexto
            
        Returns:
            Dicionário com o contexto ou None se não encontrado
        """
        # Verifica se existe na memória
        if contexto_id in self.contextos_ativos:
            return self.contextos_ativos[contexto_id].copy()
            
        # Verifica se existe no histórico
        if contexto_id in self.historico_contextos:
            return self.historico_contextos[contexto_id].copy()
            
        # Tenta carregar do cache
        contexto_cache = self._carregar_contexto_cache(contexto_id)
        if contexto_cache:
            self.historico_contextos[contexto_id] = contexto_cache
            return contexto_cache.copy()
            
        return None
        
    def arquivar_contexto(self, contexto_id: str) -> bool:
        """
        Move um contexto ativo para o histórico.
        
        Args:
            contexto_id: ID do contexto a ser arquivado
            
        Returns:
            True se o arquivamento foi bem-sucedido
        """
        if contexto_id not in self.contextos_ativos:
            logger.warning(f"Tentativa de arquivar contexto inexistente: {contexto_id}")
            return False
            
        # Move para o histórico
        self.historico_contextos[contexto_id] = self.contextos_ativos.pop(contexto_id)
        
        # Salva em cache
        self._salvar_contexto_cache(contexto_id, self.historico_contextos[contexto_id])
        
        return True
        
    def limpar_contexto(self, contexto_id: str) -> bool:
        """
        Remove um contexto de todas as estruturas de dados.
        
        Args:
            contexto_id: ID do contexto a ser removido
            
        Returns:
            True se a remoção foi bem-sucedida
        """
        # Remove das estruturas de memória
        removed = False
        
        if contexto_id in self.contextos_ativos:
            self.contextos_ativos.pop(contexto_id)
            removed = True
            
        if contexto_id in self.historico_contextos:
            self.historico_contextos.pop(contexto_id)
            removed = True
            
        # Remove do cache
        cache_path = os.path.join(self.cache_dir, f"{contexto_id}.pickle")
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                removed = True
            except Exception as e:
                logger.error(f"Erro ao remover arquivo de cache: {str(e)}")
                
        return removed
        
    def enriquecer_contexto(self, contexto_id: str, enriquecedores: List[Callable]) -> bool:
        """
        Enriquece um contexto usando funções específicas.
        
        Args:
            contexto_id: ID do contexto a ser enriquecido
            enriquecedores: Lista de funções de enriquecimento
            
        Returns:
            True se o enriquecimento foi bem-sucedido
        """
        contexto = self.obter_contexto(contexto_id)
        
        if not contexto:
            logger.warning(f"Tentativa de enriquecer contexto inexistente: {contexto_id}")
            return False
            
        # Aplica cada função de enriquecimento
        for enriquecedor in enriquecedores:
            try:
                enriquecedor(contexto)
            except Exception as e:
                logger.error(f"Erro ao executar enriquecedor: {str(e)}")
                
        # Atualiza o contexto com as alterações
        if contexto_id in self.contextos_ativos:
            self.contextos_ativos[contexto_id] = contexto
        else:
            self.historico_contextos[contexto_id] = contexto
            
        return True
        
    def mesclar_contextos(self, contexto_principal_id: str, 
                         contexto_secundario_id: str,
                         priorizar_principal: bool = True) -> bool:
        """
        Mescla dois contextos em um só.
        
        Args:
            contexto_principal_id: ID do contexto principal
            contexto_secundario_id: ID do contexto a ser mesclado no principal
            priorizar_principal: Se True, dados do contexto principal têm prioridade em caso de conflito
            
        Returns:
            True se a mesclagem foi bem-sucedida
        """
        contexto_principal = self.obter_contexto(contexto_principal_id)
        contexto_secundario = self.obter_contexto(contexto_secundario_id)
        
        if not contexto_principal or not contexto_secundario:
            logger.warning("Um dos contextos não foi encontrado para mesclagem")
            return False
            
        # Mescla dados específicos
        for key in ["variaveis", "memoria_compartilhada", "metadados"]:
            if key in contexto_secundario:
                if priorizar_principal:
                    # Adiciona apenas o que não existe no principal
                    for k, v in contexto_secundario[key].items():
                        if k not in contexto_principal[key]:
                            contexto_principal[key][k] = v
                else:
                    # Sobrescreve com dados do secundário
                    contexto_principal[key].update(contexto_secundario[key])
                    
        # Adiciona etapas executadas
        contexto_principal["etapas_executadas"].extend(contexto_secundario.get("etapas_executadas", []))
        
        # Atualiza timestamp
        contexto_principal["ultima_atualizacao"] = self._timestamp()
        
        # Atualiza o contexto principal
        self.contextos_ativos[contexto_principal_id] = contexto_principal
        
        return True
        
    def _atualizar_dicionario_aninhado(self, dict_original: Dict, 
                                      dict_atualizacao: Dict):
        """
        Atualiza um dicionário de forma recursiva.
        
        Args:
            dict_original: Dicionário original a ser atualizado
            dict_atualizacao: Dicionário com atualizações
        """
        for key, value in dict_atualizacao.items():
            if key in dict_original and isinstance(dict_original[key], dict) and isinstance(value, dict):
                # Recursivamente atualiza dicionários aninhados
                self._atualizar_dicionario_aninhado(dict_original[key], value)
            elif key in dict_original and isinstance(dict_original[key], list) and isinstance(value, list):
                # Para listas, adiciona apenas itens não duplicados
                dict_original[key].extend([item for item in value if item not in dict_original[key]])
            else:
                # Substitui ou adiciona o valor
                dict_original[key] = value
                
    def _timestamp(self) -> str:
        """Retorna timestamp atual no formato ISO 8601."""
        import datetime
        return datetime.datetime.now().isoformat()
        
    def _salvar_contexto_cache(self, contexto_id: str, contexto: Dict[str, Any]) -> bool:
        """
        Salva um contexto no cache.
        
        Args:
            contexto_id: ID do contexto
            contexto: Dados do contexto
            
        Returns:
            True se o salvamento foi bem-sucedido
        """
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except Exception as e:
                logger.error(f"Erro ao criar diretório de cache: {str(e)}")
                return False
                
        try:
            cache_path = os.path.join(self.cache_dir, f"{contexto_id}.pickle")
            
            with open(cache_path, 'wb') as f:
                pickle.dump(contexto, f)
                
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar contexto em cache: {str(e)}")
            return False
            
    def _carregar_contexto_cache(self, contexto_id: str) -> Optional[Dict[str, Any]]:
        """
        Carrega um contexto do cache.
        
        Args:
            contexto_id: ID do contexto
            
        Returns:
            Dicionário com o contexto ou None se não encontrado
        """
        cache_path = os.path.join(self.cache_dir, f"{contexto_id}.pickle")
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar contexto do cache: {str(e)}")
            return None

# Instância global do gerenciador de contexto
_contexto_manager = ContextoManager()

def get_contexto_manager() -> ContextoManager:
    """
    Obtém a instância global do gerenciador de contexto.
    
    Returns:
        Instância global do ContextoManager
    """
    return _contexto_manager

# Funções de enriquecimento de exemplo
def enriquecer_com_referencias_juridicas(contexto: Dict[str, Any]):
    """
    Enriquece o contexto com referências jurídicas extraídas do texto.
    
    Args:
        contexto: Contexto a ser enriquecido
    """
    from multiagent.utils.referencias_juridicas import find_legal_standards
    
    if "texto" not in contexto:
        return
        
    texto = contexto["texto"]
    referencias = find_legal_standards(texto)
    
    # Adiciona referências encontradas
    if "memoria_compartilhada" not in contexto:
        contexto["memoria_compartilhada"] = {}
        
    if "referencias_legais" not in contexto["memoria_compartilhada"]:
        contexto["memoria_compartilhada"]["referencias_legais"] = []
        
    # Converte referências para formato simplificado
    referencias_simples = []
    
    for tipo, refs in referencias.items():
        for ref in refs:
            if ref.get('validado', False):
                referencias_simples.append({
                    "tipo": tipo,
                    "texto": ref.get("texto", ""),
                    "validado": True
                })
                
    # Adiciona apenas referências não duplicadas
    existentes = {r.get("texto") for r in contexto["memoria_compartilhada"]["referencias_legais"]}
    novas_refs = [r for r in referencias_simples if r.get("texto") not in existentes]
    
    contexto["memoria_compartilhada"]["referencias_legais"].extend(novas_refs)
    
def enriquecer_com_metadados_tempo(contexto: Dict[str, Any]):
    """
    Enriquece o contexto com metadados sobre tempo de execução.
    
    Args:
        contexto: Contexto a ser enriquecido
    """
    import datetime
    
    if "metadados" not in contexto:
        contexto["metadados"] = {}
        
    # Adiciona timestamp atual
    contexto["metadados"]["ultima_atualizacao"] = datetime.datetime.now().isoformat()
    
    # Calcula tempo decorrido desde a criação
    if "criado_em" in contexto:
        try:
            criado = datetime.datetime.fromisoformat(contexto["criado_em"])
            agora = datetime.datetime.now()
            delta = agora - criado
            
            contexto["metadados"]["tempo_decorrido_ms"] = int(delta.total_seconds() * 1000)
        except Exception:
            pass