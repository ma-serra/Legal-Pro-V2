#!/usr/bin/env python3
"""
Script para testar todas as APIs do sistema e verificar se estão funcionais
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# Configuração base
BASE_URL = "http://localhost:5000"
API_ENDPOINTS = {
    "health_validacao": "/api/validacao-multi-agente/health",
    "salvar_analise": "/api/validacao-multi-agente/salvar",
    "listar_analises": "/api/validacao-multi-agente/listar",
    "buscar_analise": "/api/validacao-multi-agente/buscar",
    "marcar_exportacao": "/api/validacao-multi-agente/marcar-exportacao",
    "estatisticas": "/api/validacao-multi-agente/estatisticas",
    "chat_juridico": "/api/chat/juridico",
    "analise_robusta": "/api/analise-robusta",
    "ml_endpoints": "/api/ml/health",
    "video_export": "/api/video/export",
    "icon_library": "/api/icons/list"
}

def test_api_endpoint(endpoint_name, url, method="GET", data=None, headers=None):
    """
    Testa um endpoint específico da API
    """
    try:
        full_url = f"{BASE_URL}{url}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        print(f"🔍 Testando {endpoint_name}: {method} {url}")
        
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(full_url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(full_url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(full_url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(full_url, headers=headers, timeout=10)
        else:
            return {
                "success": False,
                "error": f"Método HTTP {method} não suportado",
                "status_code": None,
                "response_time": None
            }
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        # Tentar parsing JSON
        try:
            response_data = response.json()
        except:
            response_data = {"raw_response": response.text}
        
        result = {
            "success": response.status_code in [200, 201, 202],
            "status_code": response.status_code,
            "response_time": response_time,
            "data": response_data,
            "error": None if response.status_code in [200, 201, 202] else f"HTTP {response.status_code}"
        }
        
        if result["success"]:
            print(f"✅ {endpoint_name}: OK ({response_time}ms)")
        else:
            print(f"❌ {endpoint_name}: FALHA - {result['error']} ({response_time}ms)")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint_name}: CONEXÃO FALHOU - Servidor não está rodando")
        return {
            "success": False,
            "error": "Servidor não está rodando",
            "status_code": None,
            "response_time": None
        }
    except requests.exceptions.Timeout:
        print(f"❌ {endpoint_name}: TIMEOUT - Resposta demorou mais de 10 segundos")
        return {
            "success": False,
            "error": "Timeout",
            "status_code": None,
            "response_time": None
        }
    except Exception as e:
        print(f"❌ {endpoint_name}: ERRO - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "status_code": None,
            "response_time": None
        }

def test_validacao_multi_agente_flow():
    """
    Testa o fluxo completo da API de validação multi-agente
    """
    print("\n🧪 TESTANDO FLUXO COMPLETO DE VALIDAÇÃO MULTI-AGENTE")
    print("=" * 60)
    
    # 1. Health check
    health_result = test_api_endpoint("Health Check", API_ENDPOINTS["health_validacao"])
    if not health_result["success"]:
        print("❌ Health check falhou - abortando testes")
        return False
    
    # 2. Criar uma análise de teste (simulando dados reais)
    analise_test_data = {
        "titulo_analise": "Teste Análise Multi-Agente",
        "descricao": "Análise de teste automática",
        "documento_original": "CONTRATO DE PRESTAÇÃO DE SERVIÇOS\n\nContratante: Empresa XYZ Ltda\nContratado: Prestador ABC\n\nObjeto: Prestação de serviços de marketing digital incluindo desenvolvimento de website, criação de conteúdo e gestão de redes sociais.\n\nValor: R$ 5.000,00 mensais\nPrazo: 12 meses\n\nCláusula 4.1: A CONTRATADA poderá utilizar a marca da CONTRATANTE em seu portfólio de clientes.",
        "documento_nome": "contrato_teste.txt",
        "documento_tipo": "text/plain",
        "total_agentes_utilizados": 3,
        "areas_juridicas_envolvidas": ["Direito Empresarial", "Propriedade Intelectual"],
        "resultados_agentes": [
            {
                "agente_id": "21",
                "agente_nome": "Consultor em Propriedade Intelectual",
                "categoria": "Direito Empresarial",
                "modelo_usado": "OpenAI GPT-4o",
                "resultado": "Análise da cláusula de uso da marca identificou riscos de propriedade intelectual...",
                "pontos_criticos": ["Uso ilimitado da marca", "Ausência de limitação temporal"],
                "recomendacoes": ["Estabelecer limitação temporal", "Definir condições de uso"]
            },
            {
                "agente_id": "22",
                "agente_nome": "Especialista em Antitruste",
                "categoria": "Direito Empresarial", 
                "modelo_usado": "Anthropic Claude-3.5-Sonnet",
                "resultado": "Análise de aspectos concorrenciais do contrato...",
                "pontos_criticos": ["Cláusulas restritivas"],
                "recomendacoes": ["Revisar exclusividade"]
            },
            {
                "agente_id": "23",
                "agente_nome": "Especialista em Capital de Risco",
                "categoria": "Direito Empresarial",
                "modelo_usado": "Google Gemini-2.5-Flash", 
                "resultado": "Análise financeira e de investimento...",
                "pontos_criticos": ["Riscos de investimento"],
                "recomendacoes": ["Incluir garantias"]
            }
        ],
        "recomendacoes_prioritarias": [
            "Revisar cláusula 4.1 sobre uso da marca",
            "Definir propriedade dos materiais criativos",
            "Incluir garantias bancárias"
        ],
        "recomendacoes_importantes": [
            "Estabelecer marcos objetivos",
            "Incluir cláusulas de direitos autorais",
            "Definir procedimentos de remoção da marca",
            "Vincular pagamentos a entregas"
        ],
        "recomendacoes_sugeridas": [
            "Criar conta escrow",
            "Incluir seguro de execução",
            "Vedar uso para outros clientes",
            "Adequar às normas de PI"
        ],
        "tempo_processamento_segundos": 12.5,
        "modelos_ia_utilizados": ["OpenAI GPT-4o", "Anthropic Claude-3.5-Sonnet", "Google Gemini-2.5-Flash"],
        "tokens_consumidos": 2450,
        "custo_estimado": 0.15,
        "status": "concluida",
        "fallback_mode": False,
        "debug_mode": True
    }
    
    # NOTA: Este teste requer autenticação, então pode falhar com 401/403
    print("\n2️⃣ Testando salvamento de análise (pode falhar por falta de autenticação)...")
    save_result = test_api_endpoint(
        "Salvar Análise", 
        API_ENDPOINTS["salvar_analise"], 
        method="POST", 
        data=analise_test_data
    )
    
    # 3. Listar análises
    print("\n3️⃣ Testando listagem de análises...")
    list_result = test_api_endpoint("Listar Análises", API_ENDPOINTS["listar_analises"])
    
    # 4. Buscar análise por ID (se salvamento funcionou)
    numero_registro = None
    if save_result["success"] and isinstance(save_result.get("data"), dict):
        if "data" in save_result["data"] and isinstance(save_result["data"]["data"], dict):
            numero_registro = save_result["data"]["data"].get("numero_registro")
        elif "numero_registro" in save_result["data"]:
            numero_registro = save_result["data"]["numero_registro"]
    
    if numero_registro:
        print(f"\n4️⃣ Testando busca por número de registro: {numero_registro}")
        search_result = test_api_endpoint(
            "Buscar Análise", 
            f"{API_ENDPOINTS['buscar_analise']}/{numero_registro}"
        )
    else:
        print("\n4️⃣ Pulando teste de busca (número de registro não encontrado)")
        print(f"   Resposta do salvamento: {save_result.get('data', 'N/A')}")
    
    # 5. Estatísticas
    print("\n5️⃣ Testando estatísticas...")
    stats_result = test_api_endpoint("Estatísticas", API_ENDPOINTS["estatisticas"])
    
    return True

def test_other_apis():
    """
    Testa outras APIs do sistema
    """
    print("\n🔧 TESTANDO OUTRAS APIs DO SISTEMA")
    print("=" * 40)
    
    # Chat Jurídico (pode falhar por autenticação)
    test_api_endpoint("Chat Jurídico", API_ENDPOINTS["chat_juridico"], method="POST", data={
        "pergunta": "Qual é a diferença entre dolo e culpa?",
        "area_juridica": "Direito Penal"
    })
    
    # Análise Robusta (pode falhar por autenticação)
    test_api_endpoint("Análise Robusta", API_ENDPOINTS["analise_robusta"], method="POST", data={
        "texto_documento": "Contrato de teste para análise",
        "agentes_selecionados": ["1", "2", "3"]
    })
    
    # ML Health (pode não existir)
    test_api_endpoint("ML Health", API_ENDPOINTS["ml_endpoints"])
    
    # Icon Library
    test_api_endpoint("Icon Library", API_ENDPOINTS["icon_library"])

def check_server_status():
    """
    Verifica se o servidor está rodando
    """
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """
    Função principal do teste
    """
    print("🚀 TESTE COMPLETO DAS APIs DO SISTEMA LEGAL DESIGN PRO V2")
    print("=" * 70)
    print(f"🔗 Base URL: {BASE_URL}")
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar se o servidor está rodando
    print("🔍 Verificando status do servidor...")
    if not check_server_status():
        print("❌ SERVIDOR NÃO ESTÁ RODANDO!")
        print("   Execute o servidor antes de rodar os testes:")
        print("   python main.py")
        return False
    
    print("✅ Servidor está rodando")
    
    # Executar testes
    try:
        # Teste principal: API de Validação Multi-Agente
        test_validacao_multi_agente_flow()
        
        # Testes secundários: Outras APIs
        test_other_apis()
        
        print("\n" + "=" * 70)
        print("✅ TESTE COMPLETO FINALIZADO")
        print("📝 Verifique os resultados acima para identificar problemas")
        print("🔧 APIs que falharam podem precisar de autenticação ou configuração")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)