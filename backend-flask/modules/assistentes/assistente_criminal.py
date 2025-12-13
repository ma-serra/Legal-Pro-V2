"""
Assistente Jurídico Especializado em Direito Criminal
Integrado com base vetorial criminal e busca semântica avançada
"""
import logging
import re
from typing import Dict, List, Any
from .assistente_base import AssistenteBase

logger = logging.getLogger(__name__)

class AssistenteCriminal(AssistenteBase):
    """Assistente especializado em Direito Criminal"""
    
    def __init__(self):
        super().__init__("criminal")
        self.nome = "Assistente Criminal"
        self.descricao = "Especialista em Direito Penal e Processo Penal"
        self.areas_especializacao = [
            "Código Penal",
            "Código de Processo Penal", 
            "Tribunal do Júri",
            "Execução Penal",
            "Lei de Drogas",
            "Jurisprudência Criminal"
        ]
        
        # Prompts especializados fundamentados nos códigos penais
        self.prompts_especializados = {
            "analise_tipificacao": """
            Especialista em tipificação penal - análise técnica fundamentada:

            ESTRUTURA TÉCNICA OBRIGATÓRIA:

            I. ADEQUAÇÃO TÍPICA (CP art. específico):
            - Dispositivo legal aplicável com transcrição literal
            - Elementares objetivas e subjetivas do tipo
            - Subsunção fática aos elementos normativos

            II. ANÁLISE DOGMÁTICA:
            - Estrutura do tipo: básico, qualificado, privilegiado
            - Elemento subjetivo: dolo, culpa, especial fim de agir
            - Consumação, tentativa, iter criminis

            III. APLICAÇÃO PENAL:
            - Pena cominada (mínimo/máximo)
            - Causas de aumento/diminuição (frações aplicáveis)
            - Regime inicial: arts. 33, §2º e §3º CP

            Fundamentação exclusiva no Código Penal. Citação obrigatória do dispositivo antes da análise.
            """,
            
            "analise_processual": """
            Especialista processual penal - análise técnica procedimental:

            ESTRUTURA PROCESSUAL OBRIGATÓRIA:

            I. COMPETÊNCIA E PROCEDIMENTO (CPP):
            - Determinação da competência material/territorial
            - Procedimento aplicável (ordinário: 394-405; sumário: 531-540; sumaríssimo: Lei 9.099/95)
            - Rito especial se aplicável

            II. PRAZOS PROCESSUAIS:
            - Oferecimento denúncia: art. 46 CPP (preso) / art. 24 Lei 9.099/95
            - Defesa prévia: art. 396-A CPP
            - Alegações finais: art. 403 CPP
            - Recursos: arts. 593-667 CPP

            III. MEDIDAS CAUTELARES:
            - Prisão preventiva: requisitos art. 312 CPP
            - Medidas alternativas: rol art. 319 CPP
            - Fiança: arts. 321-350 CPP

            Citação obrigatória do dispositivo CPP específico precedendo a análise técnica.
            """,
            
            "tribunal_juri": """
            Especialista Tribunal do Júri - análise técnica procedimental especializada:

            ESTRUTURA BIFÁSICA OBRIGATÓRIA:

            I. COMPETÊNCIA CONSTITUCIONAL (Art. 5º, XXXVIII CF):
            - Crimes dolosos contra a vida: homicídio (121), induzimento/auxílio suicídio (122), infanticídio (123), aborto (124-128) CP
            - Análise conexão/continência: arts. 76-82 CPP
            - Desclassificação própria/imprópria

            II. PRIMEIRA FASE - JUDICIUM ACCUSATIONIS (arts. 406-421 CPP):
            - Decisões possíveis: pronúncia (413), impronúncia (414), despronúncia (415), absolvição sumária (415)
            - Requisitos pronúncia: materialidade, indícios suficientes autoria
            - Recurso cabível: RESE (art. 581, IV CPP)

            III. SEGUNDA FASE - JUDICIUM CAUSAE (arts. 422-497 CPP):
            - Quesitos obrigatórios: materialidade, autoria, absolutorias (defensivas)
            - Veredicto e dosimetria judicial
            - Recursos: apelação (593, I), embargos infringentes (609, parágrafo único)

            Fundamentação técnica nos arts. 406-497 CPP com citação específica precedente.
            """
        }
    
    def processar_consulta(self, mensagem: str, contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa consulta criminal com busca semântica avançada"""
        if not contexto:
            contexto = {}
        
        # Identificar tipo de consulta criminal
        tipo_consulta = self._identificar_tipo_consulta(mensagem)
        contexto['tipo_consulta'] = tipo_consulta
        
        # Adicionar prompt especializado
        if tipo_consulta in self.prompts_especializados:
            contexto['prompt_especializado'] = self.prompts_especializados[tipo_consulta]
        
        # Executar busca semântica avançada
        documentos_relevantes = self._busca_semantica_avancada(mensagem)
        contexto['documentos_especializados'] = documentos_relevantes
        
        # Chamar método da classe pai com contexto enriquecido
        return super().processar_consulta(mensagem, contexto)
    
    def _identificar_tipo_consulta(self, mensagem: str) -> str:
        """Identifica o tipo de consulta criminal"""
        mensagem_lower = mensagem.lower()
        
        if any(palavra in mensagem_lower for palavra in ['tipifica', 'crime', 'delito', 'artigo', 'pena']):
            return 'analise_tipificacao'
        elif any(palavra in mensagem_lower for palavra in ['processo', 'prazo', 'recurso', 'nulidade', 'procedimento']):
            return 'analise_processual'
        elif any(palavra in mensagem_lower for palavra in ['júri', 'juri', 'doloso contra vida', 'homicídio', 'quesito']):
            return 'tribunal_juri'
        else:
            return 'consulta_geral'
    
    def _busca_semantica_avancada(self, mensagem: str) -> List[Dict]:
        """Executa busca semântica avançada e consulta direta aos códigos"""
        documentos_encontrados = []
        
        try:
            # 1. Consulta direta aos arquivos dos códigos (prioritária)
            from modules.consulta_direta_codigos import ConsultaDiretaCodigos
            consultor = ConsultaDiretaCodigos()
            
            # Busca artigos específicos mencionados
            artigos_mencionados = re.findall(r'art\.?\s*(\d+)', mensagem, re.IGNORECASE)
            for artigo in artigos_mencionados:
                artigos_diretos = consultor.buscar_artigo_especifico(artigo)
                documentos_encontrados.extend(artigos_diretos)
            
            # Busca por termos relevantes nos códigos
            termos_juridicos = consultor._extrair_termos_juridicos(mensagem)
            for termo in termos_juridicos[:3]:  # Limita a 3 termos principais
                resultados_termo = consultor.buscar_por_termo(termo, limite=3)
                documentos_encontrados.extend(resultados_termo)
            
            # 2. Busca semântica como complemento
            try:
                from modules.busca_semantica_penal import BuscaSemanticaPenal
                busca_engine = BuscaSemanticaPenal()
                resultado_semantico = busca_engine.buscar(mensagem, limite=5)
                documentos_semanticos = resultado_semantico.get('resultados', [])
                documentos_encontrados.extend(documentos_semanticos)
            except Exception as e_semantica:
                logger.warning(f"Busca semântica falhou, usando apenas consulta direta: {e_semantica}")
            
            # Remove duplicatas e ordena por relevância
            documentos_unicos = self._remover_duplicatas_documentos(documentos_encontrados)
            return documentos_unicos[:10]  # Limita a 10 documentos mais relevantes
            
        except Exception as e:
            logger.error(f"Erro na busca avançada: {e}")
            # Fallback para busca tradicional
            return self._busca_tradicional_fallback(mensagem)
    
    def _busca_tradicional_fallback(self, mensagem: str) -> List[Dict]:
        """Busca tradicional como fallback"""
        try:
            import psycopg2
            import os
            
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            cursor = conn.cursor()
            
            # Busca simples por texto
            cursor.execute("""
                SELECT documento, artigo, titulo, conteudo, categoria, fonte
                FROM base_vetorial_universal 
                WHERE fonte IN ('Código Penal', 'Código de Processo Penal')
                AND to_tsvector('portuguese', conteudo) @@ plainto_tsquery('portuguese', %s)
                ORDER BY ts_rank(to_tsvector('portuguese', conteudo), plainto_tsquery('portuguese', %s)) DESC
                LIMIT 10
            """, (mensagem, mensagem))
            
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()
            
            docs = []
            for row in resultados:
                docs.append({
                    'documento': row[0],
                    'artigo': row[1],
                    'titulo': row[2],
                    'conteudo': row[3],
                    'categoria': row[4],
                    'fonte': row[5]
                })
            
            return docs
            
        except Exception as e:
            logger.error(f"Erro na busca tradicional: {e}")
            return []
    
    def _remover_duplicatas_documentos(self, documentos: List[Dict]) -> List[Dict]:
        """Remove documentos duplicados e ordena por relevância"""
        vistos = set()
        unicos = []
        
        for doc in documentos:
            # Cria chave única baseada na fonte e artigo
            chave = f"{doc.get('fonte', 'desconhecida')}_{doc.get('artigo', 'sem_artigo')}"
            
            if chave not in vistos:
                vistos.add(chave)
                # Garante que tenha score para ordenação
                if 'relevancia' not in doc and 'score_final' not in doc:
                    doc['relevancia'] = 0.5  # Score padrão para documentos sem score
                unicos.append(doc)
        
        # Ordena por relevância (score_final > relevancia > 0.5 padrão)
        return sorted(unicos, key=lambda x: x.get('score_final', x.get('relevancia', 0.5)), reverse=True)
    
    def _preparar_contexto(self, mensagem: str, documentos: List[Dict], contexto_extra: Dict = None) -> str:
        """Prepara contexto específico fundamentado nos códigos penais"""
        contexto_base = f"""
VOCÊ É UM ASSISTENTE JURÍDICO ESPECIALIZADO EM DIREITO PENAL E PROCESSO PENAL BRASILEIRO.

## DIRETRIZES FUNDAMENTAIS OBRIGATÓRIAS:

### 1. FONTES LEGAIS EXCLUSIVAS:
- Código Penal (Decreto-Lei 2.848/1940) - FONTE PRIMÁRIA
- Código de Processo Penal (Decreto-Lei 3.689/1941) - FONTE PRIMÁRIA
- Cite SEMPRE o artigo específico antes de qualquer explicação
- NUNCA invente ou presuma dispositivos legais

### 2. ESTRUTURA DE RESPOSTA OBRIGATÓRIA:
**🔍 ANÁLISE LEGAL:**
- Artigos do Código Penal aplicáveis (texto integral)
- Artigos do CPP relevantes (procedimento)
- Elementos do tipo penal identificados

**⚖️ FUNDAMENTAÇÃO:**
- Interpretação jurídica dos dispositivos
- Causas de aumento/diminuição de pena
- Excludentes de ilicitude/culpabilidade

**📋 PROCEDIMENTO:**
- Rito processual aplicável (CPP)
- Prazos e competência
- Medidas cautelares cabíveis

**🎯 ORIENTAÇÃO PRÁTICA:**
- Estratégias processuais
- Precedentes consolidados
- Pontos críticos de atenção

### 3. ESPECIALIDADES:
- Tipificação penal e dosimetria
- Procedimentos do CPP (ordinário, sumário, júri)
- Prisões e liberdades
- Execução penal
- Recursos criminais

CONSULTA DO USUÁRIO:
{mensagem}

DOCUMENTOS RELEVANTES DOS CÓDIGOS PENAIS:
"""
        
        for i, doc in enumerate(documentos[:5], 1):
            fonte = doc.get('fonte', 'Documento Criminal')
            artigo = doc.get('artigo', '')
            conteudo = doc.get('conteudo', '')[:400]
            contexto_base += f"\n{i}. {fonte} {artigo}: {conteudo}...\n"
        
        if contexto_extra and 'prompt_especializado' in contexto_extra:
            contexto_base += f"\n\nINSTRUÇÕES ESPECÍFICAS:\n{contexto_extra['prompt_especializado']}"
        
        contexto_base += """

DIRETRIZES PARA RESPOSTAS:
- Base suas respostas EXCLUSIVAMENTE na legislação e jurisprudência brasileira
- Cite sempre os artigos específicos (ex: "Art. 121, CP" ou "Art. 395, CPP")
- Se consultar jurisprudência, mencione o tribunal (STF, STJ, TJSP, etc.)
- Para dúvidas processuais, sempre considere o CPP de 2008 (Lei 11.719/2008)
- Em caso de conflito de leis, aplique os princípios da especialidade e posterioridade
- Se não houver informação suficiente na base, seja transparente sobre isso
- Mantenha linguagem técnica mas acessível
"""
        
        return contexto_base
    
    def obter_templates_area(self) -> List[Dict]:
        """Retorna templates específicos da área criminal"""
        return [
            {
                'id': 'denuncia_criminal',
                'nome': 'Denúncia Criminal',
                'categoria': 'Peças Processuais',
                'descricao': 'Template para denúncia do Ministério Público',
                'campos': ['qualificacao_reu', 'fatos', 'tipificacao', 'provas', 'pedidos']
            },
            {
                'id': 'defesa_previa',
                'nome': 'Defesa Prévia',
                'categoria': 'Defesa',
                'descricao': 'Resposta à acusação (Art. 396, CPP)',
                'campos': ['qualificacao_cliente', 'tese_defensiva', 'preliminares', 'merito']
            },
            {
                'id': 'alegacoes_finais',
                'nome': 'Alegações Finais',
                'categoria': 'Defesa',
                'descricao': 'Memoriais finais da defesa',
                'campos': ['sintese_fatos', 'tese_juridica', 'analise_provas', 'pedidos']
            },
            {
                'id': 'habeas_corpus',
                'nome': 'Habeas Corpus',
                'categoria': 'Remédios Constitucionais',
                'descricao': 'Writ constitucional para liberdade de locomoção',
                'campos': ['paciente', 'coator', 'constrangimento', 'fundamentacao', 'pedido']
            },
            {
                'id': 'apelacao_criminal',
                'nome': 'Apelação Criminal',
                'categoria': 'Recursos',
                'descricao': 'Recurso ordinário contra sentença',
                'campos': ['sentenca_recorrida', 'razoes_recurso', 'fundamentacao', 'pedidos']
            }
        ]
    
    def gerar_documento(self, template_id: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Gera documento criminal baseado em template"""
        templates = {template['id']: template for template in self.obter_templates_area()}
        
        if template_id not in templates:
            return {
                'sucesso': False,
                'erro': f'Template {template_id} não encontrado na área criminal'
            }
        
        template = templates[template_id]
        
        try:
            # Validar campos obrigatórios
            campos_obrigatorios = template.get('campos', [])
            campos_faltantes = [campo for campo in campos_obrigatorios if campo not in dados]
            
            if campos_faltantes:
                return {
                    'sucesso': False,
                    'erro': f'Campos obrigatórios não preenchidos: {", ".join(campos_faltantes)}'
                }
            
            # Gerar documento usando IA
            prompt_geracao = f"""
Gere um documento jurídico do tipo "{template['nome']}" com base nos seguintes dados:

DADOS FORNECIDOS:
{dados}

INSTRUÇÕES:
- Use linguagem jurídica formal e técnica
- Siga as normas do processo penal brasileiro
- Inclua fundamentação legal adequada
- Estruture o documento de forma profissional
- Cite artigos específicos quando aplicável

ESTRUTURA PARA {template['nome'].upper()}:
"""
            
            if template_id == 'denuncia_criminal':
                prompt_geracao += """
1. Cabeçalho com identificação do Ministério Público
2. Qualificação do denunciado
3. Narrativa dos fatos
4. Tipificação penal
5. Análise das provas
6. Pedidos (recebimento da denúncia, citação, etc.)
"""
            elif template_id == 'defesa_previa':
                prompt_geracao += """
1. Cabeçalho com identificação da defesa
2. Qualificação do acusado
3. Preliminares (se houver)
4. Mérito (tese defensiva)
5. Dos pedidos
"""
            
            # Usar IA para gerar o documento
            resposta_ia = self._gerar_resposta_ia("", prompt_geracao)
            
            return {
                'sucesso': True,
                'documento': resposta_ia,
                'template_usado': template['nome'],
                'tipo': template['categoria']
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar documento criminal: {e}")
            return {
                'sucesso': False,
                'erro': f'Erro na geração do documento: {str(e)}'
            }
    def processar_consulta_completa(self, pergunta: str, contexto: str = "", modelo: str = "openai") -> dict:
        """Método obrigatório para processar consultas"""
        try:
            # Implementação básica
            return {
                "resposta": f"Consulta sobre {self.__class__.__name__}: {pergunta}",
                "area": getattr(self, 'area_juridica', 'geral'),
                "status": "sucesso"
            }
        except Exception as e:
            return {
                "resposta": "Erro no processamento",
                "status": "erro",
                "erro": str(e)
            }
