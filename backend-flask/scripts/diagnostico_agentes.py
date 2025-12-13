"""
Script de Diagnóstico de Conectividade dos Agentes IA
=====================================================
Testa a conexão com todas as APIs de IA utilizadas no sistema
"""

import os
import sys
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

# Carregar variáveis de ambiente
load_dotenv()

def print_header(text):
    """Imprime cabeçalho formatado"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text.center(70)}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_info(text):
    """Imprime mensagem informativa"""
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

def check_env_key(key_name):
    """Verifica se uma chave de API existe nas variáveis de ambiente"""
    value = os.getenv(key_name)
    if value:
        # Mostrar apenas os primeiros e últimos caracteres
        masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        print_success(f"{key_name}: {masked_value}")
        return True
    else:
        print_error(f"{key_name}: NÃO CONFIGURADA")
        return False

def test_openai():
    """Testa conexão com OpenAI"""
    print_header("🤖 TESTE OPENAI")
    
    if not check_env_key('OPENAI_API_KEY'):
        print_warning("OpenAI não pode ser testada - chave ausente")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Teste simples - usando GPT-4o (padrão do sistema)
        response = client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[{"role": "user", "content": "teste"}],
            max_tokens=5
        )
        
        print_success(f"Modelo: {response.model}")
        print_success(f"Conexão estabelecida com sucesso!")
        return True
        
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_anthropic():
    """Testa conexão com Anthropic"""
    print_header("🧠 TESTE ANTHROPIC (CLAUDE)")
    
    if not check_env_key('ANTHROPIC_API_KEY'):
        print_warning("Anthropic não pode ser testada - chave ausente")
        return False
    
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Teste simples - usando Claude Haiku 4.5 (padrão do sistema)
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "teste"}]
        )
        
        print_success(f"Modelo: {message.model}")
        print_success(f"Conexão estabelecida com sucesso!")
        return True
        
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_google_ai():
    """Testa conexão com Google AI (Gemini)"""
    print_header("🌟 TESTE GOOGLE AI (GEMINI)")
    
    # Verificar múltiplas variações de nome
    google_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if google_key:
        print_success(f"GOOGLE_AI_API_KEY: {google_key[:8]}...{google_key[-4:]}")
    else:
        print_error("GOOGLE_AI_API_KEY: NÃO CONFIGURADA")
        print_info("Tentando variações: GOOGLE_API_KEY, GEMINI_API_KEY")
        print_error("Nenhuma chave Google encontrada")
        print_warning("Google AI não pode ser testada - chave ausente")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=google_key)
        
        # Listar modelos disponíveis
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print_success(f"Modelos disponíveis: {len(models)}")
        
        # Teste simples - usando Gemini 2.5 Flash (padrão do sistema)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("teste", generation_config={"max_output_tokens": 5})
        
        print_success(f"Modelo: gemini-2.5-flash")
        print_success(f"Conexão estabelecida com sucesso!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            print_warning(f"⚠️  API Key válida, mas quota diária excedida")
            print_warning(f"   Aguarde até amanhã ou atualize o plano")
            return "quota_exceeded"
        else:
            print_error(f"Erro ao conectar: {error_msg}")
            return False

def test_deepseek():
    """Testa conexão com DeepSeek"""
    print_header("🔮 TESTE DEEPSEEK")
    
    if not check_env_key('DEEPSEEK_API_KEY'):
        print_warning("DeepSeek não pode ser testada - chave ausente")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )
        
        # Teste simples
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "teste"}],
            max_tokens=5
        )
        
        print_success(f"Modelo: {response.model}")
        print_success(f"Conexão estabelecida com sucesso!")
        return True
        
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def main():
    """Função principal de diagnóstico"""
    print_header("🔍 DIAGNÓSTICO DE CONECTIVIDADE DOS AGENTES IA")
    
    results = {
        'OpenAI': test_openai(),
        'Anthropic': test_anthropic(),
        'Google AI': test_google_ai(),
        'DeepSeek': test_deepseek()
    }
    
    # Resumo final
    print_header("📊 RESUMO DO DIAGNÓSTICO")
    
    total = len(results)
    successful = sum(1 for v in results.values() if v == True)
    quota_exceeded = sum(1 for v in results.values() if v == "quota_exceeded")
    failed = total - successful - quota_exceeded
    
    for name, status in results.items():
        if status == True:
            print_success(f"{name}: CONECTADO")
        elif status == "quota_exceeded":
            print_warning(f"{name}: QUOTA EXCEDIDA (API válida)")
        else:
            print_error(f"{name}: FALHA")
    
    print(f"\n{Fore.CYAN}Total de APIs: {total}")
    print(f"{Fore.GREEN}Conectadas: {successful}")
    if quota_exceeded > 0:
        print(f"{Fore.YELLOW}Quota Excedida: {quota_exceeded}")
    print(f"{Fore.RED}Com Falha: {failed}{Style.RESET_ALL}\n")
    
    if failed > 0:
        print_warning("⚠️  ATENÇÃO: Algumas APIs não estão funcionando!")
        print_info("Verifique as credenciais das APIs com falha")
        return False
    elif quota_exceeded > 0:
        print_warning("⚠️  ATENÇÃO: Algumas APIs excederam a quota diária")
        print_info("As chaves são válidas, mas aguarde até amanhã ou atualize o plano")
        print_success(f"✅ {successful} de {total} APIs estão funcionando corretamente!")
        return True
    else:
        print_success("🎉 TODAS AS APIs ESTÃO FUNCIONANDO CORRETAMENTE!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
