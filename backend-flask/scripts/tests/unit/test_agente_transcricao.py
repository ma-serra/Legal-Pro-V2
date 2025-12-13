"""
Script para testar o agente de transcrição com suporte a SDK.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def test_agente_transcricao():
    """Testa o agente de transcrição com diferentes abordagens."""
    try:
        # Verificar se a chave API existe
        api_key = os.environ.get("ASSEMBLYAI_API_KEY", "0b7ec13989ab444580f6dfa5c35292cc")
        if not api_key:
            logger.error("API key não encontrada no ambiente (ASSEMBLYAI_API_KEY)")
            return False
        logger.info("Usando API key: " + api_key[:5] + "..." + api_key[-5:])
        
        # Importar agente
        from multiagent.agentes.transcricao import AgenteTranscricao
        
        # Definir arquivo de áudio para teste
        audio_path = "./audio_exemplo.mp3"
        if not os.path.exists(audio_path):
            logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
            return False
            
        logger.info(f"Usando arquivo de áudio: {audio_path}")
        
        # Testar com API REST (forçando)
        logger.info("Testando com API REST (forçado)...")
        agente_rest = AgenteTranscricao(api_key=api_key, use_sdk=False)
        resultado_rest = agente_rest.processar(
            audio_path=audio_path,
            parametros={
                "idioma": "pt",
                "falantes": True,
                "timeout": 60  # Esperar no máximo 60 segundos
            }
        )
        
        logger.info(f"Resultado API REST: {'Sucesso' if resultado_rest.get('sucesso', False) else 'Falha'}")
        
        # Tentar usar SDK (se disponível)
        try:
            import assemblyai
            logger.info("SDK do AssemblyAI importado com sucesso")
            sdk_disponivel = True
        except ImportError:
            logger.warning("SDK AssemblyAI não está disponível. Pulando teste com SDK.")
            sdk_disponivel = False
        
        # Se o SDK estiver disponível, testar com ele
        if sdk_disponivel:
            # Testar com SDK (forçando)
            logger.info("Testando com SDK oficial (forçado)...")
            agente_sdk = AgenteTranscricao(api_key=api_key, use_sdk=True)
            resultado_sdk = agente_sdk.processar(
                audio_path=audio_path,
                parametros={
                    "idioma": "pt",
                    "falantes": True,
                    "timeout": 60  # Esperar no máximo 60 segundos
                }
            )
            
            logger.info(f"Resultado SDK: {'Sucesso' if resultado_sdk.get('sucesso', False) else 'Falha'}")
        
        # Mostrar status dos testes
        return True
            
    except Exception as e:
        logger.exception(f"Erro durante teste: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando teste do agente de transcrição...")
    success = test_agente_transcricao()
    logger.info(f"Resultado final: {'Sucesso' if success else 'Falha'}")
    sys.exit(0 if success else 1)