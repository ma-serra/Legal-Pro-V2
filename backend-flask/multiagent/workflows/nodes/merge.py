"""
Nó de junção (merge) para fluxos de trabalho.
"""
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MergeNode:
    """
    Nó de junção que combina múltiplos fluxos de entrada.
    
    Este nó permite mesclar dados provenientes de diferentes caminhos do fluxo,
    consolidando-os para passar para os próximos nós.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o nó de junção.
        
        Args:
            config: Configurações do nó
                - nome: Nome do nó
                - estrategia_merge: Como mesclar dados (append, merge, substituir)
                - campos_mesclagem: Campos específicos a serem mesclados
        """
        self.nome = config.get('nome', 'Junção')
        self.estrategia_merge = config.get('estrategia_merge', 'merge')
        self.campos_mesclagem = config.get('campos_mesclagem', [])
        self.contexto = config.get('contexto', {})
        
        # Rastreamento de inputs recebidos (para entradas múltiplas)
        self.entradas_recebidas = {}
        
    def processar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa os dados de entrada e os combina conforme a estratégia definida.
        
        Args:
            dados: Dados de entrada (acumulados dos nós anteriores)
            
        Returns:
            Dados combinados conforme a estratégia configurada
        """
        try:
            logger.debug(f"Processando junção '{self.nome}' com estratégia '{self.estrategia_merge}'")
            
            # Identificamos a fonte de entrada (se houver)
            fonte = dados.get('_fonte_input', 'desconhecida')
            
            # Registramos esta entrada
            self.entradas_recebidas[fonte] = dados.copy()
            
            # Se houver apenas uma entrada, simplesmente passamos adiante
            if len(self.entradas_recebidas) == 1 and fonte == 'desconhecida':
                logger.debug("Apenas uma entrada detectada, passando dados sem alteração")
                
                # Remover metadados internos
                if '_fonte_input' in dados:
                    del dados['_fonte_input']
                    
                return dados
            
            # Aplicamos a estratégia de mesclagem
            resultado = self._aplicar_estrategia_mesclagem()
            
            # Incluir metadados sobre a junção no resultado
            resultado['resultado_juncao'] = {
                'estrategia_usada': self.estrategia_merge,
                'fontes_combinadas': list(self.entradas_recebidas.keys()),
                'numero_fontes': len(self.entradas_recebidas)
            }
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar junção: {str(e)}")
            return {
                'erro': f"Erro ao processar junção: {str(e)}",
                'resultado_juncao': {
                    'erro': True,
                    'estrategia_usada': self.estrategia_merge,
                    'descricao': f"Erro: {str(e)}"
                }
            }
    
    def _aplicar_estrategia_mesclagem(self) -> Dict[str, Any]:
        """
        Aplica a estratégia de mesclagem configurada aos dados de entrada.
        
        Returns:
            Resultado da mesclagem de dados conforme a estratégia
        """
        resultado = {}
        
        # Estratégia "append": Coloca os resultados em listas
        if self.estrategia_merge == 'append':
            for fonte, dados in self.entradas_recebidas.items():
                for chave, valor in dados.items():
                    # Ignora metadados internos
                    if chave.startswith('_'):
                        continue
                        
                    # Se é um campo que deve ser mesclado específico ou se deve mesclar todos
                    if not self.campos_mesclagem or chave in self.campos_mesclagem:
                        if chave not in resultado:
                            resultado[chave] = []
                            
                        # Adiciona o valor à lista correspondente
                        if isinstance(valor, list):
                            resultado[chave].extend(valor)
                        else:
                            resultado[chave].append(valor)
                    else:
                        # Para campos não mesclados, usa o último valor recebido
                        resultado[chave] = valor
                        
        # Estratégia "substituir": Mantém apenas o último valor recebido para cada campo
        elif self.estrategia_merge == 'substituir':
            for fonte, dados in self.entradas_recebidas.items():
                for chave, valor in dados.items():
                    # Ignora metadados internos
                    if chave.startswith('_'):
                        continue
                        
                    # Sempre sobrescreve com o valor mais recente
                    resultado[chave] = valor
                    
        # Estratégia "merge" (padrão): Mescla valores, recursivamente para dicionários
        else:  # merge
            for fonte, dados in self.entradas_recebidas.items():
                for chave, valor in dados.items():
                    # Ignora metadados internos
                    if chave.startswith('_'):
                        continue
                        
                    # Campo é um dicionário: mescla recursivamente
                    if isinstance(valor, dict) and chave in resultado and isinstance(resultado[chave], dict):
                        self._mesclar_dicionarios(resultado[chave], valor)
                    # Campo é uma lista: concatena se for para mesclar este campo
                    elif isinstance(valor, list) and chave in resultado and isinstance(resultado[chave], list):
                        if not self.campos_mesclagem or chave in self.campos_mesclagem:
                            resultado[chave].extend(valor)
                        else:
                            resultado[chave] = valor
                    # Outros casos: usa o valor mais recente
                    else:
                        resultado[chave] = valor
        
        return resultado
                    
    def _mesclar_dicionarios(self, base: Dict[str, Any], novo: Dict[str, Any]) -> None:
        """
        Mescla dois dicionários recursivamente.
        
        Args:
            base: Dicionário base (será modificado)
            novo: Novo dicionário a mesclar no base
        """
        for chave, valor in novo.items():
            # Se o valor é um dicionário e a chave já existe no base como dicionário
            if isinstance(valor, dict) and chave in base and isinstance(base[chave], dict):
                self._mesclar_dicionarios(base[chave], valor)
            else:
                base[chave] = valor