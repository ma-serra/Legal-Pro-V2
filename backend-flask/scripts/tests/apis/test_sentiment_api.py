#!/usr/bin/env python3
"""
Teste simples da API de análise de sentimento do AssemblyAI.
"""

import os
import json
import requests
from datetime import datetime

# URL base da API
BASE_URL = "https://api.assemblyai.com/v2"

# Obter chave da API
API_KEY = os.environ.get("ASSEMBLYAI_API_KEY") or "0b7ec13989ab444580f6dfa5c35292cc"

# Configurar cabeçalhos
HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

def transcrever_com_sentimento(audio_url):
    """
    Inicia uma transcrição com análise de sentimento.
    """
    print(f"Iniciando transcrição para: {audio_url}")
    
    # Dados para a requisição
    data = {
        "audio_url": audio_url,
        "sentiment_analysis": "true"
    }
    
    # Fazer requisição
    response = requests.post(
        f"{BASE_URL}/transcript",
        json=data,
        headers=HEADERS
    )
    
    # Verificar resposta
    if response.status_code == 200:
        result = response.json()
        print(f"Transcrição iniciada com ID: {result['id']}")
        return result["id"]
    else:
        print(f"Erro: {response.status_code} - {response.text}")
        return None

def obter_resultado(transcript_id):
    """
    Obtém o resultado de uma transcrição.
    """
    print(f"Verificando status para ID: {transcript_id}")
    
    response = requests.get(
        f"{BASE_URL}/transcript/{transcript_id}",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        result = response.json()
        status = result.get("status")
        print(f"Status atual: {status}")
        
        if status == "completed":
            return result
        else:
            return {"status": status}
    else:
        print(f"Erro: {response.status_code} - {response.text}")
        return None

def analisar_sentimento(results):
    """
    Analisa os resultados de sentimento de uma transcrição.
    """
    if not results or results.get("status") != "completed":
        print("Não há resultados completos para análise")
        return
    
    # Obter resultados de sentimento
    sentiment_results = results.get("sentiment_analysis_results", [])
    
    if not sentiment_results:
        print("Não há resultados de análise de sentimento")
        return
    
    # Contar ocorrências
    positivos = sum(1 for item in sentiment_results if item.get("sentiment") == "POSITIVE")
    negativos = sum(1 for item in sentiment_results if item.get("sentiment") == "NEGATIVE")
    neutros = sum(1 for item in sentiment_results if item.get("sentiment") == "NEUTRAL")
    total = len(sentiment_results)
    
    # Exibir resultados
    print("\n=== ANÁLISE DE SENTIMENTO ===\n")
    print(f"Total de segmentos analisados: {total}")
    print(f"Positivos: {positivos} ({positivos/total*100:.1f}%)")
    print(f"Negativos: {negativos} ({negativos/total*100:.1f}%)")
    print(f"Neutros: {neutros} ({neutros/total*100:.1f}%)")
    
    # Determinar predominante
    if positivos > negativos and positivos > neutros:
        print("\nSentimento predominante: POSITIVO")
    elif negativos > positivos and negativos > neutros:
        print("\nSentimento predominante: NEGATIVO")
    else:
        print("\nSentimento predominante: NEUTRO")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sentimento_resultado_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados completos salvos em: {filename}")

def main():
    # ID de áudio de exemplo do AssemblyAI
    audio_url = "https://storage.googleapis.com/aai-web-samples/5_common_sports_injuries.mp3"
    
    # Testar com ID existente (se você já tem um ID de transcrição)
    transcript_id = "09836fae-0097-478d-bc54-edf3d2a62a06"
    
    # Ou iniciar uma nova transcrição
    # transcript_id = transcrever_com_sentimento(audio_url)
    
    if transcript_id:
        resultados = obter_resultado(transcript_id)
        analisar_sentimento(resultados)

if __name__ == "__main__":
    main()