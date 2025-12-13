"""
Script para popular o banco de dados com templates jurídicos das 7 áreas
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models_templates import AreaJuridica, TipoDocumento, TemplateJuridico

# Configuração do banco
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def criar_areas_juridicas():
    """Cria as 7 áreas jurídicas principais"""
    session = Session()
    
    areas = [
        {
            'nome': 'Direito Civil',
            'icone': '⚖️',
            'descricao': 'Área que trata das relações privadas entre pessoas físicas e jurídicas',
            'cor_tema': '#2563eb',
            'ordem_exibicao': 1
        },
        {
            'nome': 'Direito Trabalhista',
            'icone': '⚙️',
            'descricao': 'Regulamenta as relações de trabalho e direitos dos trabalhadores',
            'cor_tema': '#dc2626',
            'ordem_exibicao': 2
        },
        {
            'nome': 'Direito Empresarial',
            'icone': '🏢',
            'descricao': 'Normas que regem as atividades empresariais e societárias',
            'cor_tema': '#059669',
            'ordem_exibicao': 3
        },
        {
            'nome': 'Direito Penal',
            'icone': '⚖️',
            'descricao': 'Área que define crimes e estabelece punições',
            'cor_tema': '#7c2d12',
            'ordem_exibicao': 4
        },
        {
            'nome': 'Direito Agrário',
            'icone': '🌾',
            'descricao': 'Regulamenta as relações jurídicas no campo e reforma agrária',
            'cor_tema': '#65a30d',
            'ordem_exibicao': 5
        },
        {
            'nome': 'Direito Securitário',
            'icone': '🛡',
            'descricao': 'Normas que regem contratos de seguro e resseguro',
            'cor_tema': '#7c3aed',
            'ordem_exibicao': 6
        },
        {
            'nome': 'Direito Tributário',
            'icone': '💰',
            'descricao': 'Regulamenta a arrecadação e fiscalização de tributos',
            'cor_tema': '#ea580c',
            'ordem_exibicao': 7
        }
    ]
    
    for area_data in areas:
        # Verificar se já existe
        area_existente = session.query(AreaJuridica).filter_by(nome=area_data['nome']).first()
        if not area_existente:
            area = AreaJuridica(**area_data)
            session.add(area)
    
    session.commit()
    session.close()
    print("✅ Áreas jurídicas criadas com sucesso!")

def criar_tipos_documento():
    """Cria os tipos de documentos jurídicos"""
    session = Session()
    
    tipos = [
        # Petições e Iniciais
        {'nome': 'Petição Inicial', 'categoria': 'peticao', 'descricao': 'Documento que dá início a uma ação judicial', 'icone': '📄'},
        {'nome': 'Reclamação Trabalhista', 'categoria': 'peticao', 'descricao': 'Petição inicial específica da Justiça do Trabalho', 'icone': '📄'},
        {'nome': 'Queixa-Crime', 'categoria': 'peticao', 'descricao': 'Petição inicial para ação penal privada', 'icone': '📄'},
        
        # Defesas
        {'nome': 'Contestação', 'categoria': 'defesa', 'descricao': 'Defesa do réu em ação civil', 'icone': '🛡️'},
        {'nome': 'Defesa Trabalhista', 'categoria': 'defesa', 'descricao': 'Contestação em processo trabalhista', 'icone': '🛡️'},
        {'nome': 'Defesa Prévia', 'categoria': 'defesa', 'descricao': 'Primeira defesa em processo penal', 'icone': '🛡️'},
        
        # Recursos
        {'nome': 'Recurso de Apelação', 'categoria': 'recurso', 'descricao': 'Recurso contra sentença de 1º grau', 'icone': '📈'},
        {'nome': 'Recurso Ordinário', 'categoria': 'recurso', 'descricao': 'Recurso trabalhista para TRT', 'icone': '📈'},
        {'nome': 'Apelação Criminal', 'categoria': 'recurso', 'descricao': 'Recurso contra sentença penal', 'icone': '📈'},
        
        # Embargos
        {'nome': 'Embargos de Declaração', 'categoria': 'embargos', 'descricao': 'Para esclarecer omissões ou contradições', 'icone': '❓'},
        {'nome': 'Embargos à Execução', 'categoria': 'embargos', 'descricao': 'Defesa contra execução', 'icone': '⛔'},
        {'nome': 'Embargos à Execução Fiscal', 'categoria': 'embargos', 'descricao': 'Defesa contra execução fiscal', 'icone': '⛔'},
        
        # Ações Específicas
        {'nome': 'Ação Monitória', 'categoria': 'acao_especifica', 'descricao': 'Para cobrança com prova escrita', 'icone': '💰'},
        {'nome': 'Mandado de Segurança', 'categoria': 'acao_especifica', 'descricao': 'Contra ato ilegal de autoridade', 'icone': '🛡️'},
        {'nome': 'Habeas Corpus', 'categoria': 'acao_especifica', 'descricao': 'Defesa da liberdade de locomoção', 'icone': '🔓'},
        
        # Documentos Complementares
        {'nome': 'Impugnação à Contestação', 'categoria': 'complementar', 'descricao': 'Réplica aos argumentos da defesa', 'icone': '↩️'},
        {'nome': 'Memoriais Finais', 'categoria': 'complementar', 'descricao': 'Alegações finais no processo', 'icone': '📝'},
        {'nome': 'Manifestação sobre Cálculos', 'categoria': 'complementar', 'descricao': 'Análise de liquidação de sentença', 'icone': '🧮'},
        
        # Ações Empresariais
        {'nome': 'Recuperação Judicial', 'categoria': 'empresarial', 'descricao': 'Para empresas em crise financeira', 'icone': '🏭'},
        {'nome': 'Dissolução Parcial de Sociedade', 'categoria': 'empresarial', 'descricao': 'Conflitos societários', 'icone': '👥'},
        
        # Ações Agrárias
        {'nome': 'Reintegração de Posse Rural', 'categoria': 'agrario', 'descricao': 'Conflitos possessórios rurais', 'icone': '🚜'},
        {'nome': 'Usucapião Rural', 'categoria': 'agrario', 'descricao': 'Regularização fundiária', 'icone': '🗺️'},
        
        # Ações Securitárias
        {'nome': 'Cobrança de Seguro', 'categoria': 'securitario', 'descricao': 'Exigir pagamento de seguro', 'icone': '🛡️'},
        {'nome': 'Ação Regressiva de Seguradora', 'categoria': 'securitario', 'descricao': 'Regresso contra terceiros', 'icone': '↪️'},
        
        # Ações Tributárias
        {'nome': 'Ação Anulatória de Débito Fiscal', 'categoria': 'tributario', 'descricao': 'Questionar cobrança tributária', 'icone': '🚫'},
        {'nome': 'Repetição de Indébito Tributário', 'categoria': 'tributario', 'descricao': 'Devolução de tributo pago indevidamente', 'icone': '💸'}
    ]
    
    for tipo_data in tipos:
        # Verificar se já existe
        tipo_existente = session.query(TipoDocumento).filter_by(nome=tipo_data['nome']).first()
        if not tipo_existente:
            tipo = TipoDocumento(**tipo_data)
            session.add(tipo)
    
    session.commit()
    session.close()
    print("✅ Tipos de documento criados com sucesso!")

def obter_template_html(area_nome, tipo_nome, numero_template):
    """Gera o HTML específico para cada template"""
    
    # Cabeçalho padrão
    cabecalho = f"""
    <div style="text-align: center; margin-bottom: 2rem; border-bottom: 2px solid #dee2e6; padding-bottom: 1rem;">
        <h1 style="color: #2c3e50; margin-bottom: 0.5rem; font-size: 1.8rem; font-weight: bold;">
            {tipo_nome.upper()}
        </h1>
        <p style="color: #6c757d; margin: 0; font-size: 0.9rem;">
            <strong>Área:</strong> {area_nome} | <strong>Template #{numero_template:02d}</strong>
        </p>
    </div>
    """
    
    # Corpo específico por área e tipo
    if area_nome == "Direito Civil":
        if "Petição" in tipo_nome:
            corpo = f"""
            <div style="margin: 1.5rem 0;">
                <p><strong>Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) de Direito da [VARA] de [CIDADE/UF]</strong></p>
                
                <p style="margin-top: 2rem;"><strong>[NOME DO REQUERENTE]</strong>, [qualificação completa], vem respeitosamente à presença de Vossa Excelência, por meio de seu(sua) advogado(a) que esta subscreve, com fundamento nos artigos [ARTIGOS APLICÁVEIS] do Código Civil e [DISPOSITIVOS DO CPC], propor a presente</p>
                
                <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0 1.5rem 0;">AÇÃO [TIPO DA AÇÃO]</h2>
                
                <p>em face de <strong>[NOME DO REQUERIDO]</strong>, [qualificação], pelas razões de fato e de direito a seguir expostas:</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">I - DOS FATOS</h3>
                <p>[Narração detalhada dos fatos que deram origem ao direito pleiteado, em ordem cronológica e de forma clara e objetiva]</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">II - DO DIREITO</h3>
                <p>[Fundamentação jurídica com citação de artigos de lei, jurisprudência e doutrina aplicáveis ao caso]</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">III - DOS PEDIDOS</h3>
                <p>Diante do exposto, requer-se:</p>
                <ol>
                    <li>A citação do(a) requerido(a) para contestar a presente ação;</li>
                    <li>[PEDIDOS ESPECÍFICOS];</li>
                    <li>A procedência total dos pedidos;</li>
                    <li>A condenação da parte requerida ao pagamento das custas processuais e honorários advocatícios.</li>
                </ol>
                
                <p style="margin-top: 2rem;">Dá-se à causa o valor de R$ [VALOR].</p>
                
                <p style="margin-top: 2rem;">Nestes termos, pede deferimento.</p>
                
                <div style="margin-top: 3rem; text-align: right;">
                    <p>[CIDADE], [DATA]</p>
                    <br><br>
                    <p>_________________________________</p>
                    <p><strong>[NOME DO ADVOGADO]</strong></p>
                    <p>OAB/[UF] nº [NÚMERO]</p>
                </div>
            </div>
            """
        elif "Contestação" in tipo_nome:
            corpo = f"""
            <div style="margin: 1.5rem 0;">
                <p><strong>Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) de Direito</strong></p>
                
                <p style="margin-top: 2rem;"><strong>[NOME DO CONTESTANTE]</strong>, [qualificação], já devidamente qualificado nos autos da ação [TIPO] que lhe move [NOME DO AUTOR], vem, respeitosamente, por intermédio de seu advogado que esta subscreve, apresentar sua</p>
                
                <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0 1.5rem 0;">CONTESTAÇÃO</h2>
                
                <p>nos termos dos artigos 335 e seguintes do Código de Processo Civil, pelas razões a seguir expostas:</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">I - DAS PRELIMINARES</h3>
                <p>[Arguir eventuais preliminares como ilegitimidade, incompetência, inépcia da inicial, etc.]</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">II - DO MÉRITO</h3>
                <p>Quanto ao mérito, impugna-se integralmente os fatos alegados pelo autor, pelos seguintes fundamentos:</p>
                <p>[Defesa detalhada com impugnação específica dos fatos e fundamentação jurídica]</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">III - DOS PEDIDOS</h3>
                <p>Ante o exposto, requer-se:</p>
                <ol>
                    <li>O acolhimento das preliminares arguidas;</li>
                    <li>No mérito, a total improcedência dos pedidos;</li>
                    <li>A condenação do autor ao pagamento das custas e honorários advocatícios.</li>
                </ol>
                
                <p style="margin-top: 2rem;">Nestes termos, pede deferimento.</p>
                
                <div style="margin-top: 3rem; text-align: right;">
                    <p>[CIDADE], [DATA]</p>
                    <br><br>
                    <p>_________________________________</p>
                    <p><strong>[NOME DO ADVOGADO]</strong></p>
                    <p>OAB/[UF] nº [NÚMERO]</p>
                </div>
            </div>
            """
    elif area_nome == "Direito Trabalhista":
        if "Reclamação" in tipo_nome:
            corpo = f"""
            <div style="margin: 1.5rem 0;">
                <p><strong>Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) do Trabalho da [VARA] de [CIDADE/UF]</strong></p>
                
                <p style="margin-top: 2rem;"><strong>[NOME DO RECLAMANTE]</strong>, [qualificação completa], vem respeitosamente à presença de Vossa Excelência apresentar</p>
                
                <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0 1.5rem 0;">RECLAMAÇÃO TRABALHISTA</h2>
                
                <p>em face de <strong>[NOME DA EMPRESA RECLAMADA]</strong>, [qualificação], pelos fundamentos a seguir expostos:</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">I - DOS FATOS</h3>
                <p>O reclamante foi admitido em [DATA DE ADMISSÃO] para exercer a função de [CARGO], sendo dispensado em [DATA DE DISPENSA], [COM/SEM] justa causa.</p>
                <p>[Narração dos fatos que originaram os direitos pleiteados]</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">II - DOS DIREITOS PLEITEADOS</h3>
                <p>Diante dos fatos narrados, pleiteia o reclamante:</p>
                <ol>
                    <li>Aviso prévio: R$ [VALOR]</li>
                    <li>13º salário proporcional: R$ [VALOR]</li>
                    <li>Férias proporcionais + 1/3: R$ [VALOR]</li>
                    <li>Saldo de salário: R$ [VALOR]</li>
                    <li>FGTS + 40%: R$ [VALOR]</li>
                    <li>[OUTROS DIREITOS ESPECÍFICOS]</li>
                </ol>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">III - DOS PEDIDOS</h3>
                <p>Ante o exposto, requer:</p>
                <ol>
                    <li>A citação da reclamada;</li>
                    <li>A procedência total dos pedidos;</li>
                    <li>A condenação da reclamada ao pagamento de todos os direitos pleiteados.</li>
                </ol>
                
                <p style="margin-top: 2rem;">Valor da causa: R$ [VALOR TOTAL]</p>
                
                <div style="margin-top: 3rem; text-align: right;">
                    <p>[CIDADE], [DATA]</p>
                    <br><br>
                    <p>_________________________________</p>
                    <p><strong>[NOME DO ADVOGADO]</strong></p>
                    <p>OAB/[UF] nº [NÚMERO]</p>
                </div>
            </div>
            """
    elif area_nome == "Direito Penal":
        if "Defesa" in tipo_nome:
            corpo = f"""
            <div style="margin: 1.5rem 0;">
                <p><strong>Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) de Direito da [VARA CRIMINAL]</strong></p>
                
                <p style="margin-top: 2rem;"><strong>[NOME DO RÉU]</strong>, [qualificação], por seu defensor que esta subscreve, vem, respeitosamente, apresentar</p>
                
                <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0 1.5rem 0;">DEFESA PRÉVIA</h2>
                
                <p>nos autos da Ação Penal nº [NÚMERO], pelas razões a seguir expostas:</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">I - DA INÉPCIA DA DENÚNCIA</h3>
                <p>[Arguir eventuais vícios da denúncia, falta de justa causa, etc.]</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">II - DA DEFESA DE MÉRITO</h3>
                <p>Quanto ao mérito, sustenta a defesa:</p>
                <p>[Argumentos de mérito, negativa de autoria, excludentes de ilicitude, etc.]</p>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">III - DA PRODUÇÃO DE PROVAS</h3>
                <p>Requer a produção das seguintes provas:</p>
                <ol>
                    <li>Prova testemunhal;</li>
                    <li>Prova documental;</li>
                    <li>[OUTRAS PROVAS ESPECÍFICAS]</li>
                </ol>
                
                <h3 style="color: #2c3e50; margin-top: 2rem;">IV - DOS PEDIDOS</h3>
                <p>Ante o exposto, requer:</p>
                <ol>
                    <li>A rejeição da denúncia;</li>
                    <li>Subsidiariamente, a absolvição do réu;</li>
                    <li>A produção das provas requeridas.</li>
                </ol>
                
                <div style="margin-top: 3rem; text-align: right;">
                    <p>[CIDADE], [DATA]</p>
                    <br><br>
                    <p>_________________________________</p>
                    <p><strong>[NOME DO ADVOGADO]</strong></p>
                    <p>OAB/[UF] nº [NÚMERO]</p>
                </div>
            </div>
            """
    else:
        # Template genérico para outras áreas
        corpo = f"""
        <div style="margin: 1.5rem 0;">
            <p><strong>Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) de Direito</strong></p>
            
            <p style="margin-top: 2rem;"><strong>[NOME DA PARTE]</strong>, [qualificação completa], vem respeitosamente à presença de Vossa Excelência, por intermédio de seu(sua) advogado(a) que esta subscreve, apresentar o presente documento, pelos fundamentos a seguir expostos:</p>
            
            <h3 style="color: #2c3e50; margin-top: 2rem;">I - DOS FATOS</h3>
            <p>[Exposição clara e objetiva dos fatos relevantes para o caso]</p>
            
            <h3 style="color: #2c3e50; margin-top: 2rem;">II - DO DIREITO</h3>
            <p>[Fundamentação jurídica com base na legislação, jurisprudência e doutrina aplicáveis]</p>
            
            <h3 style="color: #2c3e50; margin-top: 2rem;">III - DOS PEDIDOS</h3>
            <p>Diante do exposto, requer-se:</p>
            <ol>
                <li>[PEDIDO PRINCIPAL];</li>
                <li>[PEDIDOS SUBSIDIÁRIOS];</li>
                <li>O que mais se fizer necessário para o deslinde da questão.</li>
            </ol>
            
            <p style="margin-top: 2rem;">Nestes termos, pede deferimento.</p>
            
            <div style="margin-top: 3rem; text-align: right;">
                <p>[CIDADE], [DATA]</p>
                <br><br>
                <p>_________________________________</p>
                <p><strong>[NOME DO ADVOGADO]</strong></p>
                <p>OAB/[UF] nº [NÚMERO]</p>
            </div>
        </div>
        """
    
    return cabecalho + corpo

def criar_templates():
    """Cria os templates para todas as áreas jurídicas"""
    session = Session()
    
    # Templates do documento anexo organizados por área
    templates_data = {
        "Direito Civil": [
            {"tipo": "Petição Inicial", "desc": "Início de ações como indenizatórias, cobrança, obrigação de fazer"},
            {"tipo": "Contestação", "desc": "Defesa do réu, com argumentos de mérito e preliminares"},
            {"tipo": "Impugnação à Contestação", "desc": "Réplica do autor para rebater os argumentos da parte contrária"},
            {"tipo": "Recurso de Apelação", "desc": "Recurso contra sentença de 1º grau"},
            {"tipo": "Embargos de Declaração", "desc": "Utilizados para esclarecer omissão, contradição ou obscuridade"},
            {"tipo": "Ação Monitória", "desc": "Usada para cobrar dívida baseada em prova escrita"},
            {"tipo": "Ação de Obrigação de Fazer", "desc": "Muito comum em relações contratuais e consumeristas"},
            {"tipo": "Ação de Tutela Antecipada", "desc": "Para obtenção urgente de medida judicial"},
            {"tipo": "Embargos à Execução", "desc": "Defesa do executado"},
            {"tipo": "Recurso Especial", "desc": "Destinado ao STJ"}
        ],
        "Direito Trabalhista": [
            {"tipo": "Reclamação Trabalhista", "desc": "Propositura de ação pelo trabalhador"},
            {"tipo": "Defesa Trabalhista", "desc": "Apresentada pelo empregador"},
            {"tipo": "Impugnação à Contestação", "desc": "Rebate os argumentos do empregador"},
            {"tipo": "Embargos à Execução", "desc": "Defesa contra execução de sentença"},
            {"tipo": "Recurso Ordinário", "desc": "Recurso contra decisões das Varas do Trabalho para os TRTs"},
            {"tipo": "Acordo Judicial Homologado", "desc": "Formaliza conciliação entre as partes"},
            {"tipo": "Embargos de Declaração", "desc": "Esclarecimento de decisões com omissão ou contradição"},
            {"tipo": "Agravo de Petição", "desc": "Recurso usado na fase de execução"},
            {"tipo": "Pedido de Homologação de Acordo", "desc": "Formalização de acordos fora do processo"},
            {"tipo": "Manifestação sobre Cálculos", "desc": "Fundamental na fase de execução"}
        ],
        "Direito Empresarial": [
            {"tipo": "Petição Inicial de Execução", "desc": "Cobrança de dívidas empresariais"},
            {"tipo": "Recuperação Judicial", "desc": "Para empresas em dificuldade financeira"},
            {"tipo": "Dissolução Parcial de Sociedade", "desc": "Usada em conflitos societários"},
            {"tipo": "Contestação Responsabilidade", "desc": "Defesa de sócios ou administradores"},
            {"tipo": "Embargos à Execução Fiscal", "desc": "Defesa contra execuções promovidas pela Fazenda Pública"},
            {"tipo": "Carta de Intimação", "desc": "Essencial em tratativas pré-processuais"},
            {"tipo": "Ação de Prestação de Contas", "desc": "Para sócios, administradores ou representantes legais"},
            {"tipo": "Ação de Obrigação de Entregar", "desc": "Relevante em disputas entre sócios"},
            {"tipo": "Interpelação Judicial", "desc": "Usada para constituir em mora"},
            {"tipo": "Ação de Não Concorrência", "desc": "Muito usada após cisões e aquisições"}
        ],
        "Direito Penal": [
            {"tipo": "Queixa-Crime", "desc": "Ação penal privada"},
            {"tipo": "Defesa Prévia", "desc": "Apresentada após o recebimento da denúncia"},
            {"tipo": "Memoriais Finais", "desc": "Alegações finais antes da sentença"},
            {"tipo": "Apelação Criminal", "desc": "Recurso contra sentença condenatória"},
            {"tipo": "Habeas Corpus", "desc": "Defesa da liberdade de locomoção frente a ilegalidades"},
            {"tipo": "Denúncia", "desc": "Proposta pelo Ministério Público em ação penal pública"},
            {"tipo": "Pedido de Liberdade Provisória", "desc": "Muito comum em flagrantes"},
            {"tipo": "Pedido de Relaxamento", "desc": "Quando há prisão ilegal"},
            {"tipo": "Revisão Criminal", "desc": "Para revisão de sentença condenatória transitada"},
            {"tipo": "Agravo em Execução Penal", "desc": "Contestação de atos da execução penal"}
        ],
        "Direito Agrário": [
            {"tipo": "Reintegração de Posse", "desc": "Usada em conflitos possessórios rurais"},
            {"tipo": "Nulidade de Arrendamento", "desc": "Questionamento de contratos viciados"},
            {"tipo": "Contestação em Despejo Rural", "desc": "Defesa de produtores rurais"},
            {"tipo": "Rescisão de Contrato Agrário", "desc": "Encerramento judicial de relações contratuais"},
            {"tipo": "Ação Indenizatória Produção", "desc": "Por pulverização indevida de agrotóxicos"},
            {"tipo": "Usucapião Rural", "desc": "Regularização fundiária de área produtiva"},
            {"tipo": "Defesa em Despejo Agrário", "desc": "Muito frequente em conflitos de posse"},
            {"tipo": "Regularização Fundiária", "desc": "Instrumento administrativo com forte impacto jurídico"},
            {"tipo": "Ação Cautelar Sustação", "desc": "Proteção ambiental e possessória"},
            {"tipo": "Cumprimento de Parceria", "desc": "Para exigir obrigações de parceiros agrícolas"}
        ],
        "Direito Securitário": [
            {"tipo": "Cobrança de Seguro", "desc": "Ação do segurado para exigir pagamento"},
            {"tipo": "Contestação da Seguradora", "desc": "Defesa da negativa de cobertura"},
            {"tipo": "Ação Declaratória Inexistência", "desc": "Normalmente movida pela seguradora"},
            {"tipo": "Recurso de Apelação", "desc": "Contra sentença de 1ª instância"},
            {"tipo": "Embargos à Execução", "desc": "Defesa do devedor contra cumprimento de sentença"},
            {"tipo": "Produção Antecipada de Provas", "desc": "Comum quando segurado quer preservar evidência"},
            {"tipo": "Ação de Exibição de Documentos", "desc": "Usada para forçar seguradora a entregar apólice"},
            {"tipo": "Manifestação Técnica Contrária", "desc": "Apresentada por peritos do segurado"},
            {"tipo": "Ação Indenização Perda Total", "desc": "Muito comum em casos de automóveis e imóveis"},
            {"tipo": "Ação Regressiva da Seguradora", "desc": "Quando seguradora busca reaver valores pagos"}
        ],
        "Direito Tributário": [
            {"tipo": "Mandado de Segurança", "desc": "Usado contra cobranças ilegais de tributos"},
            {"tipo": "Ação Anulatória de Débito", "desc": "Questiona a validade de cobranças"},
            {"tipo": "Embargos à Execução Fiscal", "desc": "Defesa do contribuinte"},
            {"tipo": "Ação Declaratória Inexistência", "desc": "Busca afastar obrigação tributária indevida"},
            {"tipo": "Recurso de Apelação", "desc": "Para revisão de decisão desfavorável"},
            {"tipo": "Consulta Fiscal Preventiva", "desc": "Esclarece dúvidas sobre incidência de tributo"},
            {"tipo": "Defesa em Auto de Infração", "desc": "Primeira etapa no contencioso tributário"},
            {"tipo": "Pedido de Compensação", "desc": "Para uso de crédito tributário legítimo"},
            {"tipo": "Repetição de Indébito", "desc": "Requer devolução de tributo pago indevidamente"},
            {"tipo": "Recurso ao CARF", "desc": "Etapa fundamental no contencioso administrativo federal"}
        ]
    }
    
    contador_global = 1
    
    for area_nome, templates_lista in templates_data.items():
        # Buscar área
        area = session.query(AreaJuridica).filter_by(nome=area_nome).first()
        if not area:
            print(f"❌ Área {area_nome} não encontrada!")
            continue
        
        for i, template_info in enumerate(templates_lista, 1):
            # Buscar tipo de documento
            tipo = session.query(TipoDocumento).filter_by(nome=template_info["tipo"]).first()
            if not tipo:
                # Criar tipo se não existir
                categoria_map = {
                    "Petição": "peticao", "Reclamação": "peticao", "Queixa": "peticao",
                    "Contestação": "defesa", "Defesa": "defesa",
                    "Recurso": "recurso", "Apelação": "recurso",
                    "Embargos": "embargos",
                    "Ação": "acao_especifica", "Mandado": "acao_especifica", "Habeas": "acao_especifica"
                }
                
                categoria = "complementar"
                for palavra, cat in categoria_map.items():
                    if palavra in template_info["tipo"]:
                        categoria = cat
                        break
                
                tipo = TipoDocumento(
                    nome=template_info["tipo"],
                    categoria=categoria,
                    descricao=template_info["desc"],
                    icone="📄"
                )
                session.add(tipo)
                session.flush()  # Para obter o ID
            
            # Verificar se template já existe
            template_existente = session.query(TemplateJuridico).filter_by(
                area_juridica_id=area.id,
                tipo_documento_id=tipo.id,
                nome=f"{template_info['tipo']} - {area_nome}"
            ).first()
            
            if not template_existente:
                # Gerar conteúdo HTML
                conteudo_html = obter_template_html(area_nome, template_info["tipo"], i)
                
                # Gerar palavras-chave
                palavras_chave = f"{area_nome.lower()}, {template_info['tipo'].lower()}, {tipo.categoria}"
                
                template = TemplateJuridico(
                    nome=f"{template_info['tipo']} - {area_nome}",
                    descricao=template_info["desc"],
                    conteudo_html=conteudo_html,
                    conteudo_texto=conteudo_html.replace('<', '').replace('>', ''),  # Versão simplificada
                    area_juridica_id=area.id,
                    tipo_documento_id=tipo.id,
                    palavras_chave=palavras_chave,
                    complexidade="intermediario",
                    tempo_estimado=30 + (i * 5),  # 30-80 minutos baseado na complexidade
                    criado_por="Sistema",
                    versao="1.0"
                )
                session.add(template)
                print(f"✅ Template criado: {template.nome}")
                contador_global += 1
    
    session.commit()
    session.close()
    print(f"✅ {contador_global-1} templates criados com sucesso!")

def main():
    """Função principal para popular o banco"""
    print("🚀 Iniciando população do banco de dados com templates jurídicos...")
    
    try:
        # Criar tabelas se não existirem
        from models_templates import AreaJuridica, TipoDocumento, TemplateJuridico, HistoricoUsoTemplate, FavoritoTemplate
        from main import db
        
        with db.app.app_context():
            db.create_all()
        
        criar_areas_juridicas()
        criar_tipos_documento() 
        criar_templates()
        
        print("🎉 Banco de dados populado com sucesso!")
        print("📊 Resumo:")
        
        session = Session()
        total_areas = session.query(AreaJuridica).count()
        total_tipos = session.query(TipoDocumento).count()
        total_templates = session.query(TemplateJuridico).count()
        
        print(f"   - {total_areas} áreas jurídicas")
        print(f"   - {total_tipos} tipos de documento")
        print(f"   - {total_templates} templates")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Erro ao popular banco: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()