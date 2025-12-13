"""
Script para corrigir definitivamente o arquivo assistente_base.py
Remove todos os vestígios de Perplexity e xAI(Grok) e corrige erros de sintaxe
"""

import re
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def corrigir_assistente_base():
    """Corrige o arquivo assistente_base.py removendo provedores indesejados"""
    
    arquivo = 'modules/assistentes_juridicos/assistente_base.py'
    
    try:
        # Ler o arquivo atual
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        logger.info("Arquivo lido com sucesso")
        
        # Remover todas as referências a Perplexity
        patterns_remover = [
            r'.*perplexity.*\n',
            r'.*Perplexity.*\n', 
            r'.*PERPLEXITY.*\n',
            r'.*xai.*\n',
            r'.*XAI.*\n',
            r'.*grok.*\n',
            r'.*Grok.*\n',
            r'.*GROK.*\n'
        ]
        
        for pattern in patterns_remover:
            conteudo = re.sub(pattern, '', conteudo, flags=re.IGNORECASE)
        
        # Corrigir linhas com sintaxe quebrada
        linhas_quebradas = [
            r'if chaves\.get\(\):\s*\n',
            r'chaves\[\] = .*\n',
            r'api_key=chaves\[\],\s*\n'
        ]
        
        for pattern in linhas_quebradas:
            conteudo = re.sub(pattern, '', conteudo, flags=re.MULTILINE)
        
        # Limpar linhas vazias excessivas
        conteudo = re.sub(r'\n\s*\n\s*\n', '\n\n', conteudo)
        
        # Corrigir lista de provedores disponíveis
        conteudo = re.sub(
            r'self\.provedores_disponiveis = \[.*?\]',
            "self.provedores_disponiveis = ['openai', 'anthropic', 'gemini', 'deepseek']",
            conteudo,
            flags=re.DOTALL
        )
        
        # Salvar arquivo corrigido
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        logger.info("✅ Arquivo assistente_base.py corrigido com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao corrigir arquivo: {e}")
        return False

def validar_sintaxe():
    """Valida se o arquivo Python tem sintaxe correta"""
    try:
        import py_compile
        py_compile.compile('modules/assistentes_juridicos/assistente_base.py', doraise=True)
        logger.info("✅ Sintaxe do arquivo validada com sucesso")
        return True
    except py_compile.PyCompileError as e:
        logger.error(f"❌ Erro de sintaxe: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔧 Iniciando correção do assistente_base.py...")
    
    if corrigir_assistente_base():
        if validar_sintaxe():
            logger.info("🎉 Correção concluída com sucesso!")
        else:
            logger.error("❌ Arquivo ainda contém erros de sintaxe")
    else:
        logger.error("❌ Falha na correção do arquivo")

if __name__ == "__main__":
    main()