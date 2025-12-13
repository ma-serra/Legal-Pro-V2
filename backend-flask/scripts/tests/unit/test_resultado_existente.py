#!/usr/bin/env python3
"""
Testa a obtenção de uma transcrição existente usando o ID.
"""

import os
import json
import logging
from multiagent.integrations.assemblyai.client import AssemblyAIClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ID da transcrição já concluída
TRANSCRIPT_ID = "09836fae-0097-478d-bc54-edf3d2a62a06"

def main():
    # Inicializar cliente
    cliente = AssemblyAIClient()
    
    try:
        # Obter resultado
        logger.info(f"Obtendo transcrição: {TRANSCRIPT_ID}")
        resultado = cliente.get_transcription(TRANSCRIPT_ID)
        
        # Verificar status
        if resultado.get("status") == "completed":
            # Verificar se tem análise de sentimento
            if "sentiment_analysis_results" in resultado:
                # Obter resultados de sentimento
                sentiment_results = resultado.get("sentiment_analysis_results", [])
                
                # Analisar métricas
                metricas = cliente.analyze_sentiment_metrics(sentiment_results)
                
                logger.info("Análise de sentimento:")
                logger.info(f"  Total de segmentos: {metricas['count']}")
                logger.info(f"  Distribuição:")
                logger.info(f"    Positivo: {metricas['distribution']['POSITIVE']}")
                logger.info(f"    Negativo: {metricas['distribution']['NEGATIVE']}")
                logger.info(f"    Neutro: {metricas['distribution']['NEUTRAL']}")
                logger.info(f"  Percentuais:")
                logger.info(f"    Positivo: {metricas['percentage']['POSITIVE']:.1f}%")
                logger.info(f"    Negativo: {metricas['percentage']['NEGATIVE']:.1f}%")
                logger.info(f"    Neutro: {metricas['percentage']['NEUTRAL']:.1f}%")
                logger.info(f"  Sentimento predominante: {metricas['predominant']}")
                
                # Converter para o nosso formato
                sentimento_traduzido = cliente.translate_sentiment(metricas['predominant'])
                logger.info(f"  Sentimento predominante (traduzido): {sentimento_traduzido}")
                
                # Salvar resultados formatados
                resultado_formatado = {
                    "texto": resultado.get("text"),
                    "idioma": resultado.get("language_code"),
                    "duracao_segundos": resultado.get("audio_duration"),
                    "confianca": resultado.get("confidence"),
                    "sentimento": {
                        "metricas": {
                            "total": metricas["count"],
                            "distribuicao": {
                                "positivo": metricas["distribution"]["POSITIVE"],
                                "negativo": metricas["distribution"]["NEGATIVE"],
                                "neutro": metricas["distribution"]["NEUTRAL"]
                            },
                            "percentual": {
                                "positivo": metricas["percentage"]["POSITIVE"],
                                "negativo": metricas["percentage"]["NEGATIVE"],
                                "neutro": metricas["percentage"]["NEUTRAL"]
                            },
                            "predominante": sentimento_traduzido
                        }
                    }
                }
                
                # Salvar em arquivo JSON
                with open("resultado_formatado.json", "w", encoding="utf-8") as f:
                    json.dump(resultado_formatado, f, indent=2, ensure_ascii=False)
                    
                logger.info("Resultado formatado salvo em: resultado_formatado.json")
            else:
                logger.warning("Esta transcrição não contém análise de sentimento")
        else:
            logger.warning(f"Transcrição não concluída. Status: {resultado.get('status')}")
            
    except Exception as e:
        logger.error(f"Erro: {str(e)}")

if __name__ == "__main__":
    main()