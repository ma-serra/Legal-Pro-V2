"""
Script para cadastrar os agentes básicos do sistema multi-agente no banco de dados
"""
import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Obtém conexão com o banco de dados"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL não encontrada nas variáveis de ambiente")
        return None, None
    
    engine = create_engine(database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def cadastrar_agentes_basicos():
    """Cadastra os agentes básicos do sistema multi-agente"""
    
    # Definição dos agentes básicos
    agentes_basicos = [
        {
            'nome': 'Extrator',
            'classe': 'ExtratorAgent',
            'descricao': 'Agente responsável por extrair informações estruturadas de documentos jurídicos, identificando elementos-chave como partes, datas, valores e cláusulas principais.',
            'template_prompt': '''Você é um especialista em extração de informações jurídicas. Analise o documento fornecido e extraia as seguintes informações estruturadas:

1. PARTES ENVOLVIDAS:
   - Contratante/Requerente
   - Contratado/Requerido
   - Testemunhas (se houver)

2. DADOS TEMPORAIS:
   - Data do documento
   - Prazos mencionados
   - Vigência do contrato (se aplicável)

3. VALORES E QUANTIAS:
   - Valores monetários
   - Percentuais
   - Quantidades mencionadas

4. ELEMENTOS JURÍDICOS:
   - Tipo de documento
   - Cláusulas principais
   - Obrigações das partes
   - Direitos estabelecidos

5. INFORMAÇÕES COMPLEMENTARES:
   - Endereços
   - Documentos de identificação
   - Referências legais

Extraia apenas informações explicitamente presentes no texto. Forneça o resultado em formato JSON estruturado.

DOCUMENTO A ANALISAR:
{input}''',
            'base_vetorial': 'agentes_basicos',
            'ativo': True,
            'modelo_ai': 'gpt-4o',
            'temperatura': 0.1,
            'top_p': 0.9,
            'max_tokens': 2000,
            'capacidades': {
                'tipo': 'extracao',
                'especialidades': ['extração de dados', 'estruturação de informações', 'identificação de entidades'],
                'formatos_saida': ['json', 'texto estruturado'],
                'precisao': 'alta'
            }
        },
        {
            'nome': 'Classificador',
            'classe': 'ClassificadorAgent',
            'descricao': 'Agente responsável por classificar documentos jurídicos em categorias específicas e identificar a área do direito mais relevante.',
            'template_prompt': '''Você é um especialista em classificação de documentos jurídicos. Analise o documento fornecido e realize a classificação nas seguintes dimensões:

1. TIPO DE DOCUMENTO:
   - Contrato (especificar tipo)
   - Petição (inicial, recurso, etc.)
   - Parecer jurídico
   - Decisão judicial
   - Outro (especificar)

2. ÁREA DO DIREITO:
   - Direito Civil
   - Direito Empresarial
   - Direito do Trabalho
   - Direito Penal
   - Direito Tributário
   - Direito Administrativo
   - Outras áreas

3. COMPLEXIDADE:
   - Baixa (documentos simples)
   - Média (documentos com múltiplas cláusulas)
   - Alta (documentos complexos com questões especializadas)

4. URGÊNCIA:
   - Baixa (sem prazos críticos)
   - Média (prazos de médio prazo)
   - Alta (prazos urgentes)

5. RISCO JURÍDICO:
   - Baixo
   - Médio
   - Alto

Para cada categoria, forneça uma pontuação de 0 a 10 e justifique brevemente sua classificação.

DOCUMENTO A CLASSIFICAR:
{input}''',
            'base_vetorial': 'agentes_basicos',
            'ativo': True,
            'modelo_ai': 'gpt-4o',
            'temperatura': 0.2,
            'top_p': 0.9,
            'max_tokens': 1500,
            'capacidades': {
                'tipo': 'classificacao',
                'especialidades': ['categorização jurídica', 'análise de complexidade', 'avaliação de risco'],
                'criterios': ['tipo documento', 'área direito', 'complexidade', 'urgência', 'risco'],
                'precisao': 'alta'
            }
        },
        {
            'nome': 'Analisador',
            'classe': 'AnalisadorAgent',
            'descricao': 'Agente responsável por realizar análise jurídica detalhada do documento, identificando pontos críticos e questões legais relevantes.',
            'template_prompt': '''Você é um advogado especialista com ampla experiência em análise jurídica. Realize uma análise completa e detalhada do documento fornecido:

1. ANÁLISE ESTRUTURAL:
   - Adequação formal do documento
   - Completude das informações
   - Conformidade com padrões legais

2. ANÁLISE SUBSTANCIAL:
   - Validade das cláusulas
   - Equilíbrio entre as partes
   - Pontos de atenção jurídica

3. RISCOS IDENTIFICADOS:
   - Cláusulas ambíguas
   - Possíveis nulidades
   - Vulnerabilidades legais
   - Riscos contratuais

4. CONFORMIDADE LEGAL:
   - Adequação à legislação vigente
   - Compliance regulatório
   - Aspectos tributários (se aplicável)

5. RECOMENDAÇÕES:
   - Melhorias sugeridas
   - Cláusulas adicionais necessárias
   - Ações preventivas
   - Próximos passos

6. PRECEDENTES E JURISPRUDÊNCIA:
   - Casos similares relevantes
   - Tendências jurisprudenciais
   - Súmulas aplicáveis

Forneça uma análise técnica fundamentada com citações legais quando aplicável.

DOCUMENTO PARA ANÁLISE:
{input}''',
            'base_vetorial': 'agentes_basicos',
            'ativo': True,
            'modelo_ai': 'gpt-4o',
            'temperatura': 0.3,
            'top_p': 0.9,
            'max_tokens': 3000,
            'capacidades': {
                'tipo': 'analise',
                'especialidades': ['análise jurídica', 'identificação de riscos', 'conformidade legal'],
                'profundidade': 'detalhada',
                'fundamentacao': 'legal'
            }
        },
        {
            'nome': 'Sintetizador',
            'classe': 'SintetizadorAgent',
            'descricao': 'Agente responsável por sintetizar todas as análises anteriores em um resultado consolidado e coerente.',
            'template_prompt': '''Você é um especialista em síntese jurídica. Com base nas análises anteriores realizadas pelos outros agentes, elabore uma síntese consolidada e coerente:

1. RESUMO EXECUTIVO:
   - Natureza do documento
   - Principais conclusões
   - Pontos críticos identificados

2. CONSOLIDAÇÃO DAS ANÁLISES:
   - Informações extraídas (síntese dos dados)
   - Classificação final
   - Análise jurídica consolidada

3. SÍNTESE DE RISCOS:
   - Principais riscos identificados
   - Nível de criticidade
   - Impactos potenciais

4. RECOMENDAÇÕES PRIORITÁRIAS:
   - Ações imediatas necessárias
   - Melhorias recomendadas
   - Medidas preventivas

5. CONCLUSÃO GERAL:
   - Avaliação global do documento
   - Viabilidade jurídica
   - Recomendação final

A síntese deve ser clara, objetiva e tecnicamente precisa, integrando harmoniosamente todas as análises anteriores.

DADOS PARA SÍNTESE:
Extração: {extracao}
Classificação: {classificacao}
Análise: {analise}

DOCUMENTO ORIGINAL:
{input}''',
            'base_vetorial': 'agentes_basicos',
            'ativo': True,
            'modelo_ai': 'gpt-4o',
            'temperatura': 0.4,
            'top_p': 0.9,
            'max_tokens': 2500,
            'capacidades': {
                'tipo': 'sintese',
                'especialidades': ['consolidação de análises', 'síntese executiva', 'recomendações estratégicas'],
                'integracao': 'multiplos_agentes',
                'formato': 'estruturado'
            }
        },
        {
            'nome': 'Formatador',
            'classe': 'FormatadorAgent',
            'descricao': 'Agente responsável por formatar o resultado final em um formato adequado para apresentação e uso profissional.',
            'template_prompt': '''Você é um especialista em formatação de documentos jurídicos. Formate o resultado da análise em um documento profissional e bem estruturado:

1. ESTRUTURA DO DOCUMENTO:
   - Cabeçalho com identificação da análise
   - Índice de conteúdo
   - Seções bem organizadas
   - Formatação profissional

2. ELEMENTOS VISUAIS:
   - Títulos e subtítulos hierárquicos
   - Listas ordenadas quando apropriado
   - Destaques para informações críticas
   - Separação clara entre seções

3. FORMATAÇÃO DE CONTEÚDO:
   - Parágrafos bem estruturados
   - Linguagem técnica adequada
   - Citações legais formatadas
   - Tabelas quando necessário

4. ELEMENTOS COMPLEMENTARES:
   - Resumo executivo destacado
   - Alertas de risco em destaque
   - Recomendações em formato de lista
   - Conclusões em seção específica

5. METADADOS:
   - Data da análise
   - Agentes utilizados
   - Versão do documento
   - Identificadores únicos

O resultado deve ser um documento profissional, claro e adequado para uso em ambiente jurídico.

CONTEÚDO PARA FORMATAÇÃO:
{sintese}

FORMATO DESEJADO: {formato_saida}''',
            'base_vetorial': 'agentes_basicos',
            'ativo': True,
            'modelo_ai': 'gpt-4o',
            'temperatura': 0.2,
            'top_p': 0.9,
            'max_tokens': 2000,
            'capacidades': {
                'tipo': 'formatacao',
                'especialidades': ['formatação profissional', 'estruturação de documentos', 'apresentação visual'],
                'formatos': ['html', 'markdown', 'texto', 'pdf'],
                'qualidade': 'profissional'
            }
        }
    ]
    
    session, engine = get_database_connection()
    if not session:
        return False
    
    try:
        # Verifica se existe categoria para os agentes de processamento
        categoria_query = text("SELECT id FROM categoria_juridica WHERE nome = 'Agentes de Processamento' LIMIT 1")
        categoria_result = session.execute(categoria_query).fetchone()
        
        if not categoria_result:
            # Criar categoria para agentes de processamento
            insert_categoria = text("""
                INSERT INTO categoria_juridica (nome, descricao, cor, icone, ativa, created_at, updated_at)
                VALUES ('Agentes de Processamento', 'Agentes fundamentais do sistema multi-agente para processamento sequencial', '#17a2b8', 'fa-cogs', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id
            """)
            categoria_result = session.execute(insert_categoria).fetchone()
        
        categoria_id = categoria_result[0]
        
        # Cadastrar cada agente
        for agente in agentes_basicos:
            # Verificar se o agente já existe
            check_query = text("SELECT id FROM agente_juridico WHERE nome = :nome")
            existing = session.execute(check_query, {'nome': agente['nome']}).fetchone()
            
            if existing:
                logger.info(f"Agente {agente['nome']} já existe, atualizando...")
                
                # Atualizar agente existente
                update_query = text("""
                    UPDATE agente_juridico SET
                        classe = :classe,
                        descricao = :descricao,
                        template_prompt = :template_prompt,
                        base_vetorial = :base_vetorial,
                        ativo = :ativo,
                        modelo_ai = :modelo_ai,
                        temperatura = :temperatura,
                        top_p = :top_p,
                        max_tokens = :max_tokens,
                        capacidades = :capacidades,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE nome = :nome
                """)
                
                session.execute(update_query, {
                    'nome': agente['nome'],
                    'classe': agente['classe'],
                    'descricao': agente['descricao'],
                    'template_prompt': agente['template_prompt'],
                    'base_vetorial': agente['base_vetorial'],
                    'ativo': agente['ativo'],
                    'modelo_ai': agente['modelo_ai'],
                    'temperatura': agente['temperatura'],
                    'top_p': agente['top_p'],
                    'max_tokens': agente['max_tokens'],
                    'capacidades': json.dumps(agente['capacidades'])
                })
                
            else:
                logger.info(f"Cadastrando novo agente: {agente['nome']}")
                
                # Inserir novo agente
                insert_query = text("""
                    INSERT INTO agente_juridico (
                        nome, classe, descricao, categoria_id, template_prompt,
                        base_vetorial, ativo, modelo_ai, temperatura, top_p, max_tokens,
                        capacidades, icone, cor_destaque, nivel_especializacao,
                        created_at, updated_at
                    ) VALUES (
                        :nome, :classe, :descricao, :categoria_id, :template_prompt,
                        :base_vetorial, :ativo, :modelo_ai, :temperatura, :top_p, :max_tokens,
                        :capacidades, 'fa-robot', '#28a745', 1,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """)
                
                session.execute(insert_query, {
                    'nome': agente['nome'],
                    'classe': agente['classe'],
                    'descricao': agente['descricao'],
                    'categoria_id': categoria_id,
                    'template_prompt': agente['template_prompt'],
                    'base_vetorial': agente['base_vetorial'],
                    'ativo': agente['ativo'],
                    'modelo_ai': agente['modelo_ai'],
                    'temperatura': agente['temperatura'],
                    'top_p': agente['top_p'],
                    'max_tokens': agente['max_tokens'],
                    'capacidades': json.dumps(agente['capacidades'])
                })
        
        session.commit()
        logger.info("✅ Todos os agentes básicos foram cadastrados/atualizados com sucesso!")
        
        # Verificar cadastro
        verify_query = text("SELECT nome, classe, ativo FROM agente_juridico WHERE nome IN ('Extrator', 'Classificador', 'Analisador', 'Sintetizador', 'Formatador')")
        results = session.execute(verify_query).fetchall()
        
        logger.info("📋 Agentes cadastrados:")
        for result in results:
            logger.info(f"  - {result[0]} ({result[1]}) - Ativo: {result[2]}")
        
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao cadastrar agentes básicos: {e}")
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    success = cadastrar_agentes_basicos()
    if success:
        print("✅ Agentes básicos cadastrados com sucesso!")
    else:
        print("❌ Falha ao cadastrar agentes básicos")
        sys.exit(1)