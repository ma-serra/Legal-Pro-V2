#!/usr/bin/env python3
"""
Teste para validar se o modelo selecionado está sendo usado corretamente nos assistentes
"""

import requests
import json
import time

def testar_modelos():
    """Testa diferentes modelos e provedores"""
    
    base_url = "http://localhost:5000"
    
    # Testes com diferentes modelos
    testes = [
        {
            "nome": "OpenAI GPT-4.1",
            "modelo": "gpt-4.1",
            "api": "openai",
            "pergunta": "Qual é a prescrição para ação de cobrança?"
        },
        {
            "nome": "Anthropic Claude Sonnet 4",
            "modelo": "claude-sonnet-4", 
            "api": "anthropic",
            "pergunta": "Como calcular indenização por danos morais?"
        },
        {
            "nome": "Google Gemini 2.5 Pro",
            "modelo": "gemini-2.5-pro",
            "api": "google", 
            "pergunta": "Quais são os requisitos para usucapião?"
        },
        {
            "nome": "DeepSeek Reasoner",
            "modelo": "deepseek-reasoner",
            "api": "deepseek",
            "pergunta": "Como funciona a sucessão testamentária?"
        }
    ]
    
    print("🧪 Testando se modelos selecionados são utilizados corretamente...\n")
    
    for teste in testes:
        print(f"🔍 Testando: {teste['nome']}")
        print(f"   Modelo: {teste['modelo']}")
        print(f"   API: {teste['api']}")
        print(f"   Pergunta: {teste['pergunta']}")
        
        try:
            # Teste via endpoint direto
            response = requests.post(
                f"{base_url}/assistentes/area/direito_civil/chat",
                headers={"Content-Type": "application/json"},
                json={
                    "pergunta": teste["pergunta"],
                    "modelo": teste["modelo"],
                    "api": teste["api"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("resposta"):
                    print(f"✅ Sucesso! Resposta recebida ({len(data['resposta'])} caracteres)")
                    # Verificar se há indicação do modelo usado na resposta
                    if teste["modelo"].lower() in str(data).lower():
                        print(f"   ✨ Modelo {teste['modelo']} confirmado na resposta")
                    else:
                        print(f"   ⚠️ Modelo {teste['modelo']} não encontrado na resposta")
                else:
                    print(f"❌ Erro: Resposta vazia")
                    print(f"   Response: {data}")
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout - Modelo {teste['modelo']} pode estar demorando")
        except Exception as e:
            print(f"❌ Erro: {e}")
            
        print("-" * 50)
        time.sleep(2)  # Pausa entre testes
    
    print("\n📊 Teste concluído!")

if __name__ == "__main__":
    testar_modelos()