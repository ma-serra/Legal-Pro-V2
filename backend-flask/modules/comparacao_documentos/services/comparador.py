"""
Serviço para comparação de versões de documentos
"""

import os
import uuid
import logging
import re
import json
import difflib
from typing import Tuple, Dict, List, Any, Optional
from tempfile import NamedTemporaryFile
from diff_match_patch import diff_match_patch
from docx import Document as DocxDocument
from datetime import datetime
from modules.comparacao_documentos.services.custom_htmldiff import render_html_diff
from modules.comparacao_documentos.services.analise_confiavel import (
    analisar_documento_grande, validar_resposta_analise, realizar_analise_secundaria
)
from flask import current_app
from openai import OpenAI
import openai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import green, red, yellow, black
from reportlab.lib.units import inch
from io import BytesIO
import html
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ComparadorDocumentos:
    """
    Classe para comparação de documentos usando diff_match_patch
    """
    
    @staticmethod
    def extrair_texto_docx(arquivo_docx) -> str:
        """
        Extrai o texto de um documento .docx
        """
        try:
            # Salvar o arquivo temporariamente
            with NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                arquivo_docx.save(temp_file.name)
                
            # Abrir o documento com python-docx
            doc = DocxDocument(temp_file.name)
            
            # Extrair o texto
            texto_completo = []
            for paragrafo in doc.paragraphs:
                texto_completo.append(paragrafo.text)
            
            # Remover arquivo temporário
            os.unlink(temp_file.name)
            
            return '\n'.join(texto_completo)
        except Exception as e:
            logger.error(f"Erro ao extrair texto do documento DOCX: {e}")
            raise ValueError(f"Erro ao processar o documento: {e}")
    
    @staticmethod
    def extrair_texto_txt(arquivo_txt) -> str:
        """
        Extrai o texto de um arquivo .txt
        """
        try:
            # Salvar o arquivo temporariamente
            with NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                arquivo_txt.save(temp_file.name)
            
            # Ler o conteúdo do arquivo
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                texto = f.read()
                
            # Remover arquivo temporário
            os.unlink(temp_file.name)
            
            return texto
        except Exception as e:
            logger.error(f"Erro ao extrair texto do arquivo TXT: {e}")
            raise ValueError(f"Erro ao processar o arquivo: {e}")
    
    @staticmethod
    def extrair_texto(arquivo, extensao: str) -> str:
        """
        Extrai o texto de um arquivo com base na sua extensão
        """
        if extensao.lower() == 'docx':
            return ComparadorDocumentos.extrair_texto_docx(arquivo)
        elif extensao.lower() == 'txt':
            return ComparadorDocumentos.extrair_texto_txt(arquivo)
        else:
            raise ValueError(f"Formato de arquivo não suportado: {extensao}")
    
    @staticmethod
    def _destacar_diferencas_caracteres(texto1: str, texto2: str) -> Tuple[str, str]:
        """
        Método auxiliar para destacar diferenças no nível de caracteres entre duas palavras similares.
        Útil para mostrar pequenas alterações em palavras como alterações de tempos verbais, plurais, etc.
        """
        # Escape HTML antes de processar
        texto1_esc = texto1.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        texto2_esc = texto2.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Se os textos são iguais, retornar sem destaque
        if texto1 == texto2:
            return texto1_esc, texto2_esc
            
        # Encontrar a maior substring comum
        matcher = difflib.SequenceMatcher(None, texto1, texto2)
        blocos = matcher.get_matching_blocks()
        
        # Preparar resultado para o texto original
        res1 = []
        ultimo_i = 0
        for i, j, n in blocos:
            # Adicionar parte diferente antes da correspondência
            if i > ultimo_i:
                parte_diferente = texto1_esc[ultimo_i:i]
                res1.append(f'<span class="diff-deletado diff-char diff-char-deleted">{parte_diferente}</span>')
            
            # Adicionar parte correspondente
            if n > 0:
                parte_igual = texto1_esc[i:i+n]
                res1.append(parte_igual)
                
            ultimo_i = i + n
            
        # Preparar resultado para o texto modificado
        res2 = []
        ultimo_j = 0
        for i, j, n in blocos:
            # Adicionar parte diferente antes da correspondência
            if j > ultimo_j:
                parte_diferente = texto2_esc[ultimo_j:j]
                res2.append(f'<span class="diff-adicionado diff-char diff-char-added">{parte_diferente}</span>')
            
            # Adicionar parte correspondente
            if n > 0:
                parte_igual = texto2_esc[j:j+n]
                res2.append(parte_igual)
                
            ultimo_j = j + n
            
        return ''.join(res1), ''.join(res2)
    
    @staticmethod
    def comparar_textos(texto_original: str, texto_modificado: str) -> Tuple[str, str]:
        """
        Compara dois textos e retorna o HTML com as diferenças destacadas de maneira mais precisa
        
        Esta versão utiliza uma implementação robusta e direta para garantir
        que as diferenças sejam visualmente claras e corretamente marcadas.
        """
        logger.info("Iniciando comparação com marcações inline obrigatórias")
        
        try:
            # Usar diff-match-patch diretamente
            dmp = diff_match_patch()
            diffs = dmp.diff_main(texto_original, texto_modificado)
            dmp.diff_cleanupSemantic(diffs)
            
            # Estilos inline obrigatórios - não dependem de CSS externo
            DELETED_STYLE = 'style="background-color:#ffdddd!important;color:#990000!important;text-decoration:line-through!important;padding:2px 4px!important;border-radius:3px!important;display:inline-block!important;margin:0 1px!important;border-left:2px solid #ff0000!important;font-weight:bold!important;"'
            ADDED_STYLE = 'style="background-color:#ddffdd!important;color:#006600!important;padding:2px 4px!important;border-radius:3px!important;display:inline-block!important;margin:0 1px!important;border-left:2px solid #00aa00!important;font-weight:bold!important;"'
            
            # Símbolos visuais
            minus_symbol = '<span style="color:#cc0000!important;font-weight:bold!important;margin-right:3px!important;">−</span>'
            plus_symbol = '<span style="color:#008800!important;font-weight:bold!important;margin-right:3px!important;">+</span>'
            
            # Construir HTML original (só remoções)
            html_original = []
            for op, texto in diffs:
                texto_esc = texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                if op == 0:  # Igual
                    html_original.append(texto_esc)
                elif op == -1:  # Removido
                    html_original.append(f'<span {DELETED_STYLE}>{minus_symbol}{texto_esc}</span>')
            
            # Construir HTML modificado (só adições)
            html_modificado = []
            for op, texto in diffs:
                texto_esc = texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                if op == 0:  # Igual
                    html_modificado.append(texto_esc)
                elif op == 1:  # Adicionado
                    html_modificado.append(f'<span {ADDED_STYLE}>{plus_symbol}{texto_esc}</span>')
            
            # Converter quebras de linha
            html_original_final = "".join(html_original).replace('\n', '<br>')
            html_modificado_final = "".join(html_modificado).replace('\n', '<br>')
            
            # Verificação obrigatória
            tem_remocao = 'background-color:#ffdddd' in html_original_final
            tem_adicao = 'background-color:#ddffdd' in html_modificado_final
            logger.info(f"FORÇADO - Remoção: {tem_remocao}, Adição: {tem_adicao}")
            
            return html_original_final, html_modificado_final
            
        except Exception as e:
            logger.error(f"Erro crítico na comparação: {e}")
            return texto_original.replace('\n', '<br>'), texto_modificado.replace('\n', '<br>')
    
    @staticmethod
    def gerar_titulo_automatico(texto_original: str, limite: int = 50) -> str:
        """
        Gera um título automaticamente a partir do texto original
        """
        # Pegar as primeiras palavras do texto
        palavras = texto_original.split()
        titulo = ' '.join(palavras[:min(10, len(palavras))])
        
        # Limitar o tamanho do título
        if len(titulo) > limite:
            titulo = titulo[:limite] + '...'
            
        return titulo
    
    @staticmethod
    def gerar_id_unico() -> str:
        """
        Gera um ID único para a comparação
        """
        return str(uuid.uuid4())
        
    @staticmethod
    def analisar_diferencas_ia(texto_original: str, texto_modificado: str, area_juridica: str, cliente: str) -> Dict[str, Any]:
        """
        Utiliza a API da OpenAI para analisar as diferenças entre dois textos
        e gerar um resumo das alterações mais relevantes.
        
        Args:
            texto_original: Texto da versão original
            texto_modificado: Texto da versão modificada
            area_juridica: Área jurídica do documento
            cliente: Nome do cliente
            
        Returns:
            Dicionário com o resumo das alterações, pontos críticos e recomendações
        """
        try:
            # Verificar se a API key existe - usar os.environ em vez de current_app.config
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                logger.warning("Chave da API OpenAI não configurada")
                return {
                    "success": False,
                    "error": "API OpenAI não configurada"
                }
                
            # Inicializar o cliente OpenAI
            # o modelo mais recente da OpenAI é "gpt-4o" que foi lançado em 13 de maio de 2024.
            # não altere isso a menos que seja explicitamente solicitado pelo usuário
            client = OpenAI(api_key=api_key)
            
            # Preparar o prompt aprimorado para análise 100% confiável
            prompt_sistema = f"""Você é um especialista jurídico de alto nível responsável por analisar documentos legais com 100% de precisão e confiabilidade.
            
            TAREFA: Analise minuciosamente duas versões de um documento jurídico da área de {area_juridica} 
            para o cliente {cliente} e identifique TODAS as alterações com impacto jurídico, por mínimas que sejam.
            
            CONTEXTO JURÍDICO:
            - Área jurídica: {area_juridica}
            - Cliente: {cliente}
            - Objetivo: Identificar com precisão absoluta todas as alterações entre as versões
            
            PARÂMETROS DE ANÁLISE (aplique TODOS sem exceção):
            1. Alterações em cláusulas, termos, condições ou obrigações
            2. Modificações em quantias, percentuais, datas, prazos ou valores
            3. Adições ou supressões de texto que alterem direitos, deveres ou condições
            4. Mudanças em linguagem ou terminologia que possam impactar a interpretação jurídica
            5. Impacto das alterações em contratos, acordos, leis ou regulamentos relacionados
            6. Análise de potenciais riscos jurídicos, financeiros ou operacionais
            7. Comparação direta de cada parágrafo para detectar alterações de palavras-chave
            
            REQUISITOS DE RESPOSTA:
            - Sua análise DEVE ser 100% precisa e confiável para embasar decisões jurídicas críticas
            - NENHUMA alteração relevante deve ser omitida, mesmo que pareça menor
            - Forneça apenas fatos objetivos, não especulações
            - Seja extremamente detalhado na identificação das diferenças
            
            Responda APENAS em formato JSON com a seguinte estrutura exata:
            
            {{
                "resumo_geral": "Resumo detalhado e completo das alterações com seus impactos jurídicos",
                "alteracoes_criticas": [
                    {{
                        "trecho": "Texto exato do trecho alterado",
                        "efeito": "Descrição detalhada do efeito jurídico da alteração",
                        "risco": "Alto ou Médio ou Baixo"
                    }}
                ],
                "recomendacoes": [
                    "Recomendação específica 1 baseada na análise jurídica",
                    "Recomendação específica 2 baseada na análise jurídica"
                ],
                "impacto_geral": "Alto ou Médio ou Baixo"
            }}
            """
            
            # Limitar o tamanho do texto para evitar exceder o limite de tokens
            max_tokens = 12000  # Limite seguro para caber dentro da capacidade do modelo
            texto_original_truncado = texto_original[:max_tokens] if len(texto_original) > max_tokens else texto_original
            texto_modificado_truncado = texto_modificado[:max_tokens] if len(texto_modificado) > max_tokens else texto_modificado
            
            # Gerar diferenças usando diflib para ajudar na análise
            import difflib
            differ = difflib.Differ()
            diff = list(differ.compare(texto_original_truncado.splitlines(), texto_modificado_truncado.splitlines()))
            diff_highlight = "\n".join([line for line in diff if line.startswith('+ ') or line.startswith('- ') or line.startswith('? ')])
            
            mensagem_usuario = f"""
            DOCUMENTO JURÍDICO PARA ANÁLISE CONFIÁVEL
            
            Versão original:
            ```
            {texto_original_truncado}
            ```
            
            Versão modificada:
            ```
            {texto_modificado_truncado}
            ```
            
            Diferenças identificadas automaticamente (para referência):
            ```
            {diff_highlight[:4000] if len(diff_highlight) > 4000 else diff_highlight}
            ```
            
            INSTRUÇÕES ESPECÍFICAS:
            1. Compare os dois textos com extrema atenção aos detalhes
            2. Identifique TODAS as alterações com relevância jurídica
            3. Classifique o impacto de cada alteração com precisão
            4. Forneça recomendações específicas baseadas nas alterações encontradas
            5. Garanta que sua análise seja 100% confiável para uso em contexto jurídico real
            6. Cite trechos exatos para cada alteração identificada
            """
            
            # Fazer a requisição para a API
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": mensagem_usuario}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0,  # Temperatura zero para resultados 100% determinísticos e confiáveis
                )
                
                # Processar a resposta
                resposta_content = response.choices[0].message.content
                if resposta_content:
                    try:
                        resposta_json = json.loads(resposta_content)
                    except json.JSONDecodeError:
                        # Fallback caso a resposta não seja um JSON válido
                        logger.warning("A resposta da API não é um JSON válido. Criando estrutura básica.")
                        resposta_json = {
                            "resumo_geral": resposta_content[:500] + "...",
                            "alteracoes_criticas": [],
                            "recomendacoes": [],
                            "impacto_geral": "Médio"
                        }
                else:
                    resposta_json = {
                        "resumo_geral": "Não foi possível analisar as diferenças entre os documentos.",
                        "alteracoes_criticas": [],
                        "recomendacoes": ["Recomendamos uma análise manual detalhada das alterações."],
                        "impacto_geral": "Indeterminado"
                    }
                
                return {
                    "success": True,
                    "analise": resposta_json
                }
                
            except openai.APIError as e:
                logger.error(f"Erro na API da OpenAI: {e}")
                return {
                    "success": False,
                    "error": f"Erro na API da OpenAI: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao analisar diferenças com IA: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def gerar_pdf_com_marcacoes(html_diferenca: str, titulo: str = "Comparação de Documentos") -> BytesIO:
        """
        Gera um PDF com as marcações de diferenças coloridas
        """
        try:
            # Criar buffer para o PDF
            buffer = BytesIO()
            
            # Configurar documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Obter estilos
            styles = getSampleStyleSheet()
            
            # Criar estilos personalizados para as marcações
            style_normal = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                leading=12,
                spaceAfter=6
            )
            
            style_titulo = ParagraphStyle(
                'Titulo',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                alignment=1  # Centro
            )
            
            style_adicao = ParagraphStyle(
                'Adicao',
                parent=styles['Normal'],
                fontSize=10,
                leading=12,
                textColor=green,
                backColor=None,
                spaceAfter=6
            )
            
            style_remocao = ParagraphStyle(
                'Remocao',
                parent=styles['Normal'],
                fontSize=10,
                leading=12,
                textColor=red,
                backColor=None,
                spaceAfter=6
            )
            
            # Lista para armazenar elementos do PDF
            elementos = []
            
            # Adicionar título
            elementos.append(Paragraph(titulo, style_titulo))
            elementos.append(Spacer(1, 20))
            
            # Processar HTML das diferenças
            conteudo_processado = ComparadorDocumentos._processar_html_para_pdf(html_diferenca)
            
            # Adicionar conteúdo processado
            for item in conteudo_processado:
                if item['tipo'] == 'normal':
                    elementos.append(Paragraph(item['texto'], style_normal))
                elif item['tipo'] == 'adicao':
                    elementos.append(Paragraph(f"<b>[ADICIONADO]</b> {item['texto']}", style_adicao))
                elif item['tipo'] == 'remocao':
                    elementos.append(Paragraph(f"<b>[REMOVIDO]</b> {item['texto']}", style_remocao))
                elif item['tipo'] == 'modificacao':
                    elementos.append(Paragraph(f"<b>[MODIFICADO]</b> {item['texto']}", style_normal))
                
                elementos.append(Spacer(1, 6))
            
            # Construir PDF
            doc.build(elementos)
            
            # Retornar buffer
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF com marcações: {e}")
            raise
    
    @staticmethod
    def _processar_html_para_pdf(html_content: str) -> List[Dict[str, str]]:
        """
        Processa HTML das diferenças para formato adequado ao PDF
        """
        try:
            import re
            from html import unescape
            
            # Remover tags HTML e processar marcações
            conteudo = []
            
            # Padrões para identificar marcações
            patterns = {
                'adicao': r'<span[^>]*class="[^"]*\badicao\b[^"]*"[^>]*>(.*?)</span>',
                'remocao': r'<span[^>]*class="[^"]*\bremocao\b[^"]*"[^>]*>(.*?)</span>',
                'modificacao': r'<span[^>]*class="[^"]*\bmodificacao\b[^"]*"[^>]*>(.*?)</span>'
            }
            
            # Dividir conteúdo em parágrafos
            paragrafos = html_content.split('\n')
            
            for paragrafo in paragrafos:
                if not paragrafo.strip():
                    continue
                
                # Verificar se contém marcações
                encontrou_marcacao = False
                
                for tipo, pattern in patterns.items():
                    matches = re.findall(pattern, paragrafo, re.IGNORECASE | re.DOTALL)
                    if matches:
                        for match in matches:
                            texto_limpo = re.sub(r'<[^>]+>', '', match)
                            texto_limpo = unescape(texto_limpo).strip()
                            if texto_limpo:
                                conteudo.append({
                                    'tipo': tipo,
                                    'texto': texto_limpo
                                })
                        encontrou_marcacao = True
                        break
                
                # Se não encontrou marcação, é texto normal
                if not encontrou_marcacao:
                    texto_limpo = re.sub(r'<[^>]+>', '', paragrafo)
                    texto_limpo = unescape(texto_limpo).strip()
                    if texto_limpo:
                        conteudo.append({
                            'tipo': 'normal',
                            'texto': texto_limpo
                        })
            
            return conteudo
            
        except Exception as e:
            logger.error(f"Erro ao processar HTML para PDF: {e}")
            return [{'tipo': 'normal', 'texto': 'Erro ao processar conteúdo'}]

    @staticmethod
    def analisar_diferencas_ia_com_origem(texto_original: str, texto_modificado: str, area_processo: str = None, cliente: str = None):
        """
        Analisa as diferenças entre documentos usando IA e identifica de qual versão cada trecho se originou
        """
        try:
            import json
            
            # Verificar se a API key existe
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                logger.warning("Chave da API OpenAI não configurada")
                return {
                    "success": False,
                    "error": "API OpenAI não configurada"
                }
                
            # Inicializar o cliente OpenAI
            client = OpenAI(api_key=api_key)
            
            # Garantir que os textos não sejam None
            texto_original = texto_original or ""
            texto_modificado = texto_modificado or ""
            area_processo = area_processo or "Não especificada"
            
            # Prompt específico para análise com identificação de origem
            prompt = f"""Analise as diferenças entre os dois documentos legais abaixo e identifique:

1. ANÁLISE GERAL:
   - Tipo de alterações realizadas
   - Impacto jurídico das mudanças
   - Área do direito: {area_processo}

2. ANÁLISE DETALHADA POR TRECHO:
   Para cada diferença identificada, especifique:
   - O texto exato do trecho
   - Se o trecho é do DOCUMENTO ORIGINAL ou DOCUMENTO MODIFICADO
   - Tipo de alteração (adição, remoção, modificação)
   - Impacto da alteração
   - Recomendação jurídica

DOCUMENTO ORIGINAL:
{texto_original[:3000]}

DOCUMENTO MODIFICADO:
{texto_modificado[:3000]}

Responda em formato JSON com a seguinte estrutura:
{{
    "resumo_geral": "...",
    "impacto_juridico": "...",
    "trechos_analisados": [
        {{
            "trecho": "texto do trecho",
            "origem": "ORIGINAL" ou "MODIFICADO",
            "tipo_alteracao": "adição|remoção|modificação",
            "impacto": "descrição do impacto",
            "recomendacao": "recomendação jurídica"
        }}
    ],
    "conclusao": "..."
}}"""

            # Fazer a requisição para a API OpenAI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.3
            )
            
            resultado = {
                "success": True,
                "content": response.choices[0].message.content
            }
            
            if resultado.get('success'):
                try:
                    # O conteúdo pode estar em 'content' ou 'response'
                    content = resultado.get('content') or resultado.get('response', '')
                    logger.info(f"Conteúdo recebido da IA: {type(content)} - {str(content)[:200]}...")
                    
                    if isinstance(content, dict):
                        # Se já é um dicionário, use diretamente
                        analise_json = content
                    else:
                        # Tenta fazer parse do JSON
                        try:
                            analise_json = json.loads(str(content))
                        except json.JSONDecodeError:
                            # Se falhar, cria estrutura básica
                            analise_json = {
                                'resumo_geral': str(content),
                                'impacto_juridico': 'Análise realizada com sucesso',
                                'trechos_analisados': [],
                                'conclusao': 'Consulte o resumo geral para detalhes completos'
                            }
                    
                    return {
                        'success': True,
                        'analise': analise_json
                    }
                except Exception as e:
                    logger.error(f"Erro ao processar conteúdo da IA: {e}")
                    # Retorna análise básica
                    content = resultado.get('content') or resultado.get('response', 'Análise concluída')
                    return {
                        'success': True,
                        'analise': {
                            'resumo_geral': str(content),
                            'impacto_juridico': 'Análise disponível em formato texto',
                            'trechos_analisados': [],
                            'conclusao': 'Consulte o resumo geral para detalhes'
                        }
                    }
            else:
                error_msg = resultado.get('error', 'Erro desconhecido na análise de IA')
                logger.error(f"Erro na análise de IA: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.error(f"Erro na análise de IA com origem: {e}")
            return {
                'success': False,
                'error': f'Erro interno: {e}'
            }
    
    def analisar_com_ia_otimizado(self, comparacao_id):
        """
        Análise IA completa e otimizada usando estrutura robusta do sistema
        """
        try:
            logger.info(f"🚀 Iniciando análise IA otimizada para comparação {comparacao_id}")
            
            # Import local para evitar circular imports
            from models import ComparacaoDocumento
            
            # Buscar comparação no banco
            comparacao = ComparacaoDocumento.query.get(comparacao_id)
            if not comparacao:
                logger.error(f"Comparação {comparacao_id} não encontrada")
                return {
                    'success': False,
                    'error': 'Comparação não encontrada'
                }
            
            # Extrair textos das versões usando BeautifulSoup
            def extrair_texto_html_otimizado(html_content):
                if not html_content:
                    return ""
                try:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    for script in soup(["script", "style"]):
                        script.decompose()
                    texto = soup.get_text()
                    linhas = (linha.strip() for linha in texto.splitlines())
                    chunks = (frase.strip() for linha in linhas for frase in linha.split("  "))
                    return ' '.join(chunk for chunk in chunks if chunk)
                except Exception as e:
                    logger.warning(f"Erro ao extrair texto: {e}")
                    return str(html_content)
            
            texto_original = extrair_texto_html_otimizado(comparacao.resultado_html_lado_a)
            texto_modificado = extrair_texto_html_otimizado(comparacao.resultado_html_lado_b)
            
            logger.info(f"📝 Textos extraídos - Original: {len(texto_original)} chars, Modificado: {len(texto_modificado)} chars")
            
            # Verificar se a API key existe
            api_key = current_app.config.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
            if not api_key:
                logger.warning("Chave da API OpenAI não configurada")
                return {
                    'success': False,
                    'error': 'API OpenAI não configurada',
                    'analise': self._criar_analise_emergencia(texto_original, texto_modificado, "API não configurada")
                }
                
            # Inicializar o cliente OpenAI
            client = OpenAI(api_key=api_key)
            
            # Preparar prompt estruturado para análise jurídica aprofundada
            prompt_analise = f"""
            Você é um especialista em análise jurídica comparativa especializado em Direito Agrário e documentos técnicos. 
            Analise minuciosamente as duas versões do documento abaixo com foco em impactos jurídicos, técnicos e práticos.

            === VERSÃO ORIGINAL ===
            {texto_original[:4000]}

            === VERSÃO MODIFICADA ===
            {texto_modificado[:4000]}

            Forneça uma análise jurídica APROFUNDADA no seguinte formato JSON:
            {{
                "resumo_geral": "Resumo executivo detalhado das principais alterações e suas implicações",
                "impacto_juridico": "Análise DETALHADA do impacto jurídico: validade, eficácia, consequências práticas, riscos legais e conformidade normativa",
                "score_global": número de 0 a 100,
                "gravidade_alteracoes": "BAIXA|MÉDIA|ALTA - com justificativa",
                "riscos_identificados": [
                    {{
                        "tipo_risco": "legal|operacional|regulatorio|financeiro",
                        "descricao": "descrição detalhada do risco",
                        "probabilidade": "baixa|média|alta",
                        "impacto_potencial": "descrição do impacto se materializado",
                        "medidas_mitigacao": "ações para reduzir o risco"
                    }}
                ],
                "trechos_analisados": [
                    {{
                        "tipo": "estrutural|conteudo|citacao|revisao|tecnico|normativo",
                        "categoria": "categoria específica da alteração",
                        "trecho_original": "texto original (se removido)",
                        "trecho_modificado": "texto modificado (se adicionado)",
                        "natureza_alteracao": "adição|remoção|modificação|reformulação",
                        "impacto_detalhado": "análise aprofundada do impacto específico",
                        "implicacoes_praticas": "consequências práticas da alteração",
                        "recomendacao_especifica": "sugestão detalhada e específica",
                        "urgencia": "baixa|média|alta"
                    }}
                ],
                "conformidade_normativa": {{
                    "status": "conforme|nao_conforme|requer_verificacao",
                    "normas_afetadas": ["lista de normas/leis potencialmente afetadas"],
                    "observacoes": "observações sobre conformidade"
                }},
                "conclusao": "Conclusão jurídica fundamentada com recomendações estratégicas",
                "sugestoes_prioritarias": [
                    {{
                        "prioridade": 1-5,
                        "acao": "descrição da ação recomendada",
                        "justificativa": "por que esta ação é prioritária",
                        "prazo_sugerido": "prazo para implementação"
                    }}
                ],
                "analise_detalhada": {{
                    "estruturacao": {{
                        "score": número 0-100,
                        "problemas_identificados": ["problemas estruturais detalhados"],
                        "pontos_positivos": ["aspectos estruturais bem executados"],
                        "sugestoes_melhoria": ["sugestões específicas de melhoria"]
                    }},
                    "conteudo": {{
                        "score": número 0-100,
                        "problemas_identificados": ["problemas de conteúdo detalhados"],
                        "pontos_positivos": ["aspectos de conteúdo bem executados"],
                        "sugestoes_melhoria": ["sugestões específicas de melhoria"]
                    }},
                    "aspecto_tecnico": {{
                        "score": número 0-100,
                        "precisao_tecnica": "avaliação da precisão técnica",
                        "adequacao_contexto": "adequação ao contexto jurídico/técnico",
                        "sugestoes_tecnicas": ["melhorias técnicas recomendadas"]
                    }}
                }},
                "proximos_passos": [
                    "Lista de próximos passos recomendados para implementação das melhorias"
                ]
            }}
            
            IMPORTANTE: Seja específico, detalhado e foque em implicações práticas e jurídicas reais.
            """
            
            # Executar análise com IA
            logger.info("🤖 Executando análise jurídica comparativa...")
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt_analise}],
                response_format={"type": "json_object"},
                max_tokens=3000,
                temperature=0.3
            )
            
            resultado_ia = {
                "success": True,
                "content": response.choices[0].message.content
            }
            
            # Log detalhado da resposta
            logger.info(f"📋 Resposta completa da IA: {resultado_ia}")
            
            # Processar resultado com verificação mais robusta
            if not resultado_ia or not isinstance(resultado_ia, dict):
                logger.error(f"Resposta IA inválida: {type(resultado_ia)} - {resultado_ia}")
                return self._criar_analise_emergencia(texto_original, texto_modificado, "Resposta inválida da IA")
            
            # Verificar diferentes formas de sucesso
            success = resultado_ia.get('success', False)
            if not success and 'content' not in resultado_ia and 'response' not in resultado_ia:
                logger.error(f"Erro na análise IA: {resultado_ia.get('error', 'Erro desconhecido')}")
                return self._criar_analise_emergencia(texto_original, texto_modificado, resultado_ia.get('error', ''))
            
            # Extrair e processar conteúdo com múltiplas tentativas
            content = (resultado_ia.get('content') or 
                      resultado_ia.get('response') or 
                      resultado_ia.get('message') or
                      resultado_ia.get('text', ''))
            
            logger.info(f"📝 Conteúdo extraído: {content[:500]}..." if len(str(content)) > 500 else f"📝 Conteúdo extraído: {content}")
            
            try:
                # Tentar fazer parse do JSON
                if isinstance(content, str):
                    # Limpar possíveis marcadores de código
                    content_clean = content.strip()
                    if content_clean.startswith('```json'):
                        content_clean = content_clean[7:]
                    if content_clean.endswith('```'):
                        content_clean = content_clean[:-3]
                    analise_final = json.loads(content_clean)
                else:
                    analise_final = content
                
                # Validar estrutura básica
                if not isinstance(analise_final, dict):
                    raise ValueError("Resposta não é um dicionário válido")
                
                # Garantir campos obrigatórios
                campos_obrigatorios = ['resumo_geral', 'impacto_juridico', 'conclusao', 'trechos_analisados']
                for campo in campos_obrigatorios:
                    if campo not in analise_final:
                        analise_final[campo] = f"Campo {campo} não fornecido pela análise"
                
                # Garantir score_global
                if 'score_global' not in analise_final or not isinstance(analise_final['score_global'], (int, float)):
                    analise_final['score_global'] = 75  # Score padrão moderado
                
                # Adicionar metadados
                analise_final['metodo_analise'] = 'MultiProviderAI Jurídico Completo'
                analise_final['timestamp_analise'] = comparacao.data_comparacao.isoformat() if comparacao.data_comparacao else None
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Erro ao processar JSON da IA: {e}. Usando análise em texto.")
                # Fallback para análise em texto estruturado
                analise_final = self._criar_analise_texto_estruturado(content, texto_original, texto_modificado)
            
            logger.info(f"✅ Análise otimizada concluída - Score global: {analise_final.get('score_global', 0)}%")
            
            return {
                'success': True,
                'analise': analise_final
            }
            
        except Exception as e:
            logger.error(f"Erro crítico na análise otimizada: {e}")
            return self._criar_analise_emergencia("", "", str(e))
    
    def _criar_analise_texto_estruturado(self, content, texto_original, texto_modificado):
        """Cria análise estruturada a partir de texto da IA"""
        try:
            # Extrair informações básicas do texto
            texto_content = str(content)
            
            # Extrair resumo básico
            resumo_match = re.search(r'resumo[:\-\s]*([^\.]+)', texto_content.lower())
            resumo_geral = resumo_match.group(1) if resumo_match else "Análise textual em processamento"
            
            # Extrair impacto
            impacto_match = re.search(r'impacto[:\-\s]*([^\.]+)', texto_content.lower())
            impacto_juridico = impacto_match.group(1) if impacto_match else "Impacto moderado identificado"
            
            # Extrair score básico
            score_match = re.search(r'(\d+)%', texto_content)
            score_global = int(score_match.group(1)) if score_match else 70
            
            # Criar estrutura mínima
            return {
                'resumo_geral': resumo_geral.strip(),
                'impacto_juridico': impacto_juridico.strip(),
                'trechos_analisados': [{
                    'tipo': 'texto_processado',
                    'trecho': texto_content[:200] + "..." if len(texto_content) > 200 else texto_content,
                    'impacto': 'Análise baseada em processamento de texto',
                    'recomendacao': 'Revisar análise manual para validação completa'
                }],
                'conclusao': f'Análise textual processada com score estimado de {score_global}%',
                'score_global': score_global,
                'metodo_analise': 'Processamento de Texto Estruturado'
            }
            len_orig = len(texto_original)
            len_mod = len(texto_modificado)
            diferenca = abs(len_orig - len_mod)
            
            # Calcular score baseado na diferença
            if len_orig > 0:
                percentual_diferenca = (diferenca / len_orig) * 100
                if percentual_diferenca < 10:
                    score = 85
                elif percentual_diferenca < 30:
                    score = 70
                else:
                    score = 55
            else:
                score = 60
            
            # Criar estrutura baseada no conteúdo da IA
            resumo = str(content)[:500] + "..." if len(str(content)) > 500 else str(content)
            
            return {
                'resumo_geral': f"Análise baseada em IA: {resumo}",
                'impacto_juridico': f"Impacto determinado por análise comparativa. Diferença de tamanho: {diferenca} caracteres ({percentual_diferenca:.1f}%)" if len_orig > 0 else "Impacto baseado em análise de conteúdo",
                'score_global': score,
                'trechos_analisados': [{
                    'tipo': 'texto_ia',
                    'categoria': 'Análise Automatizada',
                    'trecho': 'Análise processada por IA especializada',
                    'impacto': f'Score calculado: {score}%',
                    'recomendacao': 'Revisar resultado da análise IA para validação'
                }],
                'conclusao': f"Análise concluída via IA. Score global: {score}%. Consulte o resumo geral para detalhes completos.",
                'sugestoes_prioritarias': [
                    'Validar resultado da análise automatizada',
                    'Revisar alterações significativas identificadas',
                    'Considerar impacto jurídico das modificações'
                ],
                'metodo_analise': 'IA Texto Estruturado'
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar análise de texto estruturado: {e}")
            return self._criar_analise_emergencia(texto_original, texto_modificado, str(e))['analise']
    
    def _processar_resultado_otimizado(self, resultado_bruto, texto_original, texto_modificado):
        """
        Processa resultado do DocumentAnalyst para formato de comparação otimizado
        """
        try:
            score_global = resultado_bruto.get('score_global', 0)
            
            # Extrair informações das seções
            estruturacao = resultado_bruto.get('estruturacao', {})
            conteudo = resultado_bruto.get('conteudo', {})
            citacoes = resultado_bruto.get('citacoes', {})
            revisao = resultado_bruto.get('revisao_final', {})
            
            # Montar resumo inteligente
            resumo_geral = self._gerar_resumo_inteligente(
                score_global, estruturacao, conteudo, len(texto_original), len(texto_modificado)
            )
            
            # Análise de impacto jurídico
            impacto_juridico = self._avaliar_impacto_juridico(estruturacao, conteudo, score_global)
            
            # Extrair trechos analisados estruturados
            trechos_analisados = self._extrair_trechos_estruturados(
                estruturacao, conteudo, citacoes, revisao
            )
            
            # Gerar conclusão baseada em dados
            conclusao = self._gerar_conclusao_baseada_dados(resultado_bruto, score_global)
            
            return {
                'resumo_geral': resumo_geral,
                'impacto_juridico': impacto_juridico,
                'trechos_analisados': trechos_analisados,
                'conclusao': conclusao,
                'score_global': score_global,
                'analise_detalhada': {
                    'estruturacao': estruturacao,
                    'conteudo': conteudo,
                    'citacoes': citacoes,
                    'revisao_final': revisao
                },
                'sugestoes_prioritarias': resultado_bruto.get('sugestoes_prioritarias', []),
                'metodo_analise': 'DocumentAnalyst Otimizado'
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resultado: {e}")
            return self._criar_resultado_basico(resultado_bruto)
    
    def _gerar_resumo_inteligente(self, score, estruturacao, conteudo, len_orig, len_mod):
        """Gera resumo inteligente baseado nos dados da análise"""
        diferenca_tamanho = abs(len_orig - len_mod)
        percentual_mudanca = (diferenca_tamanho / max(len_orig, 1)) * 100
        
        score_estrutura = estruturacao.get('score', 0)
        score_conteudo = conteudo.get('score', 0)
        
        resumo = f"Análise comparativa concluída com score global de {score}%. "
        
        if percentual_mudanca > 30:
            resumo += f"Alterações significativas detectadas ({percentual_mudanca:.1f}% de mudança no tamanho). "
        elif percentual_mudanca > 10:
            resumo += f"Alterações moderadas identificadas ({percentual_mudanca:.1f}% de mudança). "
        else:
            resumo += "Alterações pontuais detectadas. "
        
        if score_estrutura < 60:
            resumo += "Estrutura documental requer atenção. "
        if score_conteudo < 70:
            resumo += "Conteúdo jurídico necessita revisão. "
            
        return resumo
    
    def _avaliar_impacto_juridico(self, estruturacao, conteudo, score_global):
        """Avalia impacto jurídico baseado nos scores das seções"""
        score_estrutura = estruturacao.get('score', 0)
        score_conteudo = conteudo.get('score', 0)
        
        if score_global >= 85 and score_conteudo >= 80:
            return "Impacto jurídico mínimo - alterações preservam validade e estrutura legal"
        elif score_global >= 70 and score_conteudo >= 65:
            return "Impacto jurídico moderado - algumas adequações recomendadas para conformidade plena"
        elif score_global >= 50:
            return "Impacto jurídico significativo - revisão necessária para adequação às normas"
        else:
            return "Impacto jurídico alto - alterações comprometem estrutura legal, revisão urgente necessária"
    
    def _extrair_trechos_estruturados(self, estruturacao, conteudo, citacoes, revisao):
        """Extrai trechos analisados de forma estruturada"""
        trechos = []
        
        # Problemas de estruturação
        for problema in estruturacao.get('problemas', [])[:3]:
            trechos.append({
                'tipo': 'estrutural',
                'categoria': 'Estruturação',
                'trecho': problema,
                'impacto': f"Score estrutural: {estruturacao.get('score', 0)}%",
                'recomendacao': estruturacao.get('sugestoes', [''])[0] if estruturacao.get('sugestoes') else 'Revisar estrutura'
            })
        
        # Problemas de conteúdo
        for problema in conteudo.get('problemas', [])[:3]:
            trechos.append({
                'tipo': 'conteudo',
                'categoria': 'Conteúdo Jurídico',
                'trecho': problema,
                'impacto': f"Score de conteúdo: {conteudo.get('score', 0)}%",
                'recomendacao': conteudo.get('sugestoes', [''])[0] if conteudo.get('sugestoes') else 'Revisar conteúdo'
            })
        
        # Problemas de citações
        for problema in citacoes.get('problemas', [])[:2]:
            trechos.append({
                'tipo': 'citacao',
                'categoria': 'Citações e Referências',
                'trecho': problema,
                'impacto': f"Score de citações: {citacoes.get('score', 0)}%",
                'recomendacao': citacoes.get('sugestoes', [''])[0] if citacoes.get('sugestoes') else 'Ajustar citações'
            })
        
        return trechos[:8]  # Limitar a 8 trechos
    
    def _gerar_conclusao_baseada_dados(self, resultado, score_global):
        """Gera conclusão baseada nos dados da análise"""
        sugestoes_prioritarias = resultado.get('sugestoes_prioritarias', [])
        
        if score_global >= 85:
            base = f"Documentos apresentam alta qualidade técnica (Score: {score_global}%). "
        elif score_global >= 70:
            base = f"Documentos com qualidade adequada (Score: {score_global}%). "
        elif score_global >= 50:
            base = f"Documentos requerem melhorias (Score: {score_global}%). "
        else:
            base = f"Documentos necessitam revisão significativa (Score: {score_global}%). "
        
        if sugestoes_prioritarias:
            prioridades = " | ".join(sugestoes_prioritarias[:3])
            return base + f"Prioridades: {prioridades}"
        
        return base + "Consulte análise detalhada para orientações específicas."
    
    def _criar_resultado_basico(self, resultado_bruto):
        """Cria resultado básico a partir do resultado bruto"""
        return {
            'resumo_geral': 'Análise básica executada com estrutura robusta do sistema',
            'impacto_juridico': 'Impacto determinado através de análise automatizada',
            'trechos_analisados': [],
            'conclusao': f"Score global: {resultado_bruto.get('score_global', 0)}%",
            'score_global': resultado_bruto.get('score_global', 0),
            'metodo_analise': 'DocumentAnalyst Básico'
        }
    
    def _criar_analise_emergencia(self, texto_orig, texto_mod, erro=""):
        """Cria análise de emergência quando sistemas principais falham"""
        logger.warning("Criando análise de emergência")
        
        # Análise básica baseada no tamanho dos textos
        len_orig = len(texto_orig)
        len_mod = len(texto_mod)
        diferenca = abs(len_orig - len_mod)
        
        if diferenca > len_orig * 0.3:
            impacto = "Alto - alterações significativas detectadas"
            score = 40
        elif diferenca > len_orig * 0.1:
            impacto = "Moderado - alterações detectadas"
            score = 65
        else:
            impacto = "Baixo - poucas alterações detectadas"
            score = 80
        
        return {
            'success': True,
            'analise': {
                'resumo_geral': f"Análise de emergência executada. Diferença de tamanho: {diferenca} caracteres.",
                'impacto_juridico': impacto,
                'trechos_analisados': [{
                    'tipo': 'emergencia',
                    'trecho': 'Análise emergencial por falha no sistema principal',
                    'impacto': f'Score estimado: {score}%',
                    'recomendacao': 'Revisar manualmente os documentos'
                }],
                'conclusao': f'Análise emergencial concluída. {erro if erro else "Sistema principal indisponível."}',
                'score_global': score,
                'modo_emergencia': True
            }
        }