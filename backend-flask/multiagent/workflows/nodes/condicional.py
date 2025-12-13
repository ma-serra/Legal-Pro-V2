"""
Nó condicional para fluxos de trabalho.
"""
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CondicionalNode:
    """
    Nó condicional que permite direcionamento do fluxo com base em condições.
    
    Este nó avalia uma ou mais condições e decide o caminho a seguir no fluxo de trabalho.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o nó condicional.
        
        Args:
            config: Configurações do nó condicional
                - nome: Nome do nó
                - condicoes: Lista de condições a serem avaliadas
                - caminho_padrao: Caminho padrão se nenhuma condição for atendida
        """
        self.nome = config.get('nome', 'Condicional')
        self.condicoes = config.get('condicoes', [])
        self.caminho_padrao = config.get('caminho_padrao')
        self.contexto = config.get('contexto', {})
        
    def processar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa os dados e determina o caminho a seguir.
        
        Args:
            dados: Dados de entrada (acumulados dos nós anteriores)
            
        Returns:
            Resultado com indicação do caminho selecionado
        """
        try:
            logger.debug(f"Processando condicional '{self.nome}' com {len(self.condicoes)} condições")
            
            # Se não há condições, retorna o caminho padrão
            if not self.condicoes:
                logger.debug(f"Sem condições definidas, usando caminho padrão: {self.caminho_padrao}")
                return {
                    'resultado_condicional': {
                        'condicao_acionada': None,
                        'caminho_selecionado': self.caminho_padrao,
                        'descricao': "Nenhuma condição definida, usando caminho padrão"
                    }
                }
            
            # Avalia cada condição até encontrar uma que seja verdadeira
            for idx, condicao in enumerate(self.condicoes):
                expressao = condicao.get('expressao', '')
                caminho = condicao.get('caminho', '')
                descricao = condicao.get('descricao', f'Condição {idx+1}')
                
                if not expressao or not caminho:
                    logger.warning(f"Condição {idx+1} mal configurada, ignorando")
                    continue
                
                # Avalia a expressão
                resultado = self._avaliar_expressao(expressao, dados)
                
                if resultado:
                    logger.debug(f"Condição atendida: {descricao} - Seguindo para: {caminho}")
                    return {
                        'resultado_condicional': {
                            'condicao_acionada': descricao,
                            'caminho_selecionado': caminho,
                            'expressao_avaliada': expressao,
                            'descricao': f"Condição atendida: {descricao}"
                        }
                    }
            
            # Se nenhuma condição foi atendida, usa o caminho padrão
            logger.debug(f"Nenhuma condição atendida, usando caminho padrão: {self.caminho_padrao}")
            return {
                'resultado_condicional': {
                    'condicao_acionada': None,
                    'caminho_selecionado': self.caminho_padrao,
                    'descricao': "Nenhuma condição atendida, usando caminho padrão"
                }
            }
                
        except Exception as e:
            logger.error(f"Erro ao processar condicional: {str(e)}")
            return {
                'erro': f"Erro ao processar condicional: {str(e)}",
                'resultado_condicional': {
                    'erro': True,
                    'caminho_selecionado': self.caminho_padrao,
                    'descricao': f"Erro: {str(e)}"
                }
            }
    
    def _avaliar_expressao(self, expressao: str, dados: Dict[str, Any]) -> bool:
        """
        Avalia uma expressão de condição usando os dados.
        
        Args:
            expressao: Expressão a ser avaliada
            dados: Dados para avaliação
            
        Returns:
            True se a condição for atendida, False caso contrário
        """
        try:
            # Substitui variáveis na expressão
            for chave, valor in dados.items():
                # Para cada nível de dados aninhados
                if isinstance(valor, dict):
                    for sub_chave, sub_valor in valor.items():
                        var_nome = f"${chave}.{sub_chave}"
                        if var_nome in expressao:
                            expressao = expressao.replace(var_nome, self._formatar_valor(sub_valor))
                
                # Substituição direta
                var_nome = f"${chave}"
                if var_nome in expressao:
                    expressao = expressao.replace(var_nome, self._formatar_valor(valor))
            
            # Converte operadores textuais para Python
            expressao = expressao.replace(' E ', ' and ').replace(' OU ', ' or ').replace(' NÃO ', ' not ')
            expressao = expressao.replace(' CONTÉM ', ' in ').replace(' IGUAL ', ' == ')
            
            # Avalia a expressão
            logger.debug(f"Avaliando expressão processada: {expressao}")
            
            # Sandbox para avaliação segura
            resultado = eval(expressao, {"__builtins__": {}}, {})
            return bool(resultado)
            
        except Exception as e:
            logger.error(f"Erro ao avaliar expressão '{expressao}': {str(e)}")
            return False
    
    def _formatar_valor(self, valor: Any) -> str:
        """
        Formata um valor para uso em expressões.
        
        Args:
            valor: Valor a ser formatado
            
        Returns:
            String formatada para uso em expressões
        """
        if valor is None:
            return 'None'
        elif isinstance(valor, bool):
            return str(valor).lower()
        elif isinstance(valor, (int, float)):
            return str(valor)
        elif isinstance(valor, str):
            return f"'{valor}'"
        elif isinstance(valor, (list, dict)):
            return json.dumps(valor)
        else:
            return str(valor)