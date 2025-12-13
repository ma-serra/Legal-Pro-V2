"""
Script para testar a multi-integração de transcrição e análise de sentimento com diferentes provedores.

Este script demonstra o uso dos diferentes provedores disponíveis para:
1. Transcrição de áudio (AssemblyAI e OpenAI Whisper)
2. Análise de sentimento (AssemblyAI, OpenAI GPT, Google Natural Language)

Usage:
    python test_multiprovider_transcricao.py --audio-path [caminho] --transcricao [provedor] --sentimento [provedor]
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from multiagent.agentes.transcricao import AgenteTranscricao

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def salvar_resultado(resultado: Dict[str, Any], provedor_transcricao: str, provedor_sentimento: str, pasta: str = ".") -> str:
    """Salva o resultado em um arquivo JSON."""
    # Criar nome de arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{pasta}/transcricao_{provedor_transcricao}_{provedor_sentimento}_{timestamp}.json"
    
    # Salvar resultado
    with open(nome_arquivo, "w", encoding="utf-8") as file:
        json.dump(resultado, file, ensure_ascii=False, indent=2)
        
    return nome_arquivo

def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Testa a transcrição e análise de sentimento com múltiplos provedores.")
    parser.add_argument("--audio-path", type=str, required=True, help="Caminho para o arquivo de áudio")
    parser.add_argument("--transcricao", type=str, choices=["assemblyai", "openai"], default="assemblyai", 
                      help="Provedor para transcrição (padrão: assemblyai)")
    parser.add_argument("--sentimento", type=str, choices=["auto", "assemblyai", "openai", "google"], default="auto",
                      help="Provedor para análise de sentimento (padrão: auto)")
    parser.add_argument("--idioma", type=str, default="pt", help="Código do idioma (padrão: pt)")
    parser.add_argument("--modelo-sentimento", type=str, default="gpt-4o", 
                      help="Modelo para análise de sentimento OpenAI (padrão: gpt-4o)")
    parser.add_argument("--sdk", action="store_true", help="Usar SDK AssemblyAI em vez de API REST")
    args = parser.parse_args()

    # Verificar se o arquivo de áudio existe
    if not os.path.exists(args.audio_path):
        logger.error(f"Arquivo de áudio não encontrado: {args.audio_path}")
        sys.exit(1)
        
    # Obter chaves das variáveis de ambiente
    assemblyai_key = os.environ.get("ASSEMBLYAI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")
    
    # Inicializar agente de transcrição com todos os provedores disponíveis
    try:
        agente = AgenteTranscricao(
            assemblyai_key=assemblyai_key,
            openai_key=openai_key,
            google_key=google_key,
            use_sdk=args.sdk,
            provedor_transcricao=args.transcricao,
            provedor_sentimento_padrao=args.sentimento,
            modelo_sentimento_openai=args.modelo_sentimento
        )
    except Exception as e:
        logger.error(f"Erro ao inicializar agente: {e}")
        sys.exit(1)
        
    # Exibir provedores disponíveis
    logger.info(f"Provedores de transcrição disponíveis: {', '.join(agente.provedores_disponiveis['transcricao'])}")
    logger.info(f"Provedores de sentimento disponíveis: {', '.join(agente.provedores_disponiveis['sentimento'])}")
    
    # Verificar se o provedor de transcrição solicitado está disponível
    if args.transcricao not in agente.provedores_disponiveis["transcricao"]:
        logger.error(f"Provedor de transcrição '{args.transcricao}' não está disponível!")
        logger.error(f"Provedores disponíveis: {', '.join(agente.provedores_disponiveis['transcricao'])}")
        sys.exit(1)
        
    # Processar o arquivo de áudio com os parâmetros escolhidos
    logger.info(f"Processando arquivo: {args.audio_path}")
    logger.info(f"Provedor de transcrição: {args.transcricao}")
    logger.info(f"Provedor de sentimento: {args.sentimento}")
    logger.info(f"Idioma: {args.idioma}")
    
    resultado = agente.processar(
        audio_path=args.audio_path,
        parametros={
            "idioma": args.idioma,
            "provedor_transcricao": args.transcricao,
            "provedor_sentimento": args.sentimento,
            "modelo_sentimento": args.modelo_sentimento,
            "sentimento": True,  # Sempre solicitar análise de sentimento
            "resumo": True,  # Tentar obter resumo (só funciona para inglês)
            "falantes": True,  # Tentar identificar falantes
            "forçar_sdk": args.sdk if args.transcricao == "assemblyai" else None
        }
    )
    
    # Verificar se a transcrição foi bem-sucedida
    if resultado.get("sucesso", False):
        logger.info("Transcrição bem-sucedida!")
        
        # Exibir resumo do resultado
        logger.info(f"Texto transcrito ({len(resultado.get('texto', ''))} caracteres)")
        logger.info(f"Provedor de transcrição: {resultado.get('provedor', 'desconhecido')}")
        
        # Verificar se há análise de sentimento
        if "sentimento" in resultado:
            logger.info(f"Análise de sentimento realizada com provedor: {resultado.get('provedor_sentimento', 'desconhecido')}")
            sentimento = resultado.get("sentimento", {})
            predominante = sentimento.get("predominante", "N/A")
            pontuacao = sentimento.get("pontuacao", 0)
            
            logger.info(f"Sentimento predominante: {predominante} (pontuação: {pontuacao:.2f})")
            
            # Exibir distribuição
            distribuicao = sentimento.get("distribuicao", {})
            if distribuicao:
                positivo = distribuicao.get("positivo", 0) * 100
                negativo = distribuicao.get("negativo", 0) * 100
                neutro = distribuicao.get("neutro", 0) * 100
                
                logger.info(f"Distribuição: {positivo:.1f}% positivo, {negativo:.1f}% negativo, {neutro:.1f}% neutro")
        else:
            logger.warning("Análise de sentimento não foi realizada")
            
        # Salvar resultado em arquivo
        nome_arquivo = salvar_resultado(
            resultado=resultado,
            provedor_transcricao=args.transcricao,
            provedor_sentimento=args.sentimento
        )
        logger.info(f"Resultado salvo em: {nome_arquivo}")
        
    else:
        logger.error(f"Erro na transcrição: {resultado.get('erro', 'Erro desconhecido')}")
        logger.error(f"Detalhes: {resultado.get('detalhes', '')}")
        
if __name__ == "__main__":
    main()