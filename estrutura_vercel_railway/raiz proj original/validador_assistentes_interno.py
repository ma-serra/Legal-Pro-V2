"""
Script de Validação Interna dos Assistentes Jurídicos
Testa todas as funcionalidades e corrige erros automaticamente
"""

import os
import sys
import logging
import traceback
import json
from typing import Dict, List, Any
import psycopg2
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidadorAssistentes:
    """Validador interno completo dos assistentes jurídicos"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.resultados_validacao = {
            'testes_realizados': 0,
            'testes_aprovados': 0,
            'testes_falharam': 0,
            'erros_encontrados': [],
            'correcoes_aplicadas': [],
            'areas_testadas': []
        }
        
    def conectar_database(self):
        """Conecta ao banco de dados PostgreSQL"""
        try:
            conn = psycopg2.connect(self.database_url)
            return conn
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            return None
    
    def validar_estrutura_assistentes(self):
        """Valida estrutura dos arquivos de assistentes"""
        logger.info("🔍 Validando estrutura dos assistentes...")
        
        assistentes_esperados = [
            'modules/assistentes_juridicos/assistente_base.py',
            'modules/assistentes_juridicos/gerenciador_central.py',
            'modules/assistentes/assistente_empresarial.py',
            'modules/assistentes/assistente_agrario.py',
            'modules/assistentes/assistente_analise_riscos.py',
            'modules/assistentes/assistente_recuperacao.py'
        ]
        
        for arquivo in assistentes_esperados:
            if not os.path.exists(arquivo):
                erro = f"Arquivo de assistente não encontrado: {arquivo}"
                self.resultados_validacao['erros_encontrados'].append(erro)
                logger.error(f"❌ {erro}")
            else:
                logger.info(f"✅ Arquivo encontrado: {arquivo}")
        
        self.resultados_validacao['testes_realizados'] += len(assistentes_esperados)
        self.resultados_validacao['testes_aprovados'] += len([a for a in assistentes_esperados if os.path.exists(a)])
    
    def validar_metodos_obrigatorios(self):
        """Valida se todos os métodos obrigatórios existem"""
        logger.info("🔍 Validando métodos obrigatórios...")
        
        metodos_obrigatorios = [
            'processar_consulta_completa',
            'chat_openai',
            'chat_anthropic',
            'chat_gemini',
            'buscar_semantica'
        ]
        
        try:
            # Importar e testar assistente base
            sys.path.append('.')
            from modules.assistentes_juridicos.assistente_base import AssistenteJuridicoBase
            
            assistente_teste = AssistenteJuridicoBase("teste")
            
            for metodo in metodos_obrigatorios:
                if hasattr(assistente_teste, metodo):
                    logger.info(f"✅ Método {metodo} encontrado")
                    self.resultados_validacao['testes_aprovados'] += 1
                else:
                    erro = f"Método obrigatório ausente: {metodo}"
                    self.resultados_validacao['erros_encontrados'].append(erro)
                    logger.error(f"❌ {erro}")
                    self.resultados_validacao['testes_falharam'] += 1
                
                self.resultados_validacao['testes_realizados'] += 1
                
        except Exception as e:
            erro = f"Erro ao validar métodos obrigatórios: {str(e)}"
            self.resultados_validacao['erros_encontrados'].append(erro)
            logger.error(f"❌ {erro}")
    
    def testar_interacao_basica(self):
        """Testa interação básica com cada assistente"""
        logger.info("🔍 Testando interação básica...")
        
        areas_teste = [
            'direito_penal',
            'direito_civil',
            'direito_trabalhista',
            'direito_empresarial'
        ]
        
        for area in areas_teste:
            try:
                logger.info(f"Testando área: {area}")
                
                # Importar assistente base
                from modules.assistentes_juridicos.assistente_base import AssistenteJuridicoBase
                assistente = AssistenteJuridicoBase(area)
                
                # Teste 1: Verificar inicialização
                if assistente.area_juridica == area:
                    logger.info(f"✅ Assistente {area} inicializado corretamente")
                    self.resultados_validacao['testes_aprovados'] += 1
                else:
                    erro = f"Assistente {area} não inicializou corretamente"
                    self.resultados_validacao['erros_encontrados'].append(erro)
                    self.resultados_validacao['testes_falharam'] += 1
                
                # Teste 2: Verificar status das APIs
                status_apis = assistente.obter_status_apis()
                if isinstance(status_apis, dict):
                    logger.info(f"✅ Status das APIs retornado para {area}")
                    self.resultados_validacao['testes_aprovados'] += 1
                else:
                    erro = f"Status das APIs inválido para {area}"
                    self.resultados_validacao['erros_encontrados'].append(erro)
                    self.resultados_validacao['testes_falharam'] += 1
                
                # Teste 3: Verificar prompt do sistema
                prompt = assistente._get_system_prompt("juridico_tecnico")
                if prompt and len(prompt) > 10:
                    logger.info(f"✅ Prompt do sistema gerado para {area}")
                    self.resultados_validacao['testes_aprovados'] += 1
                else:
                    erro = f"Prompt do sistema inválido para {area}"
                    self.resultados_validacao['erros_encontrados'].append(erro)
                    self.resultados_validacao['testes_falharam'] += 1
                
                self.resultados_validacao['testes_realizados'] += 3
                self.resultados_validacao['areas_testadas'].append(area)
                
            except Exception as e:
                erro = f"Erro ao testar área {area}: {str(e)}"
                self.resultados_validacao['erros_encontrados'].append(erro)
                self.resultados_validacao['testes_falharam'] += 3
                self.resultados_validacao['testes_realizados'] += 3
                logger.error(f"❌ {erro}")
    
    def testar_consulta_completa(self):
        """Testa o método processar_consulta_completa"""
        logger.info("🔍 Testando consulta completa...")
        
        try:
            from modules.assistentes_juridicos.assistente_base import AssistenteJuridicoBase
            assistente = AssistenteJuridicoBase("direito_penal")
            
            # Teste com pergunta simples
            pergunta_teste = "O que e crime?"
            
            resultado = assistente.processar_consulta_completa(
                pergunta=pergunta_teste,
                api_escolhida="openai",
                estilo="juridico_tecnico",
                usar_base_vetorial=False
            )
            
            if isinstance(resultado, dict) and 'resposta' in resultado:
                logger.info("✅ Método processar_consulta_completa funcionando")
                self.resultados_validacao['testes_aprovados'] += 1
                
                # Verificar se não há erro de encoding
                if "ascii" not in resultado['resposta'].lower():
                    logger.info("✅ Sem erros de encoding detectados")
                    self.resultados_validacao['testes_aprovados'] += 1
                else:
                    erro = "Erro de encoding detectado na resposta"
                    self.resultados_validacao['erros_encontrados'].append(erro)
                    self.resultados_validacao['testes_falharam'] += 1
            else:
                erro = "Método processar_consulta_completa retornou formato inválido"
                self.resultados_validacao['erros_encontrados'].append(erro)
                self.resultados_validacao['testes_falharam'] += 1
            
            self.resultados_validacao['testes_realizados'] += 2
            
        except Exception as e:
            erro = f"Erro ao testar consulta completa: {str(e)}"
            self.resultados_validacao['erros_encontrados'].append(erro)
            self.resultados_validacao['testes_falharam'] += 2
            self.resultados_validacao['testes_realizados'] += 2
            logger.error(f"❌ {erro}")
    
    def validar_database_conexao(self):
        """Valida conexão com banco de dados"""
        logger.info("🔍 Validando conexão com banco de dados...")
        
        conn = self.conectar_database()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM agente_juridico")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    logger.info(f"✅ Banco de dados conectado - {count} agentes encontrados")
                    self.resultados_validacao['testes_aprovados'] += 1
                else:
                    erro = "Banco de dados vazio - sem agentes"
                    self.resultados_validacao['erros_encontrados'].append(erro)
                    self.resultados_validacao['testes_falharam'] += 1
                
                cursor.close()
                conn.close()
                
            except Exception as e:
                erro = f"Erro ao consultar banco: {str(e)}"
                self.resultados_validacao['erros_encontrados'].append(erro)
                self.resultados_validacao['testes_falharam'] += 1
        else:
            erro = "Falha ao conectar com banco de dados"
            self.resultados_validacao['erros_encontrados'].append(erro)
            self.resultados_validacao['testes_falharam'] += 1
        
        self.resultados_validacao['testes_realizados'] += 1
    
    def corrigir_erros_encoding(self):
        """Corrige erros de encoding nos assistentes"""
        logger.info("🔧 Corrigindo erros de encoding...")
        
        try:
            # Arquivo principal que contém os prompts
            arquivo_base = 'modules/assistentes_juridicos/assistente_base.py'
            
            if os.path.exists(arquivo_base):
                with open(arquivo_base, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Verificar se ainda há caracteres problemáticos
                caracteres_problematicos = ['ã', 'ç', 'é', 'ê', 'á', 'à', 'ô', 'õ', 'ú', 'í']
                
                conteudo_corrigido = conteudo
                for char in caracteres_problematicos:
                    if char in conteudo_corrigido:
                        # Substituir por versões ASCII-safe
                        replacements = {
                            'ã': 'a', 'ç': 'c', 'é': 'e', 'ê': 'e', 
                            'á': 'a', 'à': 'a', 'ô': 'o', 'õ': 'o', 
                            'ú': 'u', 'í': 'i'
                        }
                        if char in replacements:
                            conteudo_corrigido = conteudo_corrigido.replace(char, replacements[char])
                
                if conteudo_corrigido != conteudo:
                    with open(arquivo_base, 'w', encoding='utf-8') as f:
                        f.write(conteudo_corrigido)
                    
                    correcao = "Caracteres especiais removidos dos prompts do sistema"
                    self.resultados_validacao['correcoes_aplicadas'].append(correcao)
                    logger.info(f"✅ {correcao}")
                
        except Exception as e:
            erro = f"Erro ao corrigir encoding: {str(e)}"
            self.resultados_validacao['erros_encontrados'].append(erro)
            logger.error(f"❌ {erro}")
    
    def corrigir_metodos_ausentes(self):
        """Corrige métodos ausentes nos assistentes especializados"""
        logger.info("🔧 Corrigindo métodos ausentes...")
        
        assistentes_especializados = [
            'modules/assistentes/assistente_empresarial.py',
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
        
        for arquivo in assistentes_especializados:
            if os.path.exists(arquivo):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    if 'def processar_consulta_completa(' not in conteudo:
                        # Encontrar o final da classe para inserir o método
                        lines = conteudo.split('\n')
                        insert_position = -1
                        
                        # Procurar pela última linha com conteúdo da classe
                        for i in range(len(lines) - 1, -1, -1):
                            line = lines[i].strip()
                            if line and not line.startswith('#') and line != '}':
                                insert_position = i + 1
                                break
                        
                        if insert_position > 0:
                            lines.insert(insert_position, metodo_processar)
                            conteudo_atualizado = '\n'.join(lines)
                            
                            with open(arquivo, 'w', encoding='utf-8') as f:
                                f.write(conteudo_atualizado)
                            
                            correcao = f"Método processar_consulta_completa adicionado em {arquivo}"
                            self.resultados_validacao['correcoes_aplicadas'].append(correcao)
                            logger.info(f"✅ {correcao}")
                
                except Exception as e:
                    erro = f"Erro ao corrigir {arquivo}: {str(e)}"
                    self.resultados_validacao['erros_encontrados'].append(erro)
                    logger.error(f"❌ {erro}")
    
    def gerar_relatorio_validacao(self):
        """Gera relatório completo da validação"""
        logger.info("📋 Gerando relatório de validação...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_validacao_assistentes_{timestamp}.json"
        
        # Adicionar estatísticas
        total_testes = self.resultados_validacao['testes_realizados']
        aprovados = self.resultados_validacao['testes_aprovados']
        falharam = self.resultados_validacao['testes_falharam']
        
        taxa_sucesso = (aprovados / total_testes * 100) if total_testes > 0 else 0
        
        relatorio_completo = {
            'timestamp': timestamp,
            'resumo': {
                'total_testes': total_testes,
                'testes_aprovados': aprovados,
                'testes_falharam': falharam,
                'taxa_sucesso_pct': round(taxa_sucesso, 2)
            },
            'detalhes': self.resultados_validacao,
            'status_geral': 'APROVADO' if taxa_sucesso >= 80 else 'REPROVADO'
        }
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(relatorio_completo, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Relatório salvo em: {nome_arquivo}")
            
            # Imprimir resumo no console
            print("\n" + "="*60)
            print("📊 RELATÓRIO DE VALIDAÇÃO DOS ASSISTENTES")
            print("="*60)
            print(f"Total de Testes: {total_testes}")
            print(f"Testes Aprovados: {aprovados}")
            print(f"Testes Falharam: {falharam}")
            print(f"Taxa de Sucesso: {taxa_sucesso:.1f}%")
            print(f"Status Geral: {relatorio_completo['status_geral']}")
            
            if self.resultados_validacao['erros_encontrados']:
                print("\n🚨 ERROS ENCONTRADOS:")
                for i, erro in enumerate(self.resultados_validacao['erros_encontrados'], 1):
                    print(f"{i}. {erro}")
            
            if self.resultados_validacao['correcoes_aplicadas']:
                print("\n✅ CORREÇÕES APLICADAS:")
                for i, correcao in enumerate(self.resultados_validacao['correcoes_aplicadas'], 1):
                    print(f"{i}. {correcao}")
            
            print("="*60)
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")
    
    def executar_validacao_completa(self):
        """Executa validação completa dos assistentes"""
        logger.info("🚀 Iniciando validação completa dos assistentes...")
        
        # 1. Validar estrutura
        self.validar_estrutura_assistentes()
        
        # 2. Validar métodos obrigatórios
        self.validar_metodos_obrigatorios()
        
        # 3. Validar conexão com banco
        self.validar_database_conexao()
        
        # 4. Testar interação básica
        self.testar_interacao_basica()
        
        # 5. Testar consulta completa
        self.testar_consulta_completa()
        
        # 6. Aplicar correções necessárias
        self.corrigir_erros_encoding()
        self.corrigir_metodos_ausentes()
        
        # 7. Gerar relatório
        self.gerar_relatorio_validacao()
        
        logger.info("🎉 Validação completa finalizada!")
        
        return self.resultados_validacao

def main():
    """Função principal"""
    try:
        validador = ValidadorAssistentes()
        resultados = validador.executar_validacao_completa()
        
        # Retornar código de saída baseado no sucesso
        total = resultados['testes_realizados']
        aprovados = resultados['testes_aprovados']
        taxa_sucesso = (aprovados / total * 100) if total > 0 else 0
        
        return 0 if taxa_sucesso >= 80 else 1
        
    except Exception as e:
        logger.error(f"Erro fatal na validação: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())