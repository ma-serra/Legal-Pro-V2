"""
Assistente Jurídico Especializado em Direito Agrário
Módulo integrado ao Legal Design Pro V2 com funcionalidades avançadas
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AssistenteAgrario:
    def __init__(self):
        """Inicializa o Assistente de Direito Agrário"""
        self.area_juridica = "Direito Agrário"
        self.cor_primaria = "#896302"
        self.cor_secundaria = "#a67c00"
        self.database_url = os.environ.get('DATABASE_URL')
        
        # Configuração de especialidades
        self.especialidades = {
            "reforma_agraria": "Reforma Agrária e Redistribuição de Terras",
            "regularizacao_fundiaria": "Regularização Fundiária",
            "desapropriacao": "Desapropriação para Fins de Reforma Agrária",
            "quilombolas": "Direitos Quilombolas e Territoriais",
            "indigenas": "Direitos Indígenas e Demarcação",
            "agricultura_familiar": "Agricultura Familiar e Crédito Rural",
            "meio_ambiente_rural": "Meio Ambiente e Sustentabilidade Rural",
            "contratos_rurais": "Contratos e Arrendamentos Rurais",
            "agronegocio": "Agronegócio e Cooperativismo",
            "trabalho_rural": "Relações de Trabalho Rural",
            "tributacao_rural": "Tributação e Fiscalização Rural",
            "agua_irrigacao": "Recursos Hídricos e Irrigação",
            "credito_financiamento": "Crédito e Financiamento Rural",
            "seguro_rural": "Seguro Rural e Proteção",
            "tecnologia_rural": "Inovação e Tecnologia Rural",
            "certificacao": "Certificação e Qualidade Rural",
            "conflitos_agrarios": "Mediação de Conflitos Agrários"
        }
        
        # Conectar ao banco
        self._init_database()
        
    def _init_database(self):
        """Inicializa conexão com banco de dados"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            logger.info("✅ Conexão com banco de dados estabelecida para Direito Agrário")
        except Exception as e:
            logger.error(f"❌ Erro na conexão com banco: {e}")
            self.conn = None

    def criar_agentes_especializados(self) -> bool:
        """Cria os 17 agentes especializados em Direito Agrário"""
        if not self.conn:
            return False
            
        agentes_agrarios = [
            {
                "nome": "Especialista em Reforma Agrária",
                "descricao": "Especialista em processos de reforma agrária, redistribuição de terras e assentamentos rurais",
                "capacidades": [
                    "Análise de processos de desapropriação para reforma agrária",
                    "Elaboração de projetos de assentamento rural",
                    "Assessoria em redistribuição de terras públicas",
                    "Acompanhamento de processos no INCRA",
                    "Defesa de direitos de assentados rurais"
                ],
                "especialidade": "reforma_agraria"
            },
            {
                "nome": "Especialista em Regularização Fundiária",
                "descricao": "Especialista em regularização de propriedades rurais e documentação fundiária",
                "capacidades": [
                    "Regularização de títulos de propriedade rural",
                    "Análise de cadeia dominial rural",
                    "Elaboração de memoriais descritivos",
                    "Retificação de registros imobiliários rurais",
                    "Usucapião de imóveis rurais"
                ],
                "especialidade": "regularizacao_fundiaria"
            },
            {
                "nome": "Especialista em Desapropriação Agrária",
                "descricao": "Especialista em processos de desapropriação para fins de reforma agrária",
                "capacidades": [
                    "Defesa em processos de desapropriação",
                    "Cálculo de indenizações agrárias",
                    "Contestação de laudos periciais rurais",
                    "Análise de produtividade rural",
                    "Recursos em desapropriações"
                ],
                "especialidade": "desapropriacao"
            },
            {
                "nome": "Especialista em Direitos Quilombolas",
                "descricao": "Especialista em direitos territoriais quilombolas e comunidades tradicionais",
                "capacidades": [
                    "Titulação de territórios quilombolas",
                    "Defesa de direitos constitucionais quilombolas",
                    "Procedimentos de reconhecimento territorial",
                    "Conflitos envolvendo comunidades tradicionais",
                    "Assessoria em processos de certificação"
                ],
                "especialidade": "quilombolas"
            },
            {
                "nome": "Especialista em Direitos Indígenas",
                "descricao": "Especialista em demarcação de terras indígenas e direitos originários",
                "capacidades": [
                    "Processos de demarcação de terras indígenas",
                    "Defesa de direitos constitucionais indígenas",
                    "Conflitos por invasão de terras indígenas",
                    "Assessoria à FUNAI em processos judiciais",
                    "Proteção de patrimônio cultural indígena"
                ],
                "especialidade": "indigenas"
            },
            {
                "nome": "Especialista em Agricultura Familiar",
                "descricao": "Especialista em políticas públicas para agricultura familiar e crédito rural",
                "capacidades": [
                    "Acesso a programas de crédito rural",
                    "PRONAF e políticas de agricultura familiar",
                    "Assessoria em cooperativas rurais",
                    "Defesa de pequenos produtores rurais",
                    "Programas de fortalecimento da agricultura familiar"
                ],
                "especialidade": "agricultura_familiar"
            },
            {
                "nome": "Especialista em Meio Ambiente Rural",
                "descricao": "Especialista em legislação ambiental aplicada ao meio rural",
                "capacidades": [
                    "Licenciamento ambiental rural",
                    "Código Florestal e áreas de preservação",
                    "Cadastro Ambiental Rural (CAR)",
                    "Defesa em infrações ambientais rurais",
                    "Recuperação de áreas degradadas"
                ],
                "especialidade": "meio_ambiente_rural"
            },
            {
                "nome": "Especialista em Contratos Rurais",
                "descricao": "Especialista em contratos de arrendamento, parceria e cessão rural",
                "capacidades": [
                    "Elaboração de contratos de arrendamento rural",
                    "Contratos de parceria agrícola e pecuária",
                    "Cessão de uso de terras rurais",
                    "Resolução de conflitos contratuais rurais",
                    "Assessoria em contratos de integração"
                ],
                "especialidade": "contratos_rurais"
            },
            {
                "nome": "Especialista em Agronegócio",
                "descricao": "Especialista em agronegócio, cooperativismo e grandes empreendimentos rurais",
                "capacidades": [
                    "Constituição de cooperativas agropecuárias",
                    "Contratos do agronegócio",
                    "Fusões e aquisições no setor rural",
                    "Compliance no agronegócio",
                    "Certificações e padrões de qualidade"
                ],
                "especialidade": "agronegocio"
            },
            {
                "nome": "Especialista em Trabalho Rural",
                "descricao": "Especialista em relações trabalhistas no meio rural",
                "capacidades": [
                    "Direitos dos trabalhadores rurais",
                    "Trabalho análogo à escravidão rural",
                    "Acidentes de trabalho no campo",
                    "Sazonalidade e contratos rurais",
                    "Fiscalização trabalhista rural"
                ],
                "especialidade": "trabalho_rural"
            },
            {
                "nome": "Especialista em Tributação Rural",
                "descricao": "Especialista em tributação e fiscalização de atividades rurais",
                "capacidades": [
                    "ITR - Imposto Territorial Rural",
                    "Tributação de atividades agropecuárias",
                    "Benefícios fiscais rurais",
                    "Defesa em autos de infração rurais",
                    "Planejamento tributário rural"
                ],
                "especialidade": "tributacao_rural"
            },
            {
                "nome": "Especialista em Recursos Hídricos",
                "descricao": "Especialista em direito de águas, irrigação e recursos hídricos rurais",
                "capacidades": [
                    "Outorga de uso de recursos hídricos",
                    "Direitos de irrigação e captação",
                    "Conflitos por uso da água",
                    "Licenciamento de sistemas de irrigação",
                    "Cobrança pelo uso de recursos hídricos"
                ],
                "especialidade": "agua_irrigacao"
            },
            {
                "nome": "Especialista em Crédito Rural",
                "descricao": "Especialista em financiamento rural, crédito agrícola e programas governamentais",
                "capacidades": [
                    "Contratos de financiamento rural",
                    "Programas de crédito oficial",
                    "Renegociação de dívidas rurais",
                    "Garantias em operações rurais",
                    "Defesa em execuções de crédito rural"
                ],
                "especialidade": "credito_financiamento"
            },
            {
                "nome": "Especialista em Seguro Rural",
                "descricao": "Especialista em seguros rurais, proteção de safras e pecuária",
                "capacidades": [
                    "Seguro rural oficial e privado",
                    "PROAGRO e programas de proteção",
                    "Sinistros rurais e indenizações",
                    "Defesa em negativas de cobertura",
                    "Assessoria em contratos de seguro rural"
                ],
                "especialidade": "seguro_rural"
            },
            {
                "nome": "Especialista em Tecnologia Rural",
                "descricao": "Especialista em inovação tecnológica, propriedade intelectual e biotecnologia rural",
                "capacidades": [
                    "Propriedade intelectual rural",
                    "Contratos de tecnologia agrícola",
                    "Biotecnologia e transgênicos",
                    "Inovação em agrotecnologia",
                    "Proteção de cultivares"
                ],
                "especialidade": "tecnologia_rural"
            },
            {
                "nome": "Especialista em Certificação Rural",
                "descricao": "Especialista em certificações de qualidade, orgânicos e rastreabilidade rural",
                "capacidades": [
                    "Certificação de produtos orgânicos",
                    "Rastreabilidade e qualidade rural",
                    "Boas práticas agropecuárias",
                    "Certificações internacionais",
                    "Sistemas de gestão da qualidade rural"
                ],
                "especialidade": "certificacao"
            },
            {
                "nome": "Especialista em Conflitos Agrários",
                "descricao": "Especialista em mediação e resolução de conflitos no campo",
                "capacidades": [
                    "Mediação de conflitos agrários",
                    "Resolução extrajudicial de disputas",
                    "Invasões e conflitos por terra",
                    "Arbitragem em questões rurais",
                    "Pacificação social rural"
                ],
                "especialidade": "conflitos_agrarios"
            }
        ]
        
        try:
            cursor = self.conn.cursor()
            
            for agente in agentes_agrarios:
                # Verificar se agente já existe
                cursor.execute(
                    "SELECT id FROM agente_juridico WHERE nome = %s AND area_juridica = %s",
                    (agente["nome"], "Direito Agrário")
                )
                
                if cursor.fetchone():
                    logger.info(f"Agente {agente['nome']} já existe, pulando...")
                    continue
                
                # Inserir novo agente
                cursor.execute("""
                    INSERT INTO agente_juridico (
                        nome, descricao, capacidades, area_juridica, 
                        especialidade, ativo, criado_em, modelo_ia,
                        temperatura, max_tokens, prompt_sistema
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    agente["nome"],
                    agente["descricao"],
                    json.dumps(agente["capacidades"]),
                    "Direito Agrário",
                    agente["especialidade"],
                    True,
                    datetime.now(),
                    "gpt-4o",
                    0.7,
                    2000,
                    f"Você é um {agente['nome']} especializado em {agente['descricao']}. "
                    f"Suas principais capacidades incluem: {', '.join(agente['capacidades'])}. "
                    f"Sempre forneça respostas fundamentadas na legislação agrária brasileira, "
                    f"especialmente o Estatuto da Terra (Lei 4.504/64), Constituição Federal, "
                    f"e legislação específica da área."
                ))
                
                logger.info(f"✅ Agente {agente['nome']} criado com sucesso")
            
            self.conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar agentes: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def criar_templates_especializados(self) -> bool:
        """Cria templates especializados para cada agente agrário"""
        if not self.conn:
            return False
        
        templates_agrarios = {
            "Especialista em Reforma Agrária": [
                {
                    "nome": "Projeto de Assentamento Rural",
                    "descricao": "Template para elaboração de projetos de assentamento rural",
                    "conteudo": self._template_projeto_assentamento(),
                    "complexidade": "alta",
                    "tempo_estimado": 120
                },
                {
                    "nome": "Defesa de Direitos de Assentados",
                    "descricao": "Template para defesa judicial de direitos de assentados rurais",
                    "conteudo": self._template_defesa_assentados(),
                    "complexidade": "media",
                    "tempo_estimado": 90
                }
            ],
            "Especialista em Regularização Fundiária": [
                {
                    "nome": "Ação de Usucapião Rural",
                    "descricao": "Petição inicial para usucapião de imóvel rural",
                    "conteudo": self._template_usucapiao_rural(),
                    "complexidade": "alta",
                    "tempo_estimado": 150
                },
                {
                    "nome": "Memorial Descritivo Rural",
                    "descricao": "Template para elaboração de memorial descritivo de propriedade rural",
                    "conteudo": self._template_memorial_rural(),
                    "complexidade": "media",
                    "tempo_estimado": 60
                }
            ],
            "Especialista em Desapropriação Agrária": [
                {
                    "nome": "Contestação de Desapropriação",
                    "descricao": "Template para contestação em processo de desapropriação agrária",
                    "conteudo": self._template_contestacao_desapropriacao(),
                    "complexidade": "alta",
                    "tempo_estimado": 120
                }
            ],
            "Especialista em Direitos Quilombolas": [
                {
                    "nome": "Procedimento de Titulação Quilombola",
                    "descricao": "Template para procedimento de titulação de território quilombola",
                    "conteudo": self._template_titulacao_quilombola(),
                    "complexidade": "alta",
                    "tempo_estimado": 180
                }
            ],
            "Especialista em Direitos Indígenas": [
                {
                    "nome": "Ação de Demarcação Indígena",
                    "descricao": "Template para ações relacionadas à demarcação de terras indígenas",
                    "conteudo": self._template_demarcacao_indigena(),
                    "complexidade": "alta",
                    "tempo_estimado": 150
                }
            ],
            "Especialista em Agricultura Familiar": [
                {
                    "nome": "Contrato PRONAF",
                    "descricao": "Template para contratos do Programa Nacional de Agricultura Familiar",
                    "conteudo": self._template_contrato_pronaf(),
                    "complexidade": "media",
                    "tempo_estimado": 45
                }
            ],
            "Especialista em Meio Ambiente Rural": [
                {
                    "nome": "Cadastro Ambiental Rural",
                    "descricao": "Template para elaboração e regularização do CAR",
                    "conteudo": self._template_car(),
                    "complexidade": "media",
                    "tempo_estimado": 90
                }
            ],
            "Especialista em Contratos Rurais": [
                {
                    "nome": "Contrato de Arrendamento Rural",
                    "descricao": "Template para contrato de arrendamento rural",
                    "conteudo": self._template_arrendamento_rural(),
                    "complexidade": "media",
                    "tempo_estimado": 60
                }
            ]
        }
        
        try:
            cursor = self.conn.cursor()
            
            # Buscar área jurídica do Direito Agrário
            cursor.execute("SELECT id FROM legal_areas_juridicas WHERE nome = 'Direito Agrário'")
            result = cursor.fetchone()
            
            if not result:
                # Criar área se não existir
                cursor.execute("""
                    INSERT INTO legal_areas_juridicas (nome, descricao, cor_primaria, ativo, criado_em)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (
                    "Direito Agrário",
                    "Área jurídica especializada em questões agrárias, fundiárias e rurais",
                    self.cor_primaria,
                    True,
                    datetime.now()
                ))
                area_id = cursor.fetchone()[0]
            else:
                area_id = result[0]
            
            # Criar templates para cada agente
            for agente_nome, templates in templates_agrarios.items():
                for template in templates:
                    # Verificar se template já existe
                    cursor.execute(
                        "SELECT id FROM legal_templates_juridicos WHERE nome = %s AND criado_por = %s",
                        (template["nome"], agente_nome)
                    )
                    
                    if cursor.fetchone():
                        logger.info(f"Template {template['nome']} já existe, pulando...")
                        continue
                    
                    # Inserir template
                    cursor.execute("""
                        INSERT INTO legal_templates_juridicos (
                            nome, descricao, area_juridica_id, conteudo_html,
                            palavras_chave, complexidade, tempo_estimado,
                            ativo, criado_em, criado_por
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        template["nome"],
                        template["descricao"],
                        area_id,
                        template["conteudo"],
                        f"agrário, rural, {agente_nome.lower()}",
                        template["complexidade"],
                        template["tempo_estimado"],
                        True,
                        datetime.now(),
                        agente_nome
                    ))
                    
                    logger.info(f"✅ Template {template['nome']} criado para {agente_nome}")
            
            self.conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar templates: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def _template_projeto_assentamento(self) -> str:
        """Template para projeto de assentamento rural"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">PROJETO DE ASSENTAMENTO RURAL</h1>
                <p class="area-juridica">Direito Agrário - Reforma Agrária</p>
            </header>
            
            <section class="identificacao">
                <h3>1. IDENTIFICAÇÃO DO PROJETO</h3>
                <div class="campo-form">
                    <label>Nome do Projeto:</label>
                    <input type="text" name="nome_projeto" placeholder="Ex: Assentamento Rural São João">
                </div>
                <div class="campo-form">
                    <label>Localização (Município/UF):</label>
                    <input type="text" name="localizacao" placeholder="Ex: Município de Santos, SP">
                </div>
                <div class="campo-form">
                    <label>Área Total (hectares):</label>
                    <input type="number" name="area_total" placeholder="Ex: 1000">
                </div>
            </section>
            
            <section class="caracteristicas">
                <h3>2. CARACTERÍSTICAS DO IMÓVEL</h3>
                <div class="campo-form">
                    <label>Denominação do Imóvel:</label>
                    <input type="text" name="denominacao" placeholder="Fazenda, Sítio, Gleba">
                </div>
                <div class="campo-form">
                    <label>Matrícula/Registro:</label>
                    <input type="text" name="matricula" placeholder="Número da matrícula">
                </div>
                <div class="campo-form">
                    <label>Situação Jurídica:</label>
                    <select name="situacao_juridica">
                        <option value="">Selecione...</option>
                        <option value="desapropriado">Desapropriado</option>
                        <option value="arrecadado">Arrecadado</option>
                        <option value="doado">Doado</option>
                        <option value="incorporado">Incorporado ao Patrimônio Público</option>
                    </select>
                </div>
            </section>
            
            <section class="beneficiarios">
                <h3>3. BENEFICIÁRIOS</h3>
                <div class="campo-form">
                    <label>Número de Famílias:</label>
                    <input type="number" name="num_familias" placeholder="Ex: 50">
                </div>
                <div class="campo-form">
                    <label>Critérios de Seleção:</label>
                    <textarea name="criterios_selecao" rows="4" placeholder="Descrever critérios para seleção dos beneficiários conforme legislação aplicável"></textarea>
                </div>
            </section>
            
            <section class="infraestrutura">
                <h3>4. INFRAESTRUTURA PREVISTA</h3>
                <div class="campo-form">
                    <label>Vias de Acesso:</label>
                    <textarea name="vias_acesso" rows="3" placeholder="Descrever as vias de acesso existentes e previstas"></textarea>
                </div>
                <div class="campo-form">
                    <label>Recursos Hídricos:</label>
                    <textarea name="recursos_hidricos" rows="3" placeholder="Fontes de água, poços, açudes, rios"></textarea>
                </div>
                <div class="campo-form">
                    <label>Energia Elétrica:</label>
                    <textarea name="energia_eletrica" rows="2" placeholder="Situação atual e projeto de eletrificação"></textarea>
                </div>
            </section>
            
            <section class="viabilidade">
                <h3>5. VIABILIDADE TÉCNICA E ECONÔMICA</h3>
                <div class="campo-form">
                    <label>Aptidão Agrícola:</label>
                    <textarea name="aptidao_agricola" rows="3" placeholder="Análise da aptidão do solo para agricultura"></textarea>
                </div>
                <div class="campo-form">
                    <label>Atividades Produtivas Previstas:</label>
                    <textarea name="atividades_produtivas" rows="4" placeholder="Culturas, criações, atividades econômicas planejadas"></textarea>
                </div>
                <div class="campo-form">
                    <label>Cronograma de Implementação:</label>
                    <textarea name="cronograma" rows="4" placeholder="Fases e prazos para implementação do projeto"></textarea>
                </div>
            </section>
            
            <section class="fundamentacao">
                <h3>6. FUNDAMENTAÇÃO LEGAL</h3>
                <div class="texto-legal">
                    <p><strong>Base Legal:</strong></p>
                    <ul>
                        <li>Lei nº 4.504/64 (Estatuto da Terra)</li>
                        <li>Lei nº 8.629/93 (Lei da Reforma Agrária)</li>
                        <li>Decreto nº 9.311/18 (Regulamenta a Lei nº 8.629/93)</li>
                        <li>Constituição Federal, artigos 184 a 191</li>
                        <li>IN INCRA nº 15/2004 e alterações</li>
                    </ul>
                </div>
            </section>
            
            <footer class="template-footer">
                <p><strong>Observações:</strong> Este projeto deve ser elaborado em conformidade com as normas do INCRA e submetido aos órgãos competentes para análise e aprovação.</p>
                <p class="data-assinatura">Data: _________________ Responsável Técnico: _________________________________</p>
            </footer>
        </div>
        """

    def _template_defesa_assentados(self) -> str:
        """Template para defesa de direitos de assentados"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">DEFESA JUDICIAL DE DIREITOS DE ASSENTADOS</h1>
                <p class="area-juridica">Direito Agrário - Reforma Agrária</p>
            </header>
            
            <section class="identificacao-processo">
                <h3>1. IDENTIFICAÇÃO</h3>
                <div class="campo-form">
                    <label>Processo nº:</label>
                    <input type="text" name="numero_processo" placeholder="0000000-00.0000.0.00.0000">
                </div>
                <div class="campo-form">
                    <label>Vara/Tribunal:</label>
                    <input type="text" name="vara_tribunal">
                </div>
                <div class="campo-form">
                    <label>Nome do Assentado:</label>
                    <input type="text" name="nome_assentado">
                </div>
                <div class="campo-form">
                    <label>Projeto de Assentamento:</label>
                    <input type="text" name="projeto_assentamento">
                </div>
            </section>
            
            <section class="situacao-juridica">
                <h3>2. SITUAÇÃO CONTESTADA</h3>
                <div class="campo-form">
                    <label>Tipo de Violação:</label>
                    <select name="tipo_violacao">
                        <option value="">Selecione...</option>
                        <option value="cancelamento_irregular">Cancelamento Irregular de Título</option>
                        <option value="cobranca_indevida">Cobrança Indevida</option>
                        <option value="ameaca_despejo">Ameaça de Despejo</option>
                        <option value="negativa_credito">Negativa de Crédito Rural</option>
                        <option value="falta_infraestrutura">Falta de Infraestrutura Básica</option>
                        <option value="outro">Outro</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Descrição dos Fatos:</label>
                    <textarea name="descricao_fatos" rows="5" placeholder="Relatar detalhadamente os fatos que motivaram a ação"></textarea>
                </div>
            </section>
            
            <section class="direitos-violados">
                <h3>3. DIREITOS VIOLADOS</h3>
                <div class="campo-form">
                    <label>Direitos Constitucionais:</label>
                    <textarea name="direitos_constitucionais" rows="4" placeholder="Art. 5º, 184-191 da CF/88"></textarea>
                </div>
                <div class="campo-form">
                    <label>Direitos Legais:</label>
                    <textarea name="direitos_legais" rows="4" placeholder="Lei 8.629/93, Estatuto da Terra, regulamentos do INCRA"></textarea>
                </div>
            </section>
            
            <section class="pedidos">
                <h3>4. PEDIDOS</h3>
                <div class="campo-form">
                    <label>Tutela de Urgência:</label>
                    <textarea name="tutela_urgencia" rows="3" placeholder="Pedidos liminares ou antecipação de tutela"></textarea>
                </div>
                <div class="campo-form">
                    <label>Pedido Principal:</label>
                    <textarea name="pedido_principal" rows="4" placeholder="Pedido principal da ação"></textarea>
                </div>
                <div class="campo-form">
                    <label>Pedidos Subsidiários:</label>
                    <textarea name="pedidos_subsidiarios" rows="3" placeholder="Pedidos alternativos"></textarea>
                </div>
                <div class="campo-form">
                    <label>Indenização por Danos:</label>
                    <input type="text" name="indenizacao" placeholder="Valor ou critério para apuração">
                </div>
            </section>
            
            <section class="provas">
                <h3>5. PROVAS</h3>
                <div class="campo-form">
                    <label>Documentos Anexos:</label>
                    <textarea name="documentos" rows="4" placeholder="Listar todos os documentos que acompanham a petição"></textarea>
                </div>
                <div class="campo-form">
                    <label>Provas a Produzir:</label>
                    <textarea name="provas_produzir" rows="4" placeholder="Perícia, testemunhal, documental complementar"></textarea>
                </div>
            </section>
            
            <footer class="template-footer">
                <div class="clausula-final">
                    <p><strong>Nestes termos, pede deferimento.</strong></p>
                    <p>Local, data</p>
                    <p>_________________________________</p>
                    <p>Advogado - OAB/UF nº</p>
                </div>
            </footer>
        </div>
        """

    def _template_usucapiao_rural(self) -> str:
        """Template para ação de usucapião rural"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">AÇÃO DE USUCAPIÃO RURAL</h1>
                <p class="area-juridica">Direito Agrário - Regularização Fundiária</p>
            </header>
            
            <section class="partes">
                <h3>1. PARTES</h3>
                <div class="campo-form">
                    <label>Requerente(s):</label>
                    <textarea name="requerentes" rows="3" placeholder="Nome completo, RG, CPF, estado civil, profissão, endereço"></textarea>
                </div>
                <div class="campo-form">
                    <label>Requeridos:</label>
                    <textarea name="requeridos" rows="3" placeholder="Proprietários constantes do registro, confrontantes, Fazenda Pública"></textarea>
                </div>
            </section>
            
            <section class="imovel">
                <h3>2. DESCRIÇÃO DO IMÓVEL</h3>
                <div class="campo-form">
                    <label>Denominação:</label>
                    <input type="text" name="denominacao_imovel" placeholder="Nome da propriedade">
                </div>
                <div class="campo-form">
                    <label>Localização:</label>
                    <input type="text" name="localizacao_imovel" placeholder="Município, distrito, localidade">
                </div>
                <div class="campo-form">
                    <label>Área:</label>
                    <input type="text" name="area_imovel" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Confrontações:</label>
                    <textarea name="confrontacoes" rows="4" placeholder="Norte: ... Sul: ... Leste: ... Oeste: ..."></textarea>
                </div>
                <div class="campo-form">
                    <label>Matrícula/Registro:</label>
                    <input type="text" name="matricula_registro" placeholder="Se houver registro anterior">
                </div>
            </section>
            
            <section class="posse">
                <h3>3. CARACTERIZAÇÃO DA POSSE</h3>
                <div class="campo-form">
                    <label>Início da Posse:</label>
                    <input type="date" name="inicio_posse">
                </div>
                <div class="campo-form">
                    <label>Forma de Aquisição:</label>
                    <select name="forma_aquisicao">
                        <option value="">Selecione...</option>
                        <option value="ocupacao_direta">Ocupação Direta</option>
                        <option value="sucessao_causa_mortis">Sucessão Causa Mortis</option>
                        <option value="contrato_verbal">Contrato Verbal de Compra</option>
                        <option value="cessao_posse">Cessão de Posse</option>
                        <option value="outro">Outro</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Características da Posse:</label>
                    <div class="checkbox-group">
                        <label><input type="checkbox" name="posse_mansa"> Mansa</label>
                        <label><input type="checkbox" name="posse_pacifica"> Pacífica</label>
                        <label><input type="checkbox" name="posse_continua"> Contínua</label>
                        <label><input type="checkbox" name="posse_publica"> Pública</label>
                        <label><input type="checkbox" name="posse_boa_fe"> Boa-fé</label>
                    </div>
                </div>
            </section>
            
            <section class="atividade-rural">
                <h3>4. ATIVIDADE RURAL</h3>
                <div class="campo-form">
                    <label>Tipo de Exploração:</label>
                    <select name="tipo_exploracao">
                        <option value="">Selecione...</option>
                        <option value="agricultura">Agricultura</option>
                        <option value="pecuaria">Pecuária</option>
                        <option value="agricultura_pecuaria">Agricultura e Pecuária</option>
                        <option value="extrativismo">Extrativismo</option>
                        <option value="aquicultura">Aquicultura</option>
                        <option value="outro">Outro</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Descrição das Atividades:</label>
                    <textarea name="descricao_atividades" rows="4" placeholder="Detalhar as atividades desenvolvidas no imóvel"></textarea>
                </div>
                <div class="campo-form">
                    <label>Benfeitorias Realizadas:</label>
                    <textarea name="benfeitorias" rows="4" placeholder="Casa, currais, cercas, plantações, etc."></textarea>
                </div>
            </section>
            
            <section class="modalidade">
                <h3>5. MODALIDADE DE USUCAPIÃO</h3>
                <div class="campo-form">
                    <label>Tipo de Usucapião:</label>
                    <select name="modalidade_usucapiao">
                        <option value="">Selecione...</option>
                        <option value="pro_labore">Pro Labore (Art. 1.239 CC)</option>
                        <option value="especial_rural">Especial Rural (Art. 191 CF)</option>
                        <option value="extraordinario">Extraordinário (Art. 1.238 CC)</option>
                        <option value="ordinario">Ordinário (Art. 1.242 CC)</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Prazo Cumprido:</label>
                    <input type="number" name="prazo_cumprido" placeholder="Anos de posse">
                </div>
            </section>
            
            <section class="pedidos-usucapiao">
                <h3>6. PEDIDOS</h3>
                <div class="campo-form">
                    <label>Pedido Principal:</label>
                    <textarea name="pedido_principal_usucapiao" rows="3">Seja declarado o domínio do(s) requerente(s) sobre o imóvel rural descrito, por usucapião</textarea>
                </div>
                <div class="campo-form">
                    <label>Pedidos Acessórios:</label>
                    <textarea name="pedidos_acessorios" rows="3">Registro do título no Cartório de Registro de Imóveis competente</textarea>
                </div>
            </section>
            
            <footer class="template-footer">
                <div class="fundamentacao-legal">
                    <p><strong>Base Legal:</strong> Art. 191 da CF/88, Arts. 1.238, 1.239 e 1.242 do CC, CPC Arts. 246 e seguintes</p>
                </div>
                <div class="clausula-final">
                    <p><strong>Nestes termos, pede deferimento.</strong></p>
                    <p>Local, data</p>
                    <p>_________________________________</p>
                    <p>Advogado - OAB/UF nº</p>
                </div>
            </footer>
        </div>
        """

    def _template_memorial_rural(self) -> str:
        """Template para memorial descritivo rural"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">MEMORIAL DESCRITIVO - IMÓVEL RURAL</h1>
                <p class="area-juridica">Direito Agrário - Regularização Fundiária</p>
            </header>
            
            <section class="identificacao-memorial">
                <h3>1. IDENTIFICAÇÃO DO IMÓVEL</h3>
                <div class="campo-form">
                    <label>Denominação:</label>
                    <input type="text" name="denominacao_memorial" placeholder="Nome da propriedade">
                </div>
                <div class="campo-form">
                    <label>Município:</label>
                    <input type="text" name="municipio_memorial" placeholder="Município/UF">
                </div>
                <div class="campo-form">
                    <label>Comarca:</label>
                    <input type="text" name="comarca_memorial" placeholder="Comarca">
                </div>
                <div class="campo-form">
                    <label>Cartório de Registro:</label>
                    <input type="text" name="cartorio_memorial" placeholder="Cartório de Registro de Imóveis">
                </div>
            </section>
            
            <section class="area-memorial">
                <h3>2. ÁREA E DIMENSÕES</h3>
                <div class="campo-form">
                    <label>Área Total:</label>
                    <input type="text" name="area_total_memorial" placeholder="Ex: 50,00 hectares">
                </div>
                <div class="campo-form">
                    <label>Perímetro:</label>
                    <input type="text" name="perimetro_memorial" placeholder="Ex: 3.000,00 metros">
                </div>
            </section>
            
            <section class="confrontacoes-memorial">
                <h3>3. CONFRONTAÇÕES E DIVISAS</h3>
                <div class="campo-form">
                    <label>Norte:</label>
                    <textarea name="confrontacao_norte" rows="2" placeholder="Descrever confrontação norte com medidas lineares"></textarea>
                </div>
                <div class="campo-form">
                    <label>Sul:</label>
                    <textarea name="confrontacao_sul" rows="2" placeholder="Descrever confrontação sul com medidas lineares"></textarea>
                </div>
                <div class="campo-form">
                    <label>Leste:</label>
                    <textarea name="confrontacao_leste" rows="2" placeholder="Descrever confrontação leste com medidas lineares"></textarea>
                </div>
                <div class="campo-form">
                    <label>Oeste:</label>
                    <textarea name="confrontacao_oeste" rows="2" placeholder="Descrever confrontação oeste com medidas lineares"></textarea>
                </div>
            </section>
            
            <section class="vertices">
                <h3>4. VÉRTICES E COORDENADAS</h3>
                <div class="campo-form">
                    <label>Sistema de Coordenadas:</label>
                    <select name="sistema_coordenadas">
                        <option value="">Selecione...</option>
                        <option value="utm">UTM</option>
                        <option value="geograficas">Geográficas (Lat/Long)</option>
                        <option value="topograficas">Topográficas Locais</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Datum:</label>
                    <select name="datum">
                        <option value="">Selecione...</option>
                        <option value="SIRGAS2000">SIRGAS 2000</option>
                        <option value="SAD69">SAD 69</option>
                        <option value="WGS84">WGS 84</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Coordenadas dos Vértices:</label>
                    <textarea name="coordenadas_vertices" rows="6" placeholder="V1: X=000000 Y=0000000&#10;V2: X=000000 Y=0000000&#10;V3: X=000000 Y=0000000&#10;V4: X=000000 Y=0000000"></textarea>
                </div>
            </section>
            
            <section class="acesso-memorial">
                <h3>5. ACESSO AO IMÓVEL</h3>
                <div class="campo-form">
                    <label>Forma de Acesso:</label>
                    <textarea name="forma_acesso" rows="3" placeholder="Descrever como se chega ao imóvel (estradas, caminhos, etc.)"></textarea>
                </div>
                <div class="campo-form">
                    <label>Distância da Sede Municipal:</label>
                    <input type="text" name="distancia_sede" placeholder="Ex: 15 km">
                </div>
            </section>
            
            <section class="caracteristicas-fisicas">
                <h3>6. CARACTERÍSTICAS FÍSICAS</h3>
                <div class="campo-form">
                    <label>Topografia:</label>
                    <select name="topografia">
                        <option value="">Selecione...</option>
                        <option value="plana">Plana</option>
                        <option value="ondulada">Ondulada</option>
                        <option value="montanhosa">Montanhosa</option>
                        <option value="mista">Mista</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Tipo de Solo:</label>
                    <input type="text" name="tipo_solo" placeholder="Ex: Latossolo Vermelho">
                </div>
                <div class="campo-form">
                    <label>Recursos Hídricos:</label>
                    <textarea name="recursos_hidricos_memorial" rows="3" placeholder="Rios, córregos, nascentes, açudes"></textarea>
                </div>
                <div class="campo-form">
                    <label>Vegetação:</label>
                    <textarea name="vegetacao" rows="3" placeholder="Tipo de vegetação predominante"></textarea>
                </div>
            </section>
            
            <section class="uso-atual">
                <h3>7. USO ATUAL DO SOLO</h3>
                <div class="campo-form">
                    <label>Atividade Principal:</label>
                    <select name="atividade_principal_memorial">
                        <option value="">Selecione...</option>
                        <option value="agricultura">Agricultura</option>
                        <option value="pecuaria">Pecuária</option>
                        <option value="mista">Atividade Mista</option>
                        <option value="preservacao">Preservação</option>
                        <option value="nao_explorado">Não Explorado</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Benfeitorias Existentes:</label>
                    <textarea name="benfeitorias_memorial" rows="4" placeholder="Casa sede, galpões, currais, cercas, etc."></textarea>
                </div>
            </section>
            
            <footer class="template-footer">
                <div class="responsavel-tecnico">
                    <p><strong>Responsável Técnico:</strong></p>
                    <p>Nome: _________________________________</p>
                    <p>Profissão: _________________________________</p>
                    <p>Registro: _________________________________</p>
                    <p>Data: _________________________________</p>
                    <p>Assinatura: _________________________________</p>
                </div>
                <div class="observacoes">
                    <p><strong>Observações:</strong></p>
                    <p>- Este memorial deverá ser acompanhado de planta topográfica</p>
                    <p>- Coordenadas georreferenciadas conforme INCRA</p>
                    <p>- Atende às exigências da Lei 10.267/2001</p>
                </div>
            </footer>
        </div>
        """

    def _template_contestacao_desapropriacao(self) -> str:
        """Template para contestação de desapropriação"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">CONTESTAÇÃO - DESAPROPRIAÇÃO AGRÁRIA</h1>
                <p class="area-juridica">Direito Agrário - Desapropriação</p>
            </header>
            
            <section class="preliminares">
                <h3>1. PRELIMINARES</h3>
                <div class="campo-form">
                    <label>Tempestividade:</label>
                    <textarea name="tempestividade" rows="2">A presente contestação é tempestiva, conforme certidão de intimação em anexo.</textarea>
                </div>
                <div class="campo-form">
                    <label>Interesse de Agir:</label>
                    <textarea name="interesse_agir" rows="3" placeholder="Questionar eventual falta de interesse processual do expropriante"></textarea>
                </div>
                <div class="campo-form">
                    <label>Vícios Procedimentais:</label>
                    <textarea name="vicios_procedimentais" rows="4" placeholder="Apontar eventuais vícios no procedimento expropriatório"></textarea>
                </div>
            </section>
            
            <section class="merito-contestacao">
                <h3>2. MÉRITO</h3>
                <div class="campo-form">
                    <label>Improdutividade Contestada:</label>
                    <textarea name="improdutividade" rows="5" placeholder="Demonstrar que o imóvel É produtivo conforme índices do INCRA"></textarea>
                </div>
                <div class="campo-form">
                    <label>Função Social Cumprida:</label>
                    <textarea name="funcao_social" rows="5" placeholder="Demonstrar que o imóvel cumpre sua função social (art. 186, CF)"></textarea>
                </div>
                <div class="campo-form">
                    <label>Vícios no Decreto:</label>
                    <textarea name="vicios_decreto" rows="4" placeholder="Apontar eventuais vícios no decreto de desapropriação"></textarea>
                </div>
            </section>
            
            <section class="valor-indenizacao">
                <h3>3. VALOR DA INDENIZAÇÃO</h3>
                <div class="campo-form">
                    <label>Valor Oferecido:</label>
                    <input type="text" name="valor_oferecido" placeholder="R$ 0,00">
                </div>
                <div class="campo-form">
                    <label>Valor Justo Pleiteado:</label>
                    <input type="text" name="valor_pleiteado" placeholder="R$ 0,00">
                </div>
                <div class="campo-form">
                    <label>Critérios para Avaliação:</label>
                    <textarea name="criterios_avaliacao" rows="4" placeholder="Fundamentar critérios para avaliação justa (benfeitorias, localização, potencial produtivo)"></textarea>
                </div>
                <div class="campo-form">
                    <label>Benfeitorias Não Consideradas:</label>
                    <textarea name="benfeitorias_nao_consideradas" rows="4" placeholder="Listar benfeitorias não consideradas ou subavaliadas"></textarea>
                </div>
            </section>
            
            <section class="documentos-contestacao">
                <h3>4. DOCUMENTOS E PROVAS</h3>
                <div class="campo-form">
                    <label>Documentos Anexos:</label>
                    <textarea name="documentos_contestacao" rows="4" placeholder="Listar documentos que acompanham a contestação"></textarea>
                </div>
                <div class="campo-form">
                    <label>Provas a Produzir:</label>
                    <textarea name="provas_contestacao" rows="4" placeholder="Perícia técnica, testemunhal, documental"></textarea>
                </div>
                <div class="campo-form">
                    <label>Quesitos para Perícia:</label>
                    <textarea name="quesitos_pericia" rows="6" placeholder="Elaborar quesitos específicos para avaliação do imóvel"></textarea>
                </div>
            </section>
            
            <section class="pedidos-contestacao">
                <h3>5. PEDIDOS</h3>
                <div class="campo-form">
                    <label>Pedido Principal:</label>
                    <textarea name="pedido_principal_contestacao" rows="3">Seja julgada IMPROCEDENTE a ação de desapropriação</textarea>
                </div>
                <div class="campo-form">
                    <label>Pedido Subsidiário:</label>
                    <textarea name="pedido_subsidiario_contestacao" rows="3">Subsidiariamente, seja fixado valor justo para indenização</textarea>
                </div>
                <div class="campo-form">
                    <label>Pedidos Acessórios:</label>
                    <textarea name="pedidos_acessorios_contestacao" rows="3">Juros compensatórios, correção monetária, honorários periciais</textarea>
                </div>
            </section>
            
            <footer class="template-footer">
                <div class="fundamentacao-legal-contestacao">
                    <p><strong>Base Legal:</strong></p>
                    <ul>
                        <li>Art. 184-186 da Constituição Federal</li>
                        <li>Lei nº 8.629/93 (Lei da Reforma Agrária)</li>
                        <li>Lei Complementar nº 76/93</li>
                        <li>Decreto nº 9.311/18</li>
                        <li>Súmulas STF e STJ aplicáveis</li>
                    </ul>
                </div>
                <div class="clausula-final-contestacao">
                    <p><strong>Nestes termos, pede deferimento.</strong></p>
                    <p>Local, data</p>
                    <p>_________________________________</p>
                    <p>Advogado - OAB/UF nº</p>
                </div>
            </footer>
        </div>
        """

    def _template_titulacao_quilombola(self) -> str:
        """Template para titulação quilombola"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">PROCEDIMENTO DE TITULAÇÃO QUILOMBOLA</h1>
                <p class="area-juridica">Direito Agrário - Direitos Quilombolas</p>
            </header>
            
            <section class="identificacao-quilombola">
                <h3>1. IDENTIFICAÇÃO DA COMUNIDADE</h3>
                <div class="campo-form">
                    <label>Nome da Comunidade:</label>
                    <input type="text" name="nome_comunidade" placeholder="Comunidade Quilombola">
                </div>
                <div class="campo-form">
                    <label>Localização:</label>
                    <input type="text" name="localizacao_quilombola" placeholder="Município/Estado">
                </div>
                <div class="campo-form">
                    <label>Número de Famílias:</label>
                    <input type="number" name="numero_familias_quilombola" placeholder="Quantidade de famílias">
                </div>
                <div class="campo-form">
                    <label>Certificação FCP:</label>
                    <input type="text" name="certificacao_fcp" placeholder="Número do certificado da Fundação Cultural Palmares">
                </div>
            </section>
            
            <section class="territorio-quilombola">
                <h3>2. TERRITÓRIO REIVINDICADO</h3>
                <div class="campo-form">
                    <label>Área Total:</label>
                    <input type="text" name="area_quilombola" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Descrição do Território:</label>
                    <textarea name="descricao_territorio" rows="4" placeholder="Descrever limites e características do território"></textarea>
                </div>
                <div class="campo-form">
                    <label>Histórico de Ocupação:</label>
                    <textarea name="historico_ocupacao" rows="6" placeholder="Relatar histórico da ocupação quilombola na área"></textarea>
                </div>
            </section>
            
            <section class="fundamentacao-quilombola">
                <h3>3. FUNDAMENTAÇÃO ANTROPOLÓGICA</h3>
                <div class="campo-form">
                    <label>Relatório Antropológico:</label>
                    <textarea name="relatorio_antropologico" rows="5" placeholder="Resumo das conclusões do relatório técnico de identificação"></textarea>
                </div>
                <div class="campo-form">
                    <label>Critérios de Autoidentificação:</label>
                    <textarea name="autoidentificacao" rows="4" placeholder="Como a comunidade se reconhece como quilombola"></textarea>
                </div>
                <div class="campo-form">
                    <label>Práticas Culturais:</label>
                    <textarea name="praticas_culturais" rows="4" placeholder="Tradições, práticas culturais específicas"></textarea>
                </div>
            </section>
            
            <section class="situacao-juridica-quilombola">
                <h3>4. SITUAÇÃO JURÍDICA ATUAL</h3>
                <div class="campo-form">
                    <label>Propriedades Incidentes:</label>
                    <textarea name="propriedades_incidentes" rows="4" placeholder="Propriedades privadas que incidem sobre o território"></textarea>
                </div>
                <div class="campo-form">
                    <label>Conflitos Existentes:</label>
                    <textarea name="conflitos_existentes" rows="4" placeholder="Descrever conflitos fundiários na área"></textarea>
                </div>
                <div class="campo-form">
                    <label>Órgãos Envolvidos:</label>
                    <textarea name="orgaos_envolvidos" rows="3" placeholder="INCRA, FCP, ICMBio, IBAMA, etc."></textarea>
                </div>
            </section>
            
            <section class="pedidos-quilombola">
                <h3>5. PEDIDOS</h3>
                <div class="campo-form">
                    <label>Reconhecimento do Território:</label>
                    <textarea name="reconhecimento_territorio" rows="3">Seja reconhecido o território tradicionalmente ocupado pela comunidade quilombola</textarea>
                </div>
                <div class="campo-form">
                    <label>Titulação Coletiva:</label>
                    <textarea name="titulacao_coletiva" rows="3">Seja expedido título coletivo em nome da comunidade</textarea>
                </div>
                <div class="campo-form">
                    <label>Desintrusão:</label>
                    <textarea name="desintrusao" rows="3">Seja promovida a desintrusão de terceiros não quilombolas</textarea>
                </div>
                <div class="campo-form">
                    <label>Indenização:</label>
                    <textarea name="indenizacao_quilombola" rows="3">Sejam indenizados ocupantes de boa-fé, quando cabível</textarea>
                </div>
            </section>
            
            <section class="cronograma-quilombola">
                <h3>6. CRONOGRAMA DE ATIVIDADES</h3>
                <div class="campo-form">
                    <label>Etapas do Processo:</label>
                    <textarea name="etapas_processo" rows="6" placeholder="1. Relatório de identificação&#10;2. Relatório antropológico&#10;3. Consulta pública&#10;4. Decreto presidencial&#10;5. Desintrusão&#10;6. Titulação"></textarea>
                </div>
                <div class="campo-form">
                    <label>Prazos Estimados:</label>
                    <textarea name="prazos_estimados" rows="4" placeholder="Estimativa de prazos para cada etapa"></textarea>
                </div>
            </section>
            
            <footer class="template-footer">
                <div class="base-legal-quilombola">
                    <p><strong>Base Legal:</strong></p>
                    <ul>
                        <li>Art. 68 do ADCT da Constituição Federal</li>
                        <li>Decreto nº 4.887/2003</li>
                        <li>IN INCRA nº 57/2009</li>
                        <li>Convenção 169 da OIT</li>
                        <li>Lei nº 7.668/88 (FCP)</li>
                    </ul>
                </div>
                <div class="assinatura-quilombola">
                    <p>Data: _________________</p>
                    <p>Responsável: _________________________________</p>
                    <p>Representante da Comunidade: _________________________________</p>
                </div>
            </footer>
        </div>
        """

    def _template_demarcacao_indigena(self) -> str:
        """Template para demarcação indígena"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">PROCESSO DE DEMARCAÇÃO DE TERRAS INDÍGENAS</h1>
                <p class="area-juridica">Direito Agrário - Direitos Indígenas</p>
            </header>
            
            <section class="identificacao-indigena">
                <h3>1. IDENTIFICAÇÃO</h3>
                <div class="campo-form">
                    <label>Nome da Terra Indígena:</label>
                    <input type="text" name="nome_terra_indigena" placeholder="Denominação da terra indígena">
                </div>
                <div class="campo-form">
                    <label>Etnia(s):</label>
                    <input type="text" name="etnias" placeholder="Etnias que ocupam o território">
                </div>
                <div class="campo-form">
                    <label>População:</label>
                    <input type="number" name="populacao_indigena" placeholder="Número de indígenas">
                </div>
                <div class="campo-form">
                    <label>Localização:</label>
                    <input type="text" name="localizacao_indigena" placeholder="Estados e municípios abrangidos">
                </div>
            </section>
            
            <section class="territorio-indigena">
                <h3>2. TERRITÓRIO TRADICIONAL</h3>
                <div class="campo-form">
                    <label>Área Reivindicada:</label>
                    <input type="text" name="area_reivindicada" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Limites Tradicionais:</label>
                    <textarea name="limites_tradicionais" rows="4" placeholder="Descrição dos limites do território tradicional"></textarea>
                </div>
                <div class="campo-form">
                    <label>Ocupação Tradicional:</label>
                    <textarea name="ocupacao_tradicional" rows="6" placeholder="Histórico da ocupação tradicional indígena"></textarea>
                </div>
            </section>
            
            <section class="estudos-tecnicos">
                <h3>3. ESTUDOS TÉCNICOS</h3>
                <div class="campo-form">
                    <label>Estudo Antropológico:</label>
                    <textarea name="estudo_antropologico" rows="4" placeholder="Resumo das conclusões do estudo antropológico"></textarea>
                </div>
                <div class="campo-form">
                    <label>Estudo Histórico:</label>
                    <textarea name="estudo_historico" rows="4" placeholder="Fundamentação histórica da ocupação"></textarea>
                </div>
                <div class="campo-form">
                    <label>Levantamento Fundiário:</label>
                    <textarea name="levantamento_fundiario" rows="4" placeholder="Situação fundiária da área reivindicada"></textarea>
                </div>
                <div class="campo-form">
                    <label>Estudo Ambiental:</label>
                    <textarea name="estudo_ambiental" rows="4" placeholder="Características ambientais do território"></textarea>
                </div>
            </section>
            
            <section class="fase-processo">
                <h3>4. FASE ATUAL DO PROCESSO</h3>
                <div class="campo-form">
                    <label>Etapa Atual:</label>
                    <select name="etapa_atual">
                        <option value="">Selecione...</option>
                        <option value="identificacao">Em Identificação</option>
                        <option value="aprovacao_funai">Aprovação FUNAI</option>
                        <option value="contestacoes">Prazo de Contestações</option>
                        <option value="declaracao_mj">Declaração do Ministério da Justiça</option>
                        <option value="homologacao">Homologação Presidencial</option>
                        <option value="registro">Registro no CRI e SPU</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Atos Administrativos:</label>
                    <textarea name="atos_administrativos" rows="4" placeholder="Listar portarias, despachos e decisões já proferidas"></textarea>
                </div>
            </section>
            
            <section class="conflitos-indigena">
                <h3>5. CONFLITOS E CONTESTAÇÕES</h3>
                <div class="campo-form">
                    <label>Ocupantes Não-Indígenas:</label>
                    <textarea name="ocupantes_nao_indigenas" rows="4" placeholder="Identificar ocupantes não-indígenas na área"></textarea>
                </div>
                <div class="campo-form">
                    <label>Contestações Apresentadas:</label>
                    <textarea name="contestacoes_apresentadas" rows="4" placeholder="Resumir principais contestações ao processo"></textarea>
                </div>
                <div class="campo-form">
                    <label>Ações Judiciais:</label>
                    <textarea name="acoes_judiciais" rows="4" placeholder="Ações judiciais relacionadas ao processo demarcatório"></textarea>
                </div>
            </section>
            
            <section class="medidas-necessarias">
                <h3>6. MEDIDAS NECESSÁRIAS</h3>
                <div class="campo-form">
                    <label>Proteção da Terra:</label>
                    <textarea name="protecao_terra" rows="3" placeholder="Medidas de proteção necessárias"></textarea>
                </div>
                <div class="campo-form">
                    <label>Retirada de Invasores:</label>
                    <textarea name="retirada_invasores" rows="3" placeholder="Estratégia para retirada de ocupantes não-indígenas"></textarea>
                </div>
                <div class="campo-form">
                    <label>Indenizações:</label>
                    <textarea name="indenizacoes_indigena" rows="3" placeholder="Previsão de indenizações por benfeitorias de boa-fé"></textarea>
                </div>
            </section>
            
            <footer class="template-footer">
                <div class="base-legal-indigena">
                    <p><strong>Base Legal:</strong></p>
                    <ul>
                        <li>Arts. 231 e 232 da Constituição Federal</li>
                        <li>Lei nº 6.001/73 (Estatuto do Índio)</li>
                        <li>Decreto nº 1.775/96</li>
                        <li>Portaria MJ nº 14/96</li>
                        <li>Convenção 169 da OIT</li>
                    </ul>
                </div>
                <div class="responsaveis-processo">
                    <p><strong>Equipe Técnica:</strong></p>
                    <p>Coordenador: _________________________________</p>
                    <p>Antropólogo: _________________________________</p>
                    <p>Historiador: _________________________________</p>
                    <p>Advogado: _________________________________</p>
                    <p>Data: _________________________________</p>
                </div>
            </footer>
        </div>
        """

    def _template_contrato_pronaf(self) -> str:
        """Template para contrato PRONAF"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">CONTRATO DE CRÉDITO RURAL - PRONAF</h1>
                <p class="area-juridica">Direito Agrário - Agricultura Familiar</p>
            </header>
            
            <section class="partes-pronaf">
                <h3>1. PARTES CONTRATANTES</h3>
                <div class="campo-form">
                    <label>Mutuário:</label>
                    <textarea name="mutuario_pronaf" rows="3" placeholder="Nome completo, RG, CPF, estado civil, endereço"></textarea>
                </div>
                <div class="campo-form">
                    <label>Instituição Financeira:</label>
                    <textarea name="instituicao_financeira" rows="2" placeholder="Nome da instituição financeira, agência"></textarea>
                </div>
            </section>
            
            <section class="modalidade-pronaf">
                <h3>2. MODALIDADE DE CRÉDITO</h3>
                <div class="campo-form">
                    <label>Linha PRONAF:</label>
                    <select name="linha_pronaf">
                        <option value="">Selecione...</option>
                        <option value="custeio">PRONAF Custeio</option>
                        <option value="investimento">PRONAF Investimento</option>
                        <option value="mais_alimentos">PRONAF Mais Alimentos</option>
                        <option value="mulher">PRONAF Mulher</option>
                        <option value="jovem">PRONAF Jovem</option>
                        <option value="agroindústria">PRONAF Agroindústria</option>
                        <option value="eco">PRONAF Eco</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Valor do Crédito:</label>
                    <input type="text" name="valor_credito" placeholder="R$ 0,00">
                </div>
                <div class="campo-form">
                    <label>Taxa de Juros:</label>
                    <input type="text" name="taxa_juros" placeholder="% ao ano">
                </div>
                <div class="campo-form">
                    <label>Prazo de Pagamento:</label>
                    <input type="text" name="prazo_pagamento" placeholder="Número de parcelas/meses">
                </div>
            </section>
            
            <section class="finalidade-credito">
                <h3>3. FINALIDADE DO CRÉDITO</h3>
                <div class="campo-form">
                    <label>Projeto Financiado:</label>
                    <textarea name="projeto_financiado" rows="4" placeholder="Descrever detalhadamente o projeto a ser financiado"></textarea>
                </div>
                <div class="campo-form">
                    <label>Culturas/Atividades:</label>
                    <textarea name="culturas_atividades" rows="3" placeholder="Especificar culturas ou atividades pecuárias"></textarea>
                </div>
                <div class="campo-form">
                    <label>Área Cultivada:</label>
                    <input type="text" name="area_cultivada" placeholder="Área em hectares">
                </div>
            </section>
            
            <section class="garantias-pronaf">
                <h3>4. GARANTIAS</h3>
                <div class="campo-form">
                    <label>Tipo de Garantia:</label>
                    <select name="tipo_garantia">
                        <option value="">Selecione...</option>
                        <option value="penhor_rural">Penhor Rural</option>
                        <option value="hipoteca_rural">Hipoteca Rural</option>
                        <option value="aval">Aval</option>
                        <option value="fianca">Fiança</option>
                        <option value="fgd">Fundo de Garantia (FGD)</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Descrição da Garantia:</label>
                    <textarea name="descricao_garantia" rows="4" placeholder="Descrever detalhadamente a garantia oferecida"></textarea>
                </div>
                <div class="campo-form">
                    <label>Avalista/Fiador:</label>
                    <textarea name="avalista_fiador" rows="2" placeholder="Se aplicável, dados do avalista ou fiador"></textarea>
                </div>
            </section>
            
            <section class="condicoes-especiais">
                <h3>5. CONDIÇÕES ESPECIAIS</h3>
                <div class="campo-form">
                    <label>Rebate:</label>
                    <input type="text" name="rebate" placeholder="Percentual de desconto por adimplência">
                </div>
                <div class="campo-form">
                    <label>Carência:</label>
                    <input type="text" name="carencia" placeholder="Período de carência em meses">
                </div>
                <div class="campo-form">
                    <label>Bônus de Adimplência:</label>
                    <input type="text" name="bonus_adimplencia" placeholder="Percentual de bônus">
                </div>
            </section>
            
            <section class="obrigacoes-mutuario">
                <h3>6. OBRIGAÇÕES DO MUTUÁRIO</h3>
                <div class="campo-form">
                    <label>Aplicação dos Recursos:</label>
                    <textarea name="aplicacao_recursos" rows="3">Os recursos deverão ser aplicados exclusivamente na finalidade contratada</textarea>
                </div>
                <div class="campo-form">
                    <label>Comprovação de Aplicação:</label>
                    <textarea name="comprovacao_aplicacao" rows="3">Apresentar comprovantes de aplicação dos recursos conforme exigido</textarea>
                </div>
                <div class="campo-form">
                    <label>Assistência Técnica:</label>
                    <textarea name="assistencia_tecnica" rows="3">Contratar assistência técnica quando exigida pelo programa</textarea>
                </div>
                <div class="campo-form">
                    <label>Seguro Rural:</label>
                    <textarea name="seguro_rural_pronaf" rows="2">Contratar seguro rural quando disponível e exigido</textarea>
                </div>
            </section>
            
            <section class="pagamento">
                <h3>7. FORMA DE PAGAMENTO</h3>
                <div class="campo-form">
                    <label>Data de Vencimento:</label>
                    <input type="date" name="data_vencimento">
                </div>
                <div class="campo-form">
                    <label>Local de Pagamento:</label>
                    <input type="text" name="local_pagamento" placeholder="Agência bancária">
                </div>
                <div class="campo-form">
                    <label>Forma de Cobrança:</label>
                    <select name="forma_cobranca">
                        <option value="">Selecione...</option>
                        <option value="debito_automatico">Débito Automático</option>
                        <option value="boleto">Boleto Bancário</option>
                        <option value="agencia">Pagamento na Agência</option>
                    </select>
                </div>
            </section>
            
            <footer class="template-footer">
                <div class="clausulas-gerais">
                    <p><strong>Cláusulas Gerais:</strong></p>
                    <p>- O presente contrato obedece às normas do Manual de Crédito Rural (MCR)</p>
                    <p>- Aplicam-se as condições específicas do PRONAF vigentes</p>
                    <p>- O descumprimento das obrigações ensejará o vencimento antecipado</p>
                </div>
                <div class="assinaturas-contrato">
                    <p>Local e data: ________________</p>
                    <br>
                    <p>_________________________________</p>
                    <p>Mutuário</p>
                    <br>
                    <p>_________________________________</p>
                    <p>Instituição Financeira</p>
                    <br>
                    <p>Testemunhas: _________________ _________________</p>
                </div>
            </footer>
        </div>
        """

    def _template_car(self) -> str:
        """Template para Cadastro Ambiental Rural"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">CADASTRO AMBIENTAL RURAL - CAR</h1>
                <p class="area-juridica">Direito Agrário - Meio Ambiente Rural</p>
            </header>
            
            <section class="identificacao-car">
                <h3>1. IDENTIFICAÇÃO DO IMÓVEL</h3>
                <div class="campo-form">
                    <label>Denominação:</label>
                    <input type="text" name="denominacao_car" placeholder="Nome da propriedade">
                </div>
                <div class="campo-form">
                    <label>CPF/CNPJ do Proprietário:</label>
                    <input type="text" name="cpf_cnpj_car" placeholder="000.000.000-00">
                </div>
                <div class="campo-form">
                    <label>Número do CAR:</label>
                    <input type="text" name="numero_car" placeholder="Número do registro no CAR">
                </div>
                <div class="campo-form">
                    <label>Município:</label>
                    <input type="text" name="municipio_car" placeholder="Município/UF">
                </div>
                <div class="campo-form">
                    <label>Área Total:</label>
                    <input type="text" name="area_total_car" placeholder="Área em hectares">
                </div>
            </section>
            
            <section class="areas-app">
                <h3>2. ÁREAS DE PRESERVAÇÃO PERMANENTE - APP</h3>
                <div class="campo-form">
                    <label>APP Total:</label>
                    <input type="text" name="app_total" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>APP Preservada:</label>
                    <input type="text" name="app_preservada" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>APP a Recuperar:</label>
                    <input type="text" name="app_recuperar" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Tipos de APP:</label>
                    <div class="checkbox-group">
                        <label><input type="checkbox" name="app_nascente"> Nascente</label>
                        <label><input type="checkbox" name="app_rio"> Curso d'água</label>
                        <label><input type="checkbox" name="app_lago"> Lago/Lagoa</label>
                        <label><input type="checkbox" name="app_encosta"> Encosta</label>
                        <label><input type="checkbox" name="app_topo_morro"> Topo de morro</label>
                    </div>
                </div>
            </section>
            
            <section class="reserva-legal">
                <h3>3. RESERVA LEGAL</h3>
                <div class="campo-form">
                    <label>Percentual Exigido:</label>
                    <select name="percentual_rl">
                        <option value="">Selecione...</option>
                        <option value="80">80% (Amazônia Legal - floresta)</option>
                        <option value="35">35% (Amazônia Legal - cerrado)</option>
                        <option value="20">20% (Demais regiões)</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Área de RL Exigida:</label>
                    <input type="text" name="rl_exigida" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Área de RL Existente:</label>
                    <input type="text" name="rl_existente" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Situação da RL:</label>
                    <select name="situacao_rl">
                        <option value="">Selecione...</option>
                        <option value="preservada">Totalmente Preservada</option>
                        <option value="parcial">Parcialmente Preservada</option>
                        <option value="degradada">Degradada</option>
                        <option value="inexistente">Inexistente</option>
                    </select>
                </div>
            </section>
            
            <section class="uso-solo">
                <h3>4. USO DO SOLO</h3>
                <div class="campo-form">
                    <label>Área de Vegetação Nativa:</label>
                    <input type="text" name="vegetacao_nativa" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Área Agrícola:</label>
                    <input type="text" name="area_agricola" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Área de Pastagem:</label>
                    <input type="text" name="area_pastagem" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Área com Silvicultura:</label>
                    <input type="text" name="area_silvicultura" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Área de Infraestrutura:</label>
                    <input type="text" name="area_infraestrutura" placeholder="Área em hectares">
                </div>
            </section>
            
            <section class="recursos-hidricos-car">
                <h3>5. RECURSOS HÍDRICOS</h3>
                <div class="campo-form">
                    <label>Corpos d'Água:</label>
                    <textarea name="corpos_agua" rows="4" placeholder="Rios, córregos, nascentes, lagos existentes no imóvel"></textarea>
                </div>
                <div class="campo-form">
                    <label>Outorgas de Uso:</label>
                    <textarea name="outorgas_uso" rows="3" placeholder="Outorgas de captação, irrigação ou outros usos"></textarea>
                </div>
                <div class="campo-form">
                    <label>Sistemas de Irrigação:</label>
                    <textarea name="sistemas_irrigacao" rows="3" placeholder="Descrever sistemas de irrigação existentes"></textarea>
                </div>
            </section>
            
            <section class="passivos-ambientais">
                <h3>6. PASSIVOS AMBIENTAIS</h3>
                <div class="campo-form">
                    <label>APP Degradada:</label>
                    <input type="text" name="app_degradada" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>RL Degradada:</label>
                    <input type="text" name="rl_degradada" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Plano de Recuperação:</label>
                    <textarea name="plano_recuperacao" rows="4" placeholder="Descrever plano de recuperação de áreas degradadas"></textarea>
                </div>
                <div class="campo-form">
                    <label>Cronograma de Recuperação:</label>
                    <textarea name="cronograma_recuperacao" rows="4" placeholder="Prazos e etapas para recuperação"></textarea>
                </div>
            </section>
            
            <section class="compromissos">
                <h3>7. COMPROMISSOS E RESPONSABILIDADES</h3>
                <div class="campo-form">
                    <label>Manutenção da RL:</label>
                    <textarea name="manutencao_rl" rows="2">Compromete-se a manter e preservar a Reserva Legal</textarea>
                </div>
                <div class="campo-form">
                    <label>Recuperação de APP:</label>
                    <textarea name="recuperacao_app" rows="2">Compromete-se a recuperar as APPs degradadas conforme cronograma</textarea>
                </div>
                <div class="campo-form">
                    <label>Atualização do CAR:</label>
                    <textarea name="atualizacao_car" rows="2">Compromete-se a manter o CAR atualizado</textarea>
                </div>
            </section>
            
            <footer class="template-footer">
                <div class="base-legal-car">
                    <p><strong>Base Legal:</strong></p>
                    <ul>
                        <li>Lei nº 12.651/2012 (Código Florestal)</li>
                        <li>Decreto nº 7.830/2012</li>
                        <li>IN MMA nº 2/2014</li>
                        <li>Portaria MMA nº 288/2013</li>
                    </ul>
                </div>
                <div class="declaracao-veracidade">
                    <p><strong>Declaração de Veracidade:</strong></p>
                    <p>Declaro que as informações prestadas são verdadeiras e assumo total responsabilidade pelas mesmas.</p>
                    <br>
                    <p>Local e data: ________________</p>
                    <p>_________________________________</p>
                    <p>Proprietário/Possuidor Rural</p>
                    <p>CPF: ________________</p>
                </div>
            </footer>
        </div>
        """

    def _template_arrendamento_rural(self) -> str:
        """Template para contrato de arrendamento rural"""
        return """
        <div class="template-agrario" style="border-left: 4px solid #6d3501;">
            <header class="template-header">
                <h1 style="color: #6d3501;">CONTRATO DE ARRENDAMENTO RURAL</h1>
                <p class="area-juridica">Direito Agrário - Contratos Rurais</p>
            </header>
            
            <section class="partes-arrendamento">
                <h3>1. PARTES CONTRATANTES</h3>
                <div class="campo-form">
                    <label>ARRENDADOR:</label>
                    <textarea name="arrendador" rows="3" placeholder="Nome completo, RG, CPF, estado civil, profissão, endereço"></textarea>
                </div>
                <div class="campo-form">
                    <label>ARRENDATÁRIO:</label>
                    <textarea name="arrendatario" rows="3" placeholder="Nome completo, RG, CPF, estado civil, profissão, endereço"></textarea>
                </div>
            </section>
            
            <section class="objeto-arrendamento">
                <h3>2. OBJETO DO CONTRATO</h3>
                <div class="campo-form">
                    <label>Imóvel Rural:</label>
                    <input type="text" name="imovel_rural" placeholder="Denominação da propriedade">
                </div>
                <div class="campo-form">
                    <label>Localização:</label>
                    <input type="text" name="localizacao_arrendamento" placeholder="Município, distrito, localidade">
                </div>
                <div class="campo-form">
                    <label>Área Arrendada:</label>
                    <input type="text" name="area_arrendada" placeholder="Área em hectares">
                </div>
                <div class="campo-form">
                    <label>Matrícula/Registro:</label>
                    <input type="text" name="matricula_arrendamento" placeholder="Número da matrícula no registro de imóveis">
                </div>
                <div class="campo-form">
                    <label>Confrontações:</label>
                    <textarea name="confrontacoes_arrendamento" rows="4" placeholder="Norte: ... Sul: ... Leste: ... Oeste: ..."></textarea>
                </div>
            </section>
            
            <section class="finalidade-arrendamento">
                <h3>3. FINALIDADE DO ARRENDAMENTO</h3>
                <div class="campo-form">
                    <label>Atividade Principal:</label>
                    <select name="atividade_principal_arrendamento">
                        <option value="">Selecione...</option>
                        <option value="agricultura">Agricultura</option>
                        <option value="pecuaria">Pecuária</option>
                        <option value="mista">Atividade Mista</option>
                        <option value="silvicultura">Silvicultura</option>
                        <option value="aquicultura">Aquicultura</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Culturas/Criações:</label>
                    <textarea name="culturas_criacoes" rows="3" placeholder="Especificar culturas agrícolas ou criações permitidas"></textarea>
                </div>
                <div class="campo-form">
                    <label>Restrições de Uso:</label>
                    <textarea name="restricoes_uso" rows="3" placeholder="Eventuais restrições ao uso da propriedade"></textarea>
                </div>
            </section>
            
            <section class="prazo-arrendamento">
                <h3>4. PRAZO</h3>
                <div class="campo-form">
                    <label>Data de Início:</label>
                    <input type="date" name="data_inicio_arrendamento">
                </div>
                <div class="campo-form">
                    <label>Data de Término:</label>
                    <input type="date" name="data_termino_arrendamento">
                </div>
                <div class="campo-form">
                    <label>Duração:</label>
                    <input type="text" name="duracao_arrendamento" placeholder="Ex: 3 anos">
                </div>
                <div class="campo-form">
                    <label>Renovação:</label>
                    <select name="renovacao_arrendamento">
                        <option value="">Selecione...</option>
                        <option value="automatica">Renovação Automática</option>
                        <option value="acordo">Por Acordo das Partes</option>
                        <option value="nao_renovavel">Não Renovável</option>
                    </select>
                </div>
            </section>
            
            <section class="pagamento-arrendamento">
                <h3>5. PAGAMENTO</h3>
                <div class="campo-form">
                    <label>Forma de Pagamento:</label>
                    <select name="forma_pagamento_arrendamento">
                        <option value="">Selecione...</option>
                        <option value="dinheiro">Pagamento em Dinheiro</option>
                        <option value="produto">Pagamento em Produto</option>
                        <option value="misto">Pagamento Misto</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Valor/Quantidade:</label>
                    <input type="text" name="valor_arrendamento" placeholder="Valor em R$ ou quantidade do produto">
                </div>
                <div class="campo-form">
                    <label>Periodicidade:</label>
                    <select name="periodicidade_pagamento">
                        <option value="">Selecione...</option>
                        <option value="anual">Anual</option>
                        <option value="semestral">Semestral</option>
                        <option value="safra">Por Safra</option>
                        <option value="mensal">Mensal</option>
                    </select>
                </div>
                <div class="campo-form">
                    <label>Data de Vencimento:</label>
                    <input type="text" name="vencimento_arrendamento" placeholder="Ex: 30 de junho de cada ano">
                </div>
            </section>
            
            <section class="obrigacoes-arrendador">
                <h3>6. OBRIGAÇÕES DO ARRENDADOR</h3>
                <div class="campo-form">
                    <label>Entrega do Imóvel:</label>
                    <textarea name="entrega_imovel" rows="2">Entregar o imóvel em condições de uso</textarea>
                </div>
                <div class="campo-form">
                    <label>Manutenção de Benfeitorias:</label>
                    <textarea name="manutencao_benfeitorias" rows="2">Manter benfeitorias necessárias em bom estado</textarea>
                </div>
                <div class="campo-form">
                    <label>Garantia de Uso Pacífico:</label>
                    <textarea name="uso_pacifico" rows="2">Garantir o uso pacífico da propriedade</textarea>
                </div>
            </section>
            
            <section class="obrigacoes-arrendatario">
                <h3>7. OBRIGAÇÕES DO ARRENDATÁRIO</h3>
                <div class="campo-form">
                    <label>Pagamento Pontual:</label>
                    <textarea name="pagamento_pontual" rows="2">Efetuar pagamento nas datas convencionadas</textarea>
                </div>
                <div class="campo-form">
                    <label>Conservação da Propriedade:</label>
                    <textarea name="conservacao_propriedade" rows="2">Conservar a propriedade e suas benfeitorias</textarea>
                </div>
                <div class="campo-form">
                    <label>Uso Adequado:</label>
                    <textarea name="uso_adequado" rows="2">Usar a propriedade conforme sua destinação</textarea>
                </div>
                <div class="campo-form">
                    <label>Restituição:</label>
                    <textarea name="restituicao" rows="2">Restituir o imóvel ao final do contrato</textarea>
                </div>
            </section>
            
            <section class="benfeitorias-arrendamento">
                <h3>8. BENFEITORIAS</h3>
                <div class="campo-form">
                    <label>Benfeitorias Necessárias:</label>
                    <textarea name="benfeitorias_necessarias" rows="3">Indenizáveis pelo arrendador</textarea>
                </div>
                <div class="campo-form">
                    <label>Benfeitorias Úteis:</label>
                    <textarea name="benfeitorias_uteis" rows="3">Dependem de autorização prévia para indenização</textarea>
                </div>
                <div class="campo-form">
                    <label>Benfeitorias Voluptuárias:</label>
                    <textarea name="benfeitorias_voluptuarias" rows="3">Não indenizáveis, podendo ser levantadas</textarea>
                </div>
            </section>
            
            <section class="rescisao-arrendamento">
                <h3>9. RESCISÃO</h3>
                <div class="campo-form">
                    <label>Causas de Rescisão:</label>
                    <textarea name="causas_rescisao" rows="4" placeholder="Inadimplemento, uso inadequado, descumprimento de cláusulas"></textarea>
                </div>
                <div class="campo-form">
                    <label>Multa por Rescisão:</label>
                    <input type="text" name="multa_rescisao" placeholder="Valor da multa">
                </div>
            </section>
            
            <footer class="template-footer">
                <div class="clausulas-gerais-arrendamento">
                    <p><strong>Cláusulas Gerais:</strong></p>
                    <p>- Aplicam-se as disposições dos arts. 48 a 95 do Estatuto da Terra</p>
                    <p>- Lei nº 4.947/66 e demais normas pertinentes</p>
                    <p>- Foro da comarca do imóvel para questões judiciais</p>
                </div>
                <div class="assinaturas-arrendamento">
                    <p>Local e data: ________________</p>
                    <br>
                    <p>_________________________________</p>
                    <p>ARRENDADOR</p>
                    <br>
                    <p>_________________________________</p>
                    <p>ARRENDATÁRIO</p>
                    <br>
                    <p>Testemunhas:</p>
                    <p>1. _________________ 2. _________________</p>
                </div>
            </footer>
        </div>
        """

    def get_agente_by_especialidade(self, especialidade: str) -> Optional[Dict]:
        """Retorna agente por especialidade"""
        if not self.conn:
            return None
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM agente_juridico 
                WHERE especialidade = %s AND area_juridica = 'Direito Agrário' AND ativo = true
            """, (especialidade,))
            
            result = cursor.fetchone()
            cursor.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar agente: {e}")
            return None

    def listar_agentes_agrarios(self) -> List[Dict]:
        """Lista todos os agentes de Direito Agrário"""
        if not self.conn:
            return []
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM agente_juridico 
                WHERE area_juridica = 'Direito Agrário' AND ativo = true
                ORDER BY nome
            """)
            
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar agentes: {e}")
            return []

    def processar_consulta(self, consulta: str, especialidade: str = None) -> Dict[str, Any]:
        """Processa consulta jurídica agrária"""
        try:
            # Se especialidade não especificada, tentar identificar automaticamente
            if not especialidade:
                especialidade = self._identificar_especialidade(consulta)
            
            # Buscar agente especializado
            agente = self.get_agente_by_especialidade(especialidade)
            
            if not agente:
                return {
                    "erro": "Especialista não encontrado",
                    "especialidade_sugerida": especialidade
                }
            
            # Processar consulta com o agente
            resposta = self._processar_com_agente(consulta, agente)
            
            return {
                "agente": agente["nome"],
                "especialidade": especialidade,
                "resposta": resposta,
                "templates_sugeridos": self._sugerir_templates(especialidade)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar consulta: {e}")
            return {"erro": "Erro interno no processamento"}

    def _identificar_especialidade(self, consulta: str) -> str:
        """Identifica especialidade baseada na consulta"""
        consulta_lower = consulta.lower()
        
        # Palavras-chave por especialidade
        mapa_keywords = {
            "reforma_agraria": ["reforma agrária", "assentamento", "redistribuição"],
            "regularizacao_fundiaria": ["regularização", "título", "usucapião rural"],
            "desapropriacao": ["desapropriação", "indenização", "produtividade"],
            "quilombolas": ["quilombola", "território tradicional", "comunidade"],
            "indigenas": ["indígena", "demarcação", "terra indígena"],
            "agricultura_familiar": ["agricultura familiar", "pronaf", "pequeno produtor"],
            "meio_ambiente_rural": ["ambiental", "car", "código florestal"],
            "contratos_rurais": ["arrendamento", "parceria", "contrato rural"],
            "agronegocio": ["agronegócio", "cooperativa", "grande propriedade"],
            "trabalho_rural": ["trabalhador rural", "trabalho escravo", "clt rural"],
            "tributacao_rural": ["itr", "tributação rural", "imposto"],
            "agua_irrigacao": ["água", "irrigação", "recursos hídricos"],
            "credito_financiamento": ["crédito rural", "financiamento", "banco"],
            "seguro_rural": ["seguro rural", "proagro", "indenização"],
            "tecnologia_rural": ["tecnologia", "biotecnologia", "inovação"],
            "certificacao": ["certificação", "orgânico", "qualidade"],
            "conflitos_agrarios": ["conflito", "invasão", "mediação"]
        }
        
        for especialidade, keywords in mapa_keywords.items():
            for keyword in keywords:
                if keyword in consulta_lower:
                    return especialidade
        
        return "reforma_agraria"  # Padrão

    def _processar_com_agente(self, consulta: str, agente: Dict) -> str:
        """Processa consulta com agente específico"""
        # Implementação simplificada - em produção usaria IA
        return f"Resposta elaborada pelo {agente['nome']} baseada em suas capacidades específicas: {json.loads(agente['capacidades'])[:2]}"

    def _sugerir_templates(self, especialidade: str) -> List[str]:
        """Sugere templates baseados na especialidade"""
        if not self.conn:
            return []
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT nome FROM legal_templates_juridicos 
                WHERE criado_por LIKE %s AND ativo = true
                LIMIT 5
            """, (f"%{especialidade}%",))
            
            results = cursor.fetchall()
            cursor.close()
            
            return [row[0] for row in results]
            
        except Exception as e:
            logger.error(f"❌ Erro ao sugerir templates: {e}")
            return []

    def __del__(self):
        """Fecha conexão ao destruir objeto"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

def inicializar_assistente_agrario():
    """Função para inicializar o assistente de Direito Agrário"""
    try:
        assistente = AssistenteAgrario()
        
        # Criar agentes especializados
        success_agentes = assistente.criar_agentes_especializados()
        if success_agentes:
            logger.info("✅ Agentes de Direito Agrário criados com sucesso")
        
        # Criar templates especializados
        success_templates = assistente.criar_templates_especializados()
        if success_templates:
            logger.info("✅ Templates de Direito Agrário criados com sucesso")
        
        return assistente
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização do Assistente Agrário: {e}")
        return None


    def processar_consulta_completa(self, pergunta: str, api_escolhida: str = "openai", 
                                  estilo: str = "juridico_tecnico", 
                                  usar_base_vetorial: bool = True):
        """Processa consulta completa usando assistente base"""
        try:
            # Usar o método da classe base
            return super().processar_consulta_completa(pergunta, api_escolhida, estilo, usar_base_vetorial)
        except Exception as e:
            logger.error(f"Erro ao processar consulta: {e}")
            return {
                'resposta': f"Erro ao processar consulta: {str(e)}",
                'contexto_usado': False,
                'resultados_busca': [],
                'api_utilizada': api_escolhida,
                'status': 'erro'
            }

if __name__ == "__main__":
    # Para teste direto
    assistente = inicializar_assistente_agrario()
    if assistente:
        print("✅ Assistente de Direito Agrário inicializado com sucesso!")
    else:
        print("❌ Falha na inicialização do Assistente de Direito Agrário")