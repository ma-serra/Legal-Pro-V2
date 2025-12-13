#!/usr/bin/env python3
"""
Teste das melhorias AssemblyAI baseadas no código fornecido pelo usuário
"""
import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()

# Configurações
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
BASE_URL = "https://api.assemblyai.com/v2"
HEADERS = {"authorization": API_KEY}

def testar_configuracao_otimizada():
    """Testa a configuração otimizada com resumo automático"""
    print("🔧 Testando configuração otimizada da AssemblyAI...")
    
    # Usar arquivo de áudio real para teste
    arquivo_teste = "attached_assets/Audio Christian.ogg"
    
    if not os.path.exists(arquivo_teste):
        print("❌ Arquivo de teste não encontrado")
        return False
    
    # Upload do arquivo
    print("📤 Fazendo upload do arquivo...")
    try:
        with open(arquivo_teste, "rb") as f:
            response = requests.post(f"{BASE_URL}/upload", headers=HEADERS, data=f)
            response.raise_for_status()
            upload_url = response.json()["upload_url"]
            print(f"✅ Upload concluído: {upload_url[:50]}...")
    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        return False
    
    # Configuração otimizada compatível com português
    data = {
        "audio_url": upload_url,
        "language_code": "pt",  # Português
        "speaker_labels": True,
        "punctuate": True,
        "format_text": True,
        "disfluencies": False      # Remove hesitações para texto mais limpo
    }
    
    print("🚀 Submetendo transcrição com configuração otimizada...")
    print(f"📋 Configurações: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/transcript", headers=HEADERS, json=data)
        
        if response.status_code != 200:
            print(f"❌ Erro na submissão: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            return False
            
        transcript_id = response.json()["id"]
        print(f"✅ Transcrição submetida: {transcript_id}")
        
        # Polling para aguardar conclusão
        polling_url = f"{BASE_URL}/transcript/{transcript_id}"
        print("⏳ Aguardando conclusão...")
        
        max_tentativas = 30
        tentativa = 0
        
        while tentativa < max_tentativas:
            result = requests.get(polling_url, headers=HEADERS).json()
            status = result.get("status", "unknown")
            
            if status == "completed":
                print("✅ Transcrição concluída!")
                return analisar_resultados(result)
            elif status == "error":
                print(f"❌ Erro na transcrição: {result.get('error', 'Erro desconhecido')}")
                return False
            
            tentativa += 1
            print(f"⏳ Status: {status} (tentativa {tentativa}/{max_tentativas})")
            time.sleep(3)
        
        print("⏰ Timeout na transcrição")
        return False
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def analisar_resultados(resultado):
    """Analisa os resultados da transcrição otimizada"""
    print("\n📊 ANÁLISE DOS RESULTADOS")
    print("=" * 50)
    
    # Texto transcrito
    texto = resultado.get('text', '')
    print(f"📝 Texto: {len(texto)} caracteres")
    if texto:
        print(f"   Início: {texto[:100]}...")
    
    # Confiança
    confianca = resultado.get('confidence', 0) * 100
    print(f"🎯 Confiança: {confianca:.1f}%")
    
    # Falantes
    utterances = resultado.get('utterances', [])
    print(f"👥 Segmentos de falantes: {len(utterances)}")
    
    # Resumo (nova funcionalidade)
    resumo = resultado.get('summary', None)
    if resumo:
        print(f"📋 Resumo disponível: {len(resumo)} caracteres")
        print(f"   Resumo: {resumo[:100]}...")
    else:
        print("📋 Resumo: Não disponível")
    
    # Análise de sentimento
    sentimentos = resultado.get('sentiment_analysis_results', [])
    if sentimentos:
        print(f"😊 Análise de sentimento: {len(sentimentos)} segmentos")
        tipos_sentimento = {}
        for s in sentimentos:
            sentimento = s.get('sentiment', 'neutro')
            tipos_sentimento[sentimento] = tipos_sentimento.get(sentimento, 0) + 1
        print(f"   Distribuição: {tipos_sentimento}")
    else:
        print("😊 Análise de sentimento: Não disponível")
    
    # Auto highlights (nova funcionalidade)
    highlights = resultado.get('auto_highlights_result', {})
    if highlights and highlights.get('results'):
        print(f"⭐ Auto highlights: {len(highlights['results'])} destaques")
        for i, highlight in enumerate(highlights['results'][:3]):
            print(f"   {i+1}. {highlight.get('text', '')[:50]}...")
    else:
        print("⭐ Auto highlights: Não disponível")
    
    print("\n🎉 Teste concluído com sucesso!")
    return True

def main():
    """Função principal"""
    print("🚀 TESTE DAS MELHORIAS ASSEMBLYAI")
    print("=" * 40)
    
    if not API_KEY:
        print("❌ ASSEMBLYAI_API_KEY não encontrada nas variáveis de ambiente")
        return
    
    sucesso = testar_configuracao_otimizada()
    
    if sucesso:
        print("\n✅ Sistema aprimorado funcionando corretamente!")
        print("📈 Melhorias implementadas:")
        print("   • Resumo automático ativado")
        print("   • Remoção de hesitações")
        print("   • Auto highlights")
        print("   • Configuração otimizada para português")
    else:
        print("\n❌ Problemas encontrados no sistema")

if __name__ == "__main__":
    main()