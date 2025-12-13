"""
Debug completo do sistema de assistentes para identificar erro de conexão
"""
import os
import sys
import logging
import traceback
import psycopg2
from typing import Dict, Any

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def testar_variaveis_ambiente():
    """Testa se todas as variáveis de ambiente necessárias estão disponíveis"""
    print("🔍 TESTANDO VARIÁVEIS DE AMBIENTE:")
    
    variaveis_criticas = [
        'DATABASE_URL',
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'GOOGLE_API_KEY',
        'QDRANT_URL',
        'QDRANT_API_KEY'
    ]
    
    for var in variaveis_criticas:
        valor = os.environ.get(var)
        if valor:
            print(f"  ✅ {var}: {'*' * min(10, len(valor))}...")
        else:
            print(f"  ❌ {var}: NÃO DEFINIDA")
    
    print()

def testar_conexao_database():
    """Testa conexão direta com PostgreSQL"""
    print("🔍 TESTANDO CONEXÃO DATABASE:")
    
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("  ❌ DATABASE_URL não definida")
            return False
            
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Testar query simples
        cursor.execute("SELECT version();")
        versao = cursor.fetchone()[0]
        print(f"  ✅ Conexão PostgreSQL: {versao[:50]}...")
        
        # Verificar tabelas críticas
        tabelas_criticas = ['documentos_juridicos', 'agente_juridico', 'usuarios']
        
        for tabela in tabelas_criticas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela};")
                count = cursor.fetchone()[0]
                print(f"  ✅ Tabela {tabela}: {count} registros")
            except Exception as e:
                print(f"  ❌ Tabela {tabela}: {e}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na conexão database: {e}")
        return False

def testar_importacoes_assistentes():
    """Testa importação dos módulos de assistentes"""
    print("🔍 TESTANDO IMPORTAÇÕES DOS ASSISTENTES:")
    
    try:
        # Tentar importar assistente base
        sys.path.append('modules/assistentes_juridicos')
        from assistente_base import AssistenteJuridicoBase
        print("  ✅ AssistenteJuridicoBase importado")
        
        # Tentar importar gerenciador central
        from gerenciador_central import GerenciadorAssistentesJuridicos
        print("  ✅ GerenciadorAssistentesJuridicos importado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nas importações: {e}")
        print(f"  📋 Traceback: {traceback.format_exc()}")
        return False

def testar_criacao_assistente():
    """Testa criação de um assistente específico"""
    print("🔍 TESTANDO CRIAÇÃO DE ASSISTENTE:")
    
    try:
        sys.path.append('modules/assistentes_juridicos')
        from assistente_base import AssistenteJuridicoBase
        
        # Tentar criar assistente de direito penal
        assistente = AssistenteJuridicoBase("direito_penal")
        print("  ✅ Assistente direito_penal criado")
        
        # Verificar APIs configuradas
        if hasattr(assistente, 'openai_client') and assistente.openai_client:
            print("  ✅ OpenAI Client configurado")
        else:
            print("  ❌ OpenAI Client não configurado")
            
        if hasattr(assistente, 'anthropic_client') and assistente.anthropic_client:
            print("  ✅ Anthropic Client configurado") 
        else:
            print("  ❌ Anthropic Client não configurado")
            
        return assistente
        
    except Exception as e:
        print(f"  ❌ Erro na criação do assistente: {e}")
        print(f"  📋 Traceback: {traceback.format_exc()}")
        return None

def testar_busca_documentos(assistente):
    """Testa busca de documentos do assistente"""
    print("🔍 TESTANDO BUSCA DE DOCUMENTOS:")
    
    try:
        if not assistente:
            print("  ❌ Assistente não disponível")
            return False
            
        # Testar busca simples
        resultados = assistente.buscar_documentos_relevantes("crime", limit=3)
        print(f"  ✅ Busca retornou {len(resultados)} documentos")
        
        if resultados:
            print("  📄 Exemplo de documento encontrado:")
            doc = resultados[0]
            conteudo = doc.get('conteudo', '')[:100]
            referencia = doc.get('referencia', 'N/A')
            print(f"      Ref: {referencia}")
            print(f"      Conteúdo: {conteudo}...")
        
        return len(resultados) > 0
        
    except Exception as e:
        print(f"  ❌ Erro na busca de documentos: {e}")
        print(f"  📋 Traceback: {traceback.format_exc()}")
        return False

def testar_processamento_ia(assistente):
    """Testa processamento com IA"""
    print("🔍 TESTANDO PROCESSAMENTO COM IA:")
    
    try:
        if not assistente:
            print("  ❌ Assistente não disponível")
            return False
            
        # Testar com documentos mockados
        docs_mock = [{
            'conteudo': 'Art. 121. Matar alguém: Pena - reclusão, de seis a vinte anos.',
            'referencia': 'Código Penal - Art. 121',
            'metadata': {}
        }]
        
        resposta = assistente.processar_com_ia("O que é homicídio?", docs_mock, "openai")
        
        if resposta and "Não foi possível" not in resposta:
            print("  ✅ Processamento com OpenAI funcionando")
            print(f"  📝 Resposta (primeiros 100 chars): {resposta[:100]}...")
            return True
        else:
            print("  ❌ Processamento com OpenAI falhou")
            print(f"  📝 Resposta: {resposta}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro no processamento com IA: {e}")
        print(f"  📋 Traceback: {traceback.format_exc()}")
        return False

def testar_consulta_completa(assistente):
    """Testa método processar_consulta_completa"""
    print("🔍 TESTANDO CONSULTA COMPLETA:")
    
    try:
        if not assistente:
            print("  ❌ Assistente não disponível")
            return False
            
        resultado = assistente.processar_consulta_completa(
            pergunta="O que é crime?",
            contexto="",
            modelo="openai"
        )
        
        if isinstance(resultado, dict):
            print("  ✅ Consulta completa retornou dicionário")
            print(f"  📊 Status: {resultado.get('status', 'N/A')}")
            print(f"  📄 Documentos encontrados: {resultado.get('total_documentos', 0)}")
            
            resposta = resultado.get('resposta', '')
            if resposta and "Não foi possível" not in resposta:
                print("  ✅ Resposta válida gerada")
                print(f"  📝 Início da resposta: {resposta[:100]}...")
                return True
            else:
                print("  ❌ Resposta inválida ou erro")
                print(f"  📝 Resposta: {resposta}")
                if 'erro' in resultado:
                    print(f"  ⚠️  Erro reportado: {resultado['erro']}")
                return False
        else:
            print(f"  ❌ Consulta não retornou dicionário: {type(resultado)}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro na consulta completa: {e}")
        print(f"  📋 Traceback: {traceback.format_exc()}")
        return False

def testar_rotas_assistentes():
    """Testa se as rotas dos assistentes estão funcionando"""
    print("🔍 TESTANDO ROTAS DOS ASSISTENTES:")
    
    try:
        import requests
        base_url = "http://localhost:5000"
        
        # Testar rota de áreas disponíveis
        try:
            response = requests.get(f"{base_url}/assistentes/areas", timeout=5)
            if response.status_code == 200:
                print("  ✅ Rota /assistentes/areas funcionando")
                data = response.json()
                print(f"  📊 Áreas disponíveis: {len(data.get('areas', {}))}")
            else:
                print(f"  ❌ Rota /assistentes/areas: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Erro ao testar rota áreas: {e}")
        
        # Testar rota de consulta
        try:
            payload = {
                'area': 'direito_penal',
                'pergunta': 'O que é crime?',
                'modelo': 'openai'
            }
            response = requests.post(f"{base_url}/assistentes/consulta", json=payload, timeout=10)
            
            if response.status_code == 200:
                print("  ✅ Rota /assistentes/consulta funcionando")
                data = response.json()
                if data.get('status') == 'sucesso':
                    print("  ✅ Consulta processada com sucesso")
                else:
                    print(f"  ❌ Consulta falhou: {data.get('erro', 'N/A')}")
            else:
                print(f"  ❌ Rota /assistentes/consulta: Status {response.status_code}")
                print(f"  📝 Resposta: {response.text[:200]}...")
                
        except Exception as e:
            print(f"  ❌ Erro ao testar rota consulta: {e}")
            
        return True
        
    except ImportError:
        print("  ⚠️  Requests não disponível - pulando teste de rotas")
        return True
    except Exception as e:
        print(f"  ❌ Erro geral no teste de rotas: {e}")
        return False

def main():
    """Executa todos os testes de debug"""
    print("=" * 60)
    print("🔍 DEBUG COMPLETO - SISTEMA DE ASSISTENTES JURÍDICOS")
    print("=" * 60)
    
    # Executar todos os testes
    testes = [
        testar_variaveis_ambiente,
        testar_conexao_database,
        testar_importacoes_assistentes,
    ]
    
    resultados = []
    assistente = None
    
    for teste in testes:
        try:
            resultado = teste()
            resultados.append(resultado)
            print()
        except Exception as e:
            print(f"❌ Erro no teste {teste.__name__}: {e}")
            resultados.append(False)
            print()
    
    # Se importações funcionaram, testar criação
    if resultados[-1]:  # Se importações OK
        assistente = testar_criacao_assistente()
        print()
        
        if assistente:
            testar_busca_documentos(assistente)
            print()
            
            testar_processamento_ia(assistente)
            print()
            
            testar_consulta_completa(assistente)
            print()
    
    # Testar rotas
    testar_rotas_assistentes()
    print()
    
    # Relatório final
    print("=" * 60)
    print("📊 RELATÓRIO FINAL DO DEBUG")
    print("=" * 60)
    
    if all(resultados):
        print("✅ TODOS OS TESTES BÁSICOS PASSARAM")
        if assistente:
            print("✅ ASSISTENTE CRIADO E FUNCIONANDO")
            print("\n🔧 PRÓXIMOS PASSOS:")
            print("1. Verificar logs da aplicação principal")
            print("2. Testar interface web diretamente")
            print("3. Verificar se o erro persiste")
        else:
            print("❌ ASSISTENTE NÃO PÔDE SER CRIADO")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("\n🔧 PROBLEMAS IDENTIFICADOS:")
        nomes_testes = ['Variáveis Ambiente', 'Conexão Database', 'Importações']
        for i, resultado in enumerate(resultados):
            if not resultado:
                print(f"- {nomes_testes[i]}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()