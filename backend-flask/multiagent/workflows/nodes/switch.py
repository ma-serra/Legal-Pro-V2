"""
Nó switch para fluxos de trabalho.
"""
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SwitchNode:
    """
    Nó switch que permite múltiplos caminhos com base em valores.
    
    Este nó avalia um valor e seleciona o caminho com base em casos predefinidos.
    Mais flexível que o condicional para cenários com múltiplas opções.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o nó switch.
        
        Args:
            config: Configurações do nó switch
                - nome: Nome do nó
                - campo_valor: Campo cujo valor será avaliado
                - casos: Lista de casos a serem comparados
                - caso_padrao: Caminho padrão se nenhum caso corresponder
        """
        self.nome = config.get('nome', 'Switch')
        self.campo_valor = config.get('campo_valor', '')
        self.casos = config.get('casos', [])
        self.caso_padrao = config.get('caso_padrao', None)
        self.contexto = config.get('contexto', {})
        
    def processar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa os dados e determina o caminho com base no valor do campo.
        
        Args:
            dados: Dados de entrada (acumulados dos nós anteriores)
            
        Returns:
            Resultado com indicação do caminho selecionado
        """
        try:
            logger.debug(f"Processando switch '{self.nome}' para campo '{self.campo_valor}'")
            
            # Obtém o valor do campo especificado
            valor = self._obter_valor(self.campo_valor, dados)
            valor_str = str(valor) if valor is not None else "None"
            
            logger.debug(f"Valor obtido para avaliação: {valor_str}")
            
            # Se não há casos, retorna o caso padrão
            if not self.casos:
                logger.debug(f"Sem casos definidos, usando caso padrão: {self.caso_padrao}")
                return {
                    'resultado_switch': {
                        'valor_avaliado': valor_str,
                        'caso_correspondente': None,
                        'caminho_selecionado': self.caso_padrao,
                        'descricao': "Nenhum caso definido, usando padrão"
                    }
                }
            
            # Avalia cada caso para encontrar uma correspondência
            for idx, caso in enumerate(self.casos):
                valor_caso = caso.get('valor')
                caminho = caso.get('caminho', '')
                descricao = caso.get('descricao', f'Caso {idx+1}')
                
                if not caminho:
                    logger.warning(f"Caso {idx+1} mal configurado, ignorando")
                    continue
                
                # Compara o valor com o caso
                if self._comparar_valores(valor, valor_caso):
                    logger.debug(f"Caso correspondente: {descricao} - Seguindo para: {caminho}")
                    return {
                        'resultado_switch': {
                            'valor_avaliado': valor_str,
                            'caso_correspondente': descricao,
                            'valor_caso': str(valor_caso),
                            'caminho_selecionado': caminho,
                            'descricao': f"Caso correspondente: {descricao}"
                        }
                    }
            
            # Se nenhum caso corresponder, usa o caso padrão
            logger.debug(f"Nenhum caso correspondente, usando caso padrão: {self.caso_padrao}")
            return {
                'resultado_switch': {
                    'valor_avaliado': valor_str,
                    'caso_correspondente': None,
                    'caminho_selecionado': self.caso_padrao,
                    'descricao': "Nenhum caso correspondente, usando padrão"
                }
            }
                
        except Exception as e:
            logger.error(f"Erro ao processar switch: {str(e)}")
            return {
                'erro': f"Erro ao processar switch: {str(e)}",
                'resultado_switch': {
                    'erro': True,
                    'caminho_selecionado': self.caso_padrao,
                    'descricao': f"Erro: {str(e)}"
                }
            }
    
    def _obter_valor(self, campo: str, dados: Dict[str, Any]) -> Any:
        """
        Obtém o valor de um campo nos dados, suportando acesso a campos aninhados.
        
        Args:
            campo: Nome do campo (pode usar notação com ponto para campos aninhados)
            dados: Dados disponíveis
            
        Returns:
            Valor do campo ou None se não encontrado
        """
        if not campo:
            return None
            
        # Suporte para campos aninhados (ex: "classificacao.categoria")
        partes = campo.split('.')
        valor_atual = dados
        
        try:
            for parte in partes:
                if isinstance(valor_atual, dict) and parte in valor_atual:
                    valor_atual = valor_atual[parte]
                else:
                    return None
            return valor_atual
        except Exception as e:
            logger.error(f"Erro ao obter valor do campo '{campo}': {str(e)}")
            return None
    
    def _comparar_valores(self, valor1: Any, valor2: Any) -> bool:
        """
        Compara dois valores para verificar correspondência.
        
        Args:
            valor1: Primeiro valor
            valor2: Segundo valor
            
        Returns:
            True se os valores corresponderem, False caso contrário
        """
        # Tentativa de correspondência exata
        if valor1 == valor2:
            return True
            
        # Correspondência de strings (ignorando case)
        if isinstance(valor1, str) and isinstance(valor2, str):
            return valor1.lower() == valor2.lower()
            
        # Correspondência numérica
        try:
            if isinstance(valor1, (int, float)) and isinstance(valor2, (int, float)):
                return float(valor1) == float(valor2)
            elif isinstance(valor1, (int, float)) and isinstance(valor2, str):
                return float(valor1) == float(valor2)
            elif isinstance(valor1, str) and isinstance(valor2, (int, float)):
                return float(valor1) == float(valor2)
        except (ValueError, TypeError):
            pass
            
        # Correspondência de listas
        if isinstance(valor1, list) and isinstance(valor2, list):
            return sorted(valor1) == sorted(valor2)
            
        return False