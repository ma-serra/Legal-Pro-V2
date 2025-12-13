"""
Gerenciador Central dos Assistentes Jurídicos - Versão Corrigida
Coordena todos os assistentes com configuração robusta
"""

import os
import logging
from typing import Dict, List, Optional, Any
from flask import Flask

# Configurações das áreas jurídicas
AREAS_JURIDICAS = {
    'direito_penal': 'Direito Penal',
    'direito_civil': 'Direito Civil', 
    'direito_agrario': 'Direito Agrário',
    'direito_ambiental': 'Direito Ambiental',
    'direito_tributario': 'Direito Tributário',
    'direito_constitucional': 'Direito Constitucional',
    'direito_administrativo': 'Direito Administrativo',
    'direito_familia': 'Direito de Família',
    'direito_sucessorio': 'Direito Sucessório',
    'direito_empresarial': 'Direito Empresarial',
    'direito_trabalhista': 'Direito Trabalhista',
    'direito_previdenciario': 'Direito Previdenciário',
    'direito_consumidor': 'Direito do Consumidor',
    'direito_imobiliario': 'Direito Imobiliário',
    'direito_digital': 'Direito Digital',
    'seguros': 'Seguros',
    'conflitos_mediacao': 'Conflitos e Mediação',
    'analise_riscos': 'Análise de Riscos'
}

ESTILOS_ASSISTENTE = {
    'formal': 'Linguagem jurídica formal e técnica',
    'acessivel': 'Linguagem clara e acessível',
    'conciso': 'Resposta direta e objetiva'
}

logger = logging.getLogger(__name__)

class GerenciadorAssistentesJuridicos:
    """Gerenciador central para todos os assistentes jurídicos"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.assistentes = {}
        self.areas_disponiveis = AREAS_JURIDICAS
        self.estilos = ESTILOS_ASSISTENTE
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Inicializa com contexto da aplicação Flask - lazy loading ativado"""
        self.app = app
        logger.info("✅ Gerenciador de Assistentes Jurídicos configurado com lazy loading")
        logger.info(f"   • {len(AREAS_JURIDICAS)} áreas disponíveis para carregamento sob demanda")
    
    def _carregar_assistente(self, area_key: str):
        """Carrega um assistente específico sob demanda (lazy loading)"""
        if area_key not in self.assistentes:
            try:
                from .assistente_base import AssistenteJuridicoBase
                
                area_nome = AREAS_JURIDICAS.get(area_key, area_key)
                logger.info(f"🔄 Carregando assistente {area_nome} sob demanda...")
                
                assistente = AssistenteJuridicoBase(area_key)
                self.assistentes[area_key] = assistente
                logger.info(f"✅ Assistente {area_nome} carregado com sucesso")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar assistente {area_key}: {e}")
                return None
        
        return self.assistentes.get(area_key)
    
    def obter_assistente(self, area: str) -> Optional[Any]:
        """Obtém assistente específico por área com lazy loading"""
        if area not in AREAS_JURIDICAS:
            logger.warning(f"⚠️ Área jurídica '{area}' não reconhecida")
            return None
        
        return self._carregar_assistente(area)
    
    def listar_areas_disponiveis(self) -> Dict:
        """Lista todas as áreas jurídicas disponíveis"""
        return {
            "areas": AREAS_JURIDICAS,
            "total": len(AREAS_JURIDICAS),
            "assistentes_ativos": len(self.assistentes)
        }
    
    def processar_consulta(self, area: str, pergunta: str, **kwargs) -> Dict:
        """Processa consulta em área específica"""
        try:
            assistente = self.obter_assistente(area)
            if not assistente:
                # Tenta criar assistente se não existe
                try:
                    from .assistente_base import AssistenteJuridicoBase
                    assistente = AssistenteJuridicoBase(area)
                    self.assistentes[area] = assistente
                    logger.info(f"✅ Assistente {area} criado dinamicamente")
                except Exception as e:
                    return self._tratar_erro_assistente(area, Exception(f"Assistente não encontrado: {e}"))
            
            resultado = assistente.processar_consulta_completa(
                pergunta=pergunta,
                contexto=kwargs.get('contexto', ''),
                modelo=kwargs.get('modelo', 'openai'),
                personalidade=kwargs.get('personalidade', 'advogado'),
                tom=kwargs.get('tom', 'sistematico'),
                temperatura=kwargs.get('temperatura', 0.3),
                max_tokens=kwargs.get('max_tokens', 2000),
                documento_anexado=kwargs.get('documento_anexado')  # ADICIONAR DOCUMENTO ANEXADO
            )
            
            return resultado
            
        except Exception as e:
            return self._tratar_erro_assistente(area, e)
    
    def obter_estatisticas_sistema(self) -> Dict:
        """Obtém estatísticas do sistema de assistentes"""
        try:
            stats = {
                "total_areas": len(AREAS_JURIDICAS),
                "assistentes_carregados": len(self.assistentes),
                "areas_ativas": list(self.assistentes.keys()),
                "status": "operacional" if self.assistentes else "erro"
            }
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"status": "erro", "erro": str(e)}
    
    def obter_areas_disponiveis(self) -> Dict:
        """Obtém informações detalhadas das áreas jurídicas"""
        areas_info = {}
        
        for area_key, area_nome in AREAS_JURIDICAS.items():
            assistente = self.assistentes.get(area_key)
            areas_info[area_key] = {
                "nome": area_nome,
                "ativo": assistente is not None,
                "tabela_embeddings": f"embeddings_{area_key}",
                "capacidades": [
                    "Consulta de documentos",
                    "Análise jurídica especializada", 
                    "Busca por similaridade",
                    "Fundamentação legal"
                ]
            }
        
        return areas_info
    
    def _tratar_erro_assistente(self, area: str, erro: Exception) -> dict:
        """Trata erros de assistentes de forma padronizada"""
        logger.error(f"Erro no assistente {area}: {erro}")
        return {
            "resposta": "Sistema temporariamente indisponível. Reformular consulta ou reprocessar solicitação.",
            "area": area,
            "status": "erro",
            "erro_tipo": type(erro).__name__
        }

# Instância global do gerenciador
gerenciador_assistentes = GerenciadorAssistentesJuridicos()
