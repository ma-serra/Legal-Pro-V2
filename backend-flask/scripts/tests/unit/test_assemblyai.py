#!/usr/bin/env python3
"""
Script para testar a integração com AssemblyAI.

Este script testa:
1. Transcrição de áudio com resumo
2. Análise de sentimento (se ativada)
3. Obtenção de status e resultados
"""

import os
import argparse
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar a classe cliente
try:
    from multiagent.integrations.assemblyai.client import AssemblyAIClient
    IMPORT_SUCCESS = True
except ImportError:
    logger.error("Não foi possível importar o módulo AssemblyAIClient")
    IMPORT_SUCCESS = False

def testar_transcricao_basica(arquivo_audio, idioma="en"):
    """
    Testa a transcrição básica de um arquivo de áudio.
    
    Args:
        arquivo_audio: Caminho para o arquivo de áudio
        idioma: Código do idioma
    """
    if not IMPORT_SUCCESS:
        logger.error("Teste não pode ser executado: módulo não importado")
        return
        
    logger.info(f"Iniciando teste de transcrição básica para: {arquivo_audio}")
    
    # Criar cliente
    cliente = AssemblyAIClient()
    
    # Transcrever o arquivo
    try:
        # Usar o método completo
        resultado = cliente.transcribe_file(
            file_path=arquivo_audio,
            language_code=idioma,
            summarization=False,
            sentiment_analysis=False,
            wait_for_completion=True,
            max_wait_time=120
        )
        
        # Verificar resultado
        if resultado.get("status") == "completed":
            logger.info("Transcrição concluída com sucesso!")
            logger.info(f"Texto: {resultado.get('text')[:150]}...")
            logger.info(f"Duração: {resultado.get('audio_duration')} segundos")
            logger.info(f"Confiança: {resultado.get('confidence')}")
            
            return True, resultado
        else:
            logger.warning(f"Transcrição não concluída: {resultado.get('status')}")
            return False, resultado
            
    except Exception as e:
        logger.error(f"Erro durante transcrição: {str(e)}")
        return False, {"erro": str(e)}

def testar_transcricao_completa(arquivo_audio, idioma="en"):
    """
    Testa a transcrição completa com resumo e análise de sentimento.
    
    Args:
        arquivo_audio: Caminho para o arquivo de áudio
        idioma: Código do idioma
    """
    if not IMPORT_SUCCESS:
        logger.error("Teste não pode ser executado: módulo não importado")
        return
        
    logger.info(f"Iniciando teste de transcrição completa para: {arquivo_audio}")
    
    # Criar cliente
    cliente = AssemblyAIClient()
    
    # Transcrever o arquivo
    try:
        # Usar o método completo
        resultado = cliente.transcribe_file(
            file_path=arquivo_audio,
            language_code=idioma,
            summarization=True,
            summary_type="bullets",
            summary_model="informative",
            sentiment_analysis=True,
            wait_for_completion=True,
            max_wait_time=180
        )
        
        # Verificar resultado
        if resultado.get("status") == "completed":
            logger.info("Transcrição completa concluída com sucesso!")
            
            # Mostrar texto
            logger.info(f"Texto: {resultado.get('text')[:150]}...")
            
            # Mostrar resumo
            if "summary" in resultado:
                logger.info(f"Resumo: {resultado.get('summary')}")
                
            # Mostrar tópicos
            if "summary_bullets" in resultado:
                logger.info("Tópicos principais:")
                for idx, bullet in enumerate(resultado.get("summary_bullets", []), 1):
                    logger.info(f"  {idx}. {bullet}")
                    
            # Mostrar análise de sentimento
            if "sentiment_analysis_results" in resultado:
                sentiment_results = resultado.get("sentiment_analysis_results", [])
                
                if sentiment_results:
                    # Contar ocorrências
                    positive = sum(1 for item in sentiment_results if item.get("sentiment") == "POSITIVE")
                    negative = sum(1 for item in sentiment_results if item.get("sentiment") == "NEGATIVE")
                    neutral = sum(1 for item in sentiment_results if item.get("sentiment") == "NEUTRAL")
                    total = len(sentiment_results)
                    
                    # Mostrar distribuição
                    logger.info("Análise de sentimento:")
                    logger.info(f"  Positivo: {positive} ({positive/total*100:.1f}%)")
                    logger.info(f"  Negativo: {negative} ({negative/total*100:.1f}%)")
                    logger.info(f"  Neutro: {neutral} ({neutral/total*100:.1f}%)")
                    
                    # Determinar predominante
                    if positive > negative and positive > neutral:
                        predominante = "POSITIVO"
                    elif negative > positive and negative > neutral:
                        predominante = "NEGATIVO"
                    else:
                        predominante = "NEUTRO"
                        
                    logger.info(f"  Sentimento predominante: {predominante}")
                    
            return True, resultado
        else:
            logger.warning(f"Transcrição não concluída: {resultado.get('status')}")
            return False, resultado
            
    except Exception as e:
        logger.error(f"Erro durante transcrição: {str(e)}")
        return False, {"erro": str(e)}

def main():
    """
    Função principal para executar testes.
    """
    parser = argparse.ArgumentParser(description='Teste de integração com AssemblyAI')
    parser.add_argument('arquivo', help='Caminho para o arquivo de áudio')
    parser.add_argument('--idioma', default='en', help='Código do idioma (pt, en, es, etc.)')
    parser.add_argument('--basico', action='store_true', help='Executar apenas o teste básico')
    parser.add_argument('--completo', action='store_true', help='Executar apenas o teste completo')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.arquivo):
        logger.error(f"Arquivo não encontrado: {args.arquivo}")
        return
    
    # Executar teste básico
    if args.basico or not (args.basico or args.completo):
        sucesso, _ = testar_transcricao_basica(args.arquivo, args.idioma)
        if not sucesso:
            logger.warning("Teste básico de transcrição falhou")
            
    # Executar teste completo
    if args.completo or not (args.basico or args.completo):
        sucesso, _ = testar_transcricao_completa(args.arquivo, args.idioma)
        if not sucesso:
            logger.warning("Teste completo de transcrição falhou")

if __name__ == "__main__":
    main()