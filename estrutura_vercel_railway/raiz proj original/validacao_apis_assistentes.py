"""
Script de Validação Completa das APIs para Todos os Assistentes Jurídicos
Testa conectividade e remove provedores Perplexity e xAI(Grok)
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidadorAPIsAssistentes:
    """Validador completo das APIs para todos os assistentes jurídicos"""
    
    def __init__(self):
        self.provedores_validos = ['openai', 'anthropic', 'gemini', 'deepseek']
        self.provedores_remover = ['perplexity', 'xai', 'grok']
        self.resultados_validacao = {}
        self.areas_juridicas = [
            'direito_penal', 'direito_civil', 'direito_trabalhista', 
            'direito_empresarial', 'direito_constitucional', 'direito_administrativo',
            'direito_tributario', 'direito_consumidor', 'direito_familia',
            'direito_previdenciario', 'direito_ambiental', 'direito_digital',
            'direito_agrario', 'direito_bancario', 'direito_imobiliario',
            'direito_securitario', 'negociacao_conflitos', 'analise_riscos',
            'recuperacao_credito'
        ]
    
    def verificar_chaves_api(self) -> Dict[str, bool]:
        """Verifica se as chaves das APIs estão configuradas"""
        chaves_status = {}
        
        # OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        chaves_status['openai'] = bool(openai_key and openai_key.strip())
        
        # Anthropic
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        chaves_status['anthropic'] = bool(anthropic_key and anthropic_key.strip())
        
        # Google Gemini
        gemini_key = os.getenv('GOOGLE_API_KEY')
        chaves_status['gemini'] = bool(gemini_key and gemini_key.strip())
        
        # DeepSeek
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        chaves_status['deepseek'] = bool(deepseek_key and deepseek_key.strip())
        
        return chaves_status
    
    def testar_conexao_openai(self) -> Dict[str, Any]:
        """Testa conexão com OpenAI"""
        try:
            import openai
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Teste simples
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Teste de conectividade"}],
                max_tokens=10
            )
            
            return {
                'status': 'sucesso',
                'modelo_testado': 'gpt-3.5-turbo',
                'resposta_chars': len(response.choices[0].message.content or "")
            }
        except Exception as e:
            return {
                'status': 'erro',
                'erro': str(e)
            }
    
    def testar_conexao_anthropic(self) -> Dict[str, Any]:
        """Testa conexão com Anthropic"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            
            # Teste simples
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Teste de conectividade"}]
            )
            
            return {
                'status': 'sucesso',
                'modelo_testado': 'claude-3-haiku-20240307',
                'resposta_chars': len(response.content[0].text if response.content else "")
            }
        except Exception as e:
            return {
                'status': 'erro',
                'erro': str(e)
            }
    
    def testar_conexao_gemini(self) -> Dict[str, Any]:
        """Testa conexão com Google Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Teste de conectividade")
            
            return {
                'status': 'sucesso',
                'modelo_testado': 'gemini-1.5-flash',
                'resposta_chars': len(response.text or "")
            }
        except Exception as e:
            return {
                'status': 'erro',
                'erro': str(e)
            }
    
    def testar_conexao_deepseek(self) -> Dict[str, Any]:
        """Testa conexão com DeepSeek"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {os.getenv("DEEPSEEK_API_KEY")}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'deepseek-chat',
                'messages': [{'role': 'user', 'content': 'Teste de conectividade'}],
                'max_tokens': 10
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'sucesso',
                    'modelo_testado': 'deepseek-chat',
                    'resposta_chars': len(result['choices'][0]['message']['content'] or "")
                }
            else:
                return {
                    'status': 'erro',
                    'erro': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'erro',
                'erro': str(e)
            }
    
    def validar_todas_apis(self) -> Dict[str, Any]:
        """Executa validação completa de todas as APIs"""
        logger.info("🔍 Iniciando validação das APIs...")
        
        chaves_status = self.verificar_chaves_api()
        resultados_testes = {}
        
        logger.info("📋 Status das chaves de API:")
        for provedor, status in chaves_status.items():
            status_texto = "✅ Configurada" if status else "❌ Não configurada"
            logger.info(f"  {provedor}: {status_texto}")
        
        # Testar cada API se a chave estiver disponível
        if chaves_status['openai']:
            logger.info("🧪 Testando OpenAI...")
            resultados_testes['openai'] = self.testar_conexao_openai()
        else:
            resultados_testes['openai'] = {'status': 'chave_ausente'}
        
        if chaves_status['anthropic']:
            logger.info("🧪 Testando Anthropic...")
            resultados_testes['anthropic'] = self.testar_conexao_anthropic()
        else:
            resultados_testes['anthropic'] = {'status': 'chave_ausente'}
        
        if chaves_status['gemini']:
            logger.info("🧪 Testando Gemini...")
            resultados_testes['gemini'] = self.testar_conexao_gemini()
        else:
            resultados_testes['gemini'] = {'status': 'chave_ausente'}
        
        if chaves_status['deepseek']:
            logger.info("🧪 Testando DeepSeek...")
            resultados_testes['deepseek'] = self.testar_conexao_deepseek()
        else:
            resultados_testes['deepseek'] = {'status': 'chave_ausente'}
        
        return {
            'timestamp': datetime.now().isoformat(),
            'chaves_configuradas': chaves_status,
            'testes_conectividade': resultados_testes,
            'resumo': self._gerar_resumo_validacao(chaves_status, resultados_testes)
        }
    
    def _gerar_resumo_validacao(self, chaves: Dict[str, bool], testes: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo da validação"""
        funcionando = []
        com_problemas = []
        sem_chave = []
        
        for provedor in self.provedores_validos:
            if not chaves.get(provedor, False):
                sem_chave.append(provedor)
            elif testes.get(provedor, {}).get('status') == 'sucesso':
                funcionando.append(provedor)
            else:
                com_problemas.append(provedor)
        
        return {
            'funcionando': funcionando,
            'com_problemas': com_problemas,
            'sem_chave': sem_chave,
            'total_funcionando': len(funcionando),
            'total_problemas': len(com_problemas),
            'total_sem_chave': len(sem_chave)
        }
    
    def atualizar_arquivo_configuracao_apis(self):
        """Atualiza arquivo de configuração removendo provedores indesejados"""
        try:
            config_path = 'config/api_providers.py'
            
            if not os.path.exists(config_path):
                logger.warning(f"Arquivo {config_path} não encontrado")
                return False
            
            # Ler arquivo atual
            with open(config_path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Remover referências aos provedores indesejados
            linhas_modificadas = []
            for linha in conteudo.split('\n'):
                linha_lower = linha.lower()
                if any(provedor in linha_lower for provedor in self.provedores_remover):
                    logger.info(f"Removendo linha: {linha.strip()}")
                    continue
                linhas_modificadas.append(linha)
            
            # Salvar arquivo atualizado
            conteudo_novo = '\n'.join(linhas_modificadas)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(conteudo_novo)
            
            logger.info(f"✅ Arquivo {config_path} atualizado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração: {e}")
            return False
    
    def atualizar_assistentes_base(self):
        """Atualiza classe base dos assistentes removendo provedores"""
        try:
            base_path = 'modules/assistentes_juridicos/assistente_base.py'
            
            if not os.path.exists(base_path):
                logger.warning(f"Arquivo {base_path} não encontrado")
                return False
            
            # Ler arquivo atual
            with open(base_path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Atualizar lista de provedores válidos
            conteudo_novo = conteudo.replace(
                "self.provedores_disponiveis = ['openai', 'anthropic', 'gemini', 'deepseek', 'perplexity', 'xai']",
                "self.provedores_disponiveis = ['openai', 'anthropic', 'gemini', 'deepseek']"
            )
            
            # Remover outras referências
            for provedor in self.provedores_remover:
                conteudo_novo = conteudo_novo.replace(f"'{provedor}'", "")
                conteudo_novo = conteudo_novo.replace(f'"{provedor}"', "")
            
            # Salvar arquivo atualizado
            with open(base_path, 'w', encoding='utf-8') as f:
                f.write(conteudo_novo)
            
            logger.info(f"✅ Arquivo {base_path} atualizado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar assistente base: {e}")
            return False
    
    def gerar_relatorio_completo(self, resultados: Dict[str, Any]):
        """Gera relatório completo da validação"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        relatorio_path = f'relatorio_validacao_apis_{timestamp}.json'
        
        try:
            with open(relatorio_path, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Relatório salvo em: {relatorio_path}")
            
            # Exibir resumo no console
            resumo = resultados['resumo']
            logger.info("="*50)
            logger.info("📊 RESUMO DA VALIDAÇÃO DAS APIs")
            logger.info("="*50)
            logger.info(f"✅ APIs funcionando: {resumo['total_funcionando']}")
            for api in resumo['funcionando']:
                logger.info(f"  - {api}")
            
            logger.info(f"❌ APIs com problemas: {resumo['total_problemas']}")
            for api in resumo['com_problemas']:
                erro = resultados['testes_conectividade'][api].get('erro', 'Erro desconhecido')
                logger.info(f"  - {api}: {erro}")
            
            logger.info(f"🔑 APIs sem chave: {resumo['total_sem_chave']}")
            for api in resumo['sem_chave']:
                logger.info(f"  - {api}")
            
            logger.info("="*50)
            
            return relatorio_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return None
    
    def executar_validacao_completa(self):
        """Executa validação completa do sistema"""
        logger.info("🚀 Iniciando validação completa das APIs dos assistentes...")
        
        # 1. Validar todas as APIs
        resultados = self.validar_todas_apis()
        
        # 2. Atualizar configurações removendo provedores indesejados
        logger.info("🔧 Atualizando configurações...")
        self.atualizar_arquivo_configuracao_apis()
        self.atualizar_assistentes_base()
        
        # 3. Gerar relatório
        relatorio_path = self.gerar_relatorio_completo(resultados)
        
        # 4. Recomendações
        self._gerar_recomendacoes(resultados)
        
        logger.info("✅ Validação completa finalizada!")
        return resultados
    
    def _gerar_recomendacoes(self, resultados: Dict[str, Any]):
        """Gera recomendações baseadas nos resultados"""
        logger.info("💡 RECOMENDAÇÕES:")
        
        resumo = resultados['resumo']
        
        if resumo['total_sem_chave'] > 0:
            logger.info("🔑 Configurar chaves das APIs:")
            for api in resumo['sem_chave']:
                if api == 'openai':
                    logger.info("  - OPENAI_API_KEY (obter em https://platform.openai.com/api-keys)")
                elif api == 'anthropic':
                    logger.info("  - ANTHROPIC_API_KEY (obter em https://console.anthropic.com/)")
                elif api == 'gemini':
                    logger.info("  - GOOGLE_API_KEY (obter em https://console.cloud.google.com/)")
                elif api == 'deepseek':
                    logger.info("  - DEEPSEEK_API_KEY (obter em https://platform.deepseek.com/)")
        
        if resumo['total_problemas'] > 0:
            logger.info("🔧 Verificar problemas de conectividade:")
            for api in resumo['com_problemas']:
                erro = resultados['testes_conectividade'][api].get('erro', '')
                if 'auth' in erro.lower() or 'unauthorized' in erro.lower():
                    logger.info(f"  - {api}: Verificar validade da chave de API")
                elif 'network' in erro.lower() or 'timeout' in erro.lower():
                    logger.info(f"  - {api}: Verificar conexão de rede")
                else:
                    logger.info(f"  - {api}: {erro}")
        
        if resumo['total_funcionando'] == len(self.provedores_validos):
            logger.info("🎉 Todas as APIs estão funcionando perfeitamente!")


def main():
    """Função principal"""
    validador = ValidadorAPIsAssistentes()
    resultados = validador.executar_validacao_completa()
    return resultados


if __name__ == "__main__":
    main()