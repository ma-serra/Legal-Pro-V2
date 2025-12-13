"""
Script final para corrigir todos os assistentes jurídicos
Resolve problemas de métodos ausentes e encoding
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def corrigir_assistente_empresarial():
    """Corrige o assistente empresarial completamente"""
    arquivo = 'modules/assistentes/assistente_empresarial.py'
    
    conteudo_correto = '''"""
Assistente Jurídico Especializado em Direito Empresarial
"""
from typing import Dict, List, Any
from .assistente_base import AssistenteBase

class AssistenteEmpresarial(AssistenteBase):
    """Assistente especializado em Direito Empresarial"""
    
    def __init__(self):
        super().__init__("empresarial")
        self.nome = "Assistente Empresarial"
        self.descricao = "Especialista em Direito Empresarial e Societário"
        self.areas_especializacao = [
            "Constituição de Empresas",
            "Contratos Empresariais",
            "Direito Societário",
            "Compliance Corporativo",
            "Fusões e Aquisições",
            "Propriedade Intelectual"
        ]
    
    def processar_consulta_completa(self, pergunta: str, api_escolhida: str = "openai", 
                                  estilo: str = "juridico_tecnico", 
                                  usar_base_vetorial: bool = True):
        """Processa consulta completa usando assistente base"""
        try:
            return super().processar_consulta_completa(pergunta, api_escolhida, estilo, usar_base_vetorial)
        except Exception as e:
            return {
                'resposta': f"Erro ao processar consulta: {str(e)}",
                'contexto_usado': False,
                'resultados_busca': [],
                'api_utilizada': api_escolhida,
                'status': 'erro'
            }
    
    def obter_templates_area(self) -> List[Dict]:
        return [
            {
                'id': 'contrato_social',
                'nome': 'Contrato Social',
                'categoria': 'Constituição',
                'descricao': 'Contrato para constituição de sociedade limitada',
                'campos': ['socios', 'capital_social', 'objeto_social', 'administracao', 'sede']
            },
            {
                'id': 'acordo_acionistas',
                'nome': 'Acordo de Acionistas',
                'categoria': 'Societário',
                'descricao': 'Acordo entre acionistas de sociedade anônima',
                'campos': ['acionistas', 'participacoes', 'governanca', 'transferencia_acoes']
            }
        ]
    
    def obter_prompts_especializados(self) -> Dict[str, str]:
        return {
            'analise_contrato': "Analise o contrato empresarial sob aspectos de compliance e riscos jurídicos...",
            'due_diligence': "Realize due diligence jurídica focando em aspectos societários e contratuais...",
            'estrutura_societaria': "Avalie a estrutura societária proposta considerando eficiência fiscal..."
        }
'''
    
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_correto)
        logger.info(f"✅ {arquivo} corrigido completamente")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir {arquivo}: {e}")
        return False

def adicionar_metodo_aos_assistentes():
    """Adiciona método processar_consulta_completa aos assistentes que não têm"""
    assistentes = [
        'modules/assistentes/assistente_agrario.py',
        'modules/assistentes/assistente_analise_riscos.py',
        'modules/assistentes/assistente_recuperacao.py'
    ]
    
    metodo_processar = '''
    def processar_consulta_completa(self, pergunta: str, api_escolhida: str = "openai", 
                                  estilo: str = "juridico_tecnico", 
                                  usar_base_vetorial: bool = True):
        """Processa consulta completa usando assistente base"""
        try:
            return super().processar_consulta_completa(pergunta, api_escolhida, estilo, usar_base_vetorial)
        except Exception as e:
            return {
                'resposta': f"Erro ao processar consulta: {str(e)}",
                'contexto_usado': False,
                'resultados_busca': [],
                'api_utilizada': api_escolhida,
                'status': 'erro'
            }
'''
    
    for arquivo in assistentes:
        if os.path.exists(arquivo):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                if 'def processar_consulta_completa(' not in conteudo:
                    # Encontrar a última linha da classe
                    lines = conteudo.split('\n')
                    
                    # Procurar pela última linha com conteúdo válido
                    for i in range(len(lines) - 1, -1, -1):
                        line = lines[i].strip()
                        if line and not line.startswith('#'):
                            # Inserir método antes da última linha
                            lines.insert(i + 1, metodo_processar)
                            break
                    
                    conteudo_atualizado = '\n'.join(lines)
                    
                    with open(arquivo, 'w', encoding='utf-8') as f:
                        f.write(conteudo_atualizado)
                    
                    logger.info(f"✅ Método adicionado em {arquivo}")
                else:
                    logger.info(f"✅ Método já existe em {arquivo}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao processar {arquivo}: {e}")
        else:
            logger.warning(f"⚠️ Arquivo não encontrado: {arquivo}")

def corrigir_encoding_system_prompts():
    """Remove caracteres especiais dos prompts do sistema"""
    arquivo_base = 'modules/assistentes_juridicos/assistente_base.py'
    
    try:
        with open(arquivo_base, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar se ainda há problemas de encoding
        replacements = {
            'ã': 'a', 'á': 'a', 'à': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e', 'è': 'e',
            'í': 'i', 'î': 'i', 'ì': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o', 'ò': 'o',
            'ú': 'u', 'û': 'u', 'ù': 'u',
            'ç': 'c',
            'ñ': 'n'
        }
        
        conteudo_corrigido = conteudo
        alteracoes = 0
        
        for char_original, char_substituto in replacements.items():
            if char_original in conteudo_corrigido:
                conteudo_corrigido = conteudo_corrigido.replace(char_original, char_substituto)
                alteracoes += 1
        
        if alteracoes > 0:
            with open(arquivo_base, 'w', encoding='utf-8') as f:
                f.write(conteudo_corrigido)
            logger.info(f"✅ {alteracoes} caracteres especiais corrigidos em {arquivo_base}")
        else:
            logger.info(f"✅ Nenhum caractere especial encontrado em {arquivo_base}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir encoding: {e}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando correção final dos assistentes...")
    
    # 1. Corrigir assistente empresarial completamente
    corrigir_assistente_empresarial()
    
    # 2. Adicionar métodos ausentes
    adicionar_metodo_aos_assistentes()
    
    # 3. Corrigir encoding
    corrigir_encoding_system_prompts()
    
    logger.info("🎉 Correção final dos assistentes concluída!")

if __name__ == "__main__":
    main()