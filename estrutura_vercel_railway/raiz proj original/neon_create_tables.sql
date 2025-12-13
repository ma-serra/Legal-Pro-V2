-- =============================================
-- ESTRUTURA DAS TABELAS - LEGAL PRO
-- Execute ANTES de importar os dados
-- =============================================

-- Tabela: cache_resposta_api

CREATE TABLE cache_resposta_api (
	id SERIAL NOT NULL, 
	provedor VARCHAR(50) NOT NULL, 
	modelo VARCHAR(50) NOT NULL, 
	hash_prompt VARCHAR(64) NOT NULL, 
	prompt TEXT NOT NULL, 
	resposta TEXT NOT NULL, 
	parametros TEXT, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_expiracao TIMESTAMP WITHOUT TIME ZONE, 
	contador_uso INTEGER, 
	PRIMARY KEY (id)
)

;

-- Tabela: cash_flow_operacional

CREATE TABLE cash_flow_operacional (
	id SERIAL NOT NULL, 
	ano INTEGER NOT NULL, 
	mes INTEGER NOT NULL, 
	honorarios_processos FLOAT NOT NULL, 
	consultorias FLOAT NOT NULL, 
	due_diligence FLOAT NOT NULL, 
	pareceres_juridicos FLOAT NOT NULL, 
	contratos_especiais FLOAT NOT NULL, 
	outras_receitas FLOAT NOT NULL, 
	custos_processuais FLOAT NOT NULL, 
	despesas_operacionais FLOAT NOT NULL, 
	pagamento_colaboradores FLOAT NOT NULL, 
	impostos_taxas FLOAT NOT NULL, 
	investimentos_tecnologia FLOAT NOT NULL, 
	outras_despesas FLOAT NOT NULL, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;

-- Tabela: categoria_juridica

CREATE TABLE categoria_juridica (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	descricao TEXT, 
	icone VARCHAR(50), 
	cor VARCHAR(20), 
	ativa BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
)

;

-- Tabela: categoria_template

CREATE TABLE categoria_template (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	descricao TEXT, 
	icone VARCHAR(50), 
	cor VARCHAR(20), 
	ordem INTEGER, 
	ativa BOOLEAN, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_modificacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
)

;

-- Tabela: categorias_documento

CREATE TABLE categorias_documento (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	descricao VARCHAR(255), 
	icone VARCHAR(50), 
	cor_tema VARCHAR(7), 
	ativo BOOLEAN, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
)

;

-- Tabela: componente_editor

CREATE TABLE componente_editor (
	id SERIAL NOT NULL, 
	nome VARCHAR(200) NOT NULL, 
	categoria VARCHAR(100) NOT NULL, 
	tipo VARCHAR(100) NOT NULL, 
	descricao TEXT, 
	descricao_detalhada TEXT, 
	icone VARCHAR(100), 
	cor VARCHAR(20), 
	ativo BOOLEAN, 
	configuracao JSON, 
	prompt_sistema TEXT, 
	prompt_usuario TEXT, 
	capacidades JSON, 
	parametros JSON, 
	base_conhecimento VARCHAR(200), 
	temperatura FLOAT, 
	max_tokens INTEGER, 
	top_k INTEGER, 
	chunk_size INTEGER, 
	chunk_overlap INTEGER, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;

-- Tabela: inadimplencia_por_area

CREATE TABLE inadimplencia_por_area (
	id SERIAL NOT NULL, 
	area_juridica VARCHAR(100) NOT NULL, 
	ano INTEGER NOT NULL, 
	mes INTEGER, 
	total_casos INTEGER, 
	casos_inadimplentes INTEGER, 
	taxa_inadimplencia FLOAT, 
	valor_inadimplente FLOAT, 
	tempo_medio_atraso FLOAT, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_inadimplencia_area_periodo UNIQUE (area_juridica, ano, mes)
)

;

-- Tabela: indicador_fluxo

CREATE TABLE indicador_fluxo (
	id SERIAL NOT NULL, 
	ano INTEGER NOT NULL, 
	mes INTEGER NOT NULL, 
	honorarios_processos FLOAT NOT NULL, 
	repasse_pagamentos_custas FLOAT NOT NULL, 
	recebimentos_acordos FLOAT NOT NULL, 
	execucoes_realizadas FLOAT NOT NULL, 
	custos_operacionais_processos FLOAT NOT NULL, 
	custas_processuais_pagas FLOAT NOT NULL, 
	despesas_escritorio FLOAT NOT NULL, 
	investimentos_marketing FLOAT NOT NULL, 
	fluxo_liquido FLOAT NOT NULL, 
	saldo_acumulado FLOAT NOT NULL, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;

-- Tabela: indicadores_estrategicos

CREATE TABLE indicadores_estrategicos (
	id SERIAL NOT NULL, 
	ano INTEGER NOT NULL, 
	mes INTEGER, 
	total_processos INTEGER, 
	processos_ativos INTEGER, 
	processos_encerrados INTEGER, 
	taxa_sucesso_global FLOAT, 
	valor_total_carteira FLOAT, 
	provisao_total FLOAT, 
	receita_bruta FLOAT, 
	custos_totais FLOAT, 
	margem_liquida FLOAT, 
	roi_geral FLOAT, 
	tempo_medio_conclusao FLOAT, 
	satisfacao_cliente_media FLOAT, 
	produtividade_media FLOAT, 
	capacidade_utilizada FLOAT, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;

-- Tabela: lawyer_metrics

CREATE TABLE lawyer_metrics (
	id SERIAL NOT NULL, 
	advogado_nome VARCHAR(200) NOT NULL, 
	total_casos INTEGER, 
	eficiencia FLOAT, 
	carteira_total FLOAT, 
	remuneracao FLOAT, 
	produtividade_financeira FLOAT, 
	margem_media FLOAT, 
	produtividade_tecnica FLOAT, 
	roi_individual FLOAT, 
	casos_por_milhao FLOAT, 
	eficiencia_geral FLOAT, 
	taxa_sucesso FLOAT, 
	tempo_medio_caso FLOAT, 
	satisfacao_cliente FLOAT, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;

-- Tabela: legal_areas

CREATE TABLE legal_areas (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	icone VARCHAR(50), 
	cor VARCHAR(7), 
	descricao TEXT, 
	ativo BOOLEAN, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;

-- Tabela: legal_areas_juridicas

CREATE TABLE legal_areas_juridicas (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	icone VARCHAR(50) NOT NULL, 
	descricao TEXT, 
	cor_tema VARCHAR(7), 
	ativo BOOLEAN, 
	ordem_exibicao INTEGER, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
)

;

-- Tabela: legal_tipos_documento

CREATE TABLE legal_tipos_documento (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	categoria VARCHAR(50) NOT NULL, 
	descricao TEXT, 
	icone VARCHAR(50), 
	ativo BOOLEAN, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;

-- Tabela: performance_financeira_advogado

CREATE TABLE performance_financeira_advogado (
	id SERIAL NOT NULL, 
	advogado_nome VARCHAR(255) NOT NULL, 
	periodo_ano INTEGER NOT NULL, 
	periodo_mes INTEGER, 
	total_casos INTEGER, 
	carteira_total FLOAT, 
	provisao_total FLOAT, 
	pagamento_total FLOAT, 
	honorarios_recebidos FLOAT, 
	margem_media FLOAT, 
	eficiencia_media FLOAT, 
	produtividade_financeira FLOAT, 
	roi_individual FLOAT, 
	tempo_medio_processo FLOAT, 
	taxa_sucesso FLOAT, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;

-- Tabela: permission

CREATE TABLE permission (
	id SERIAL NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	code VARCHAR(64) NOT NULL, 
	description TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	UNIQUE (code)
)

;

-- Tabela: role

CREATE TABLE role (
	id SERIAL NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	description TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (name)
)

;

-- Tabela: situacao

CREATE TABLE situacao (
	id SERIAL NOT NULL, 
	nome VARCHAR(50) NOT NULL, 
	descricao VARCHAR(255), 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
)

;

-- Tabela: agente_juridico

CREATE TABLE agente_juridico (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	classe VARCHAR(100) NOT NULL, 
	descricao TEXT, 
	detalhes_tecnicos TEXT, 
	categoria_id INTEGER, 
	nivel_especializacao INTEGER, 
	ativo BOOLEAN, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	nivel VARCHAR(50), 
	modelo_ai VARCHAR(50), 
	temperatura FLOAT, 
	top_p FLOAT, 
	top_k INTEGER, 
	max_tokens INTEGER, 
	icone VARCHAR(100), 
	cor_destaque VARCHAR(20), 
	template_prompt TEXT, 
	modo_fragmentacao VARCHAR(20), 
	identificador_segmento VARCHAR(10), 
	comprimento_max_fragmento INTEGER, 
	sobreposicao_blocos INTEGER, 
	comprimento_fragmento_filho INTEGER, 
	preprocessamento_texto BOOLEAN, 
	capacidades JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(categoria_id) REFERENCES categoria_juridica (id)
)

;

-- Tabela: legal_templates_juridicos

CREATE TABLE legal_templates_juridicos (
	id SERIAL NOT NULL, 
	nome VARCHAR(200) NOT NULL, 
	descricao TEXT, 
	conteudo_html TEXT NOT NULL, 
	conteudo_texto TEXT, 
	area_juridica_id INTEGER NOT NULL, 
	tipo_documento_id INTEGER NOT NULL, 
	palavras_chave TEXT, 
	complexidade VARCHAR(20), 
	tempo_estimado INTEGER, 
	versao VARCHAR(10), 
	criado_por VARCHAR(100), 
	modificado_por VARCHAR(100), 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	modificado_em TIMESTAMP WITHOUT TIME ZONE, 
	ativo BOOLEAN, 
	uso_contador INTEGER, 
	favorito BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(area_juridica_id) REFERENCES legal_areas_juridicas (id), 
	FOREIGN KEY(tipo_documento_id) REFERENCES legal_tipos_documento (id)
)

;

-- Tabela: legal_templates_v2

CREATE TABLE legal_templates_v2 (
	id SERIAL NOT NULL, 
	nome VARCHAR(200) NOT NULL, 
	descricao TEXT, 
	conteudo_html TEXT NOT NULL, 
	area_id INTEGER NOT NULL, 
	tipo_documento VARCHAR(100), 
	complexidade VARCHAR(20), 
	tempo_estimado INTEGER, 
	uso_contador INTEGER, 
	palavras_chave TEXT, 
	ativo BOOLEAN, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(area_id) REFERENCES legal_areas (id)
)

;

-- Tabela: role_permissions

CREATE TABLE role_permissions (
	role_id INTEGER NOT NULL, 
	permission_id INTEGER NOT NULL, 
	PRIMARY KEY (role_id, permission_id), 
	FOREIGN KEY(role_id) REFERENCES role (id), 
	FOREIGN KEY(permission_id) REFERENCES permission (id)
)

;

-- Tabela: user

CREATE TABLE "user" (
	id SERIAL NOT NULL, 
	username VARCHAR(64) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(256) NOT NULL, 
	first_name VARCHAR(64), 
	last_name VARCHAR(64), 
	active BOOLEAN, 
	is_admin BOOLEAN, 
	last_login TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	role_id INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email), 
	FOREIGN KEY(role_id) REFERENCES role (id)
)

;

-- Tabela: analise_especialista_individual

CREATE TABLE analise_especialista_individual (
	id VARCHAR(36) NOT NULL, 
	codigo_analise VARCHAR(20) NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	documento_original TEXT NOT NULL, 
	documento_nome VARCHAR(255), 
	documento_tipo VARCHAR(100), 
	agente_id INTEGER NOT NULL, 
	agente_nome VARCHAR(255) NOT NULL, 
	agente_especialidade VARCHAR(255) NOT NULL, 
	agente_nivel_experiencia VARCHAR(50) NOT NULL, 
	area_juridica VARCHAR(255) NOT NULL, 
	opiniao_juridica TEXT NOT NULL, 
	fundamentacao_legal TEXT, 
	jurisprudencia_citada JSON, 
	doutrina_citada JSON, 
	legislacao_aplicavel JSON, 
	pontos_positivos JSON, 
	pontos_negativos JSON, 
	riscos_identificados JSON, 
	recomendacoes TEXT, 
	conclusao_geral TEXT, 
	nivel_confianca FLOAT, 
	complexidade_documento VARCHAR(20), 
	urgencia_recomendada VARCHAR(20), 
	status VARCHAR(30), 
	tempo_processamento INTEGER, 
	modelo_ia_utilizado VARCHAR(100), 
	tokens_utilizados INTEGER, 
	embeddings_consultados INTEGER, 
	documentos_referencia JSON, 
	PRIMARY KEY (id), 
	UNIQUE (codigo_analise), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: analise_juridica

CREATE TABLE analise_juridica (
	id SERIAL NOT NULL, 
	numero_registro VARCHAR(50) NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	texto_original TEXT NOT NULL, 
	resultados_json TEXT NOT NULL, 
	total_agentes INTEGER NOT NULL, 
	status VARCHAR(20), 
	PRIMARY KEY (id), 
	UNIQUE (numero_registro), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: arquivo_relacional

CREATE TABLE arquivo_relacional (
	id SERIAL NOT NULL, 
	filename VARCHAR(255) NOT NULL, 
	original_filename VARCHAR(255) NOT NULL, 
	file_type VARCHAR(10) NOT NULL, 
	file_size INTEGER NOT NULL, 
	file_path VARCHAR(500) NOT NULL, 
	category VARCHAR(50), 
	description TEXT, 
	uploaded_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(uploaded_by) REFERENCES "user" (id)
)

;

-- Tabela: arquivo_transcricao

CREATE TABLE arquivo_transcricao (
	id VARCHAR(36) NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	data_upload TIMESTAMP WITHOUT TIME ZONE, 
	arquivo_nome VARCHAR(255) NOT NULL, 
	arquivo_path VARCHAR(500) NOT NULL, 
	arquivo_tipo VARCHAR(100) NOT NULL, 
	arquivo_tamanho INTEGER NOT NULL, 
	hash_arquivo VARCHAR(64), 
	duracao INTEGER, 
	taxa_amostragem INTEGER, 
	bitrate INTEGER, 
	canais INTEGER, 
	metadados TEXT, 
	status VARCHAR(30), 
	status_mensagem VARCHAR(255), 
	prioridade INTEGER, 
	configuracoes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: audit_log

CREATE TABLE audit_log (
	id SERIAL NOT NULL, 
	timestamp TIMESTAMP WITHOUT TIME ZONE, 
	user_id INTEGER, 
	action VARCHAR(50) NOT NULL, 
	entity_type VARCHAR(50), 
	entity_id VARCHAR(50), 
	details TEXT, 
	ip_address VARCHAR(45), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES "user" (id)
)

;

-- Tabela: avaliacao_agente

CREATE TABLE avaliacao_agente (
	id SERIAL NOT NULL, 
	agente_id INTEGER NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	documento_id INTEGER, 
	rating INTEGER NOT NULL, 
	comentario TEXT, 
	data_avaliacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(agente_id) REFERENCES agente_juridico (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: comparacao_documento

CREATE TABLE comparacao_documento (
	id VARCHAR(36) NOT NULL, 
	titulo VARCHAR(200) NOT NULL, 
	area_processo VARCHAR(100) NOT NULL, 
	descricao_area VARCHAR(100), 
	documento_cliente VARCHAR(20), 
	user_id INTEGER, 
	data_comparacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	resultado_html_lado_a TEXT NOT NULL, 
	resultado_html_lado_b TEXT NOT NULL, 
	resultado_editado_a TEXT, 
	resultado_editado_b TEXT, 
	total_diferencas INTEGER, 
	total_adicoes INTEGER, 
	total_remocoes INTEGER, 
	percentual_similaridade FLOAT, 
	formato_exportacao VARCHAR(10), 
	incluir_marcacoes BOOLEAN, 
	status VARCHAR(20), 
	status_mensagem TEXT, 
	analise_ia TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES "user" (id)
)

;

-- Tabela: documento

CREATE TABLE documento (
	id SERIAL NOT NULL, 
	titulo VARCHAR(200) NOT NULL, 
	descricao TEXT, 
	tipo VARCHAR(50), 
	usuario_id INTEGER NOT NULL, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	tags VARCHAR(255), 
	hash_conteudo VARCHAR(64), 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: documento_carregado

CREATE TABLE documento_carregado (
	id SERIAL NOT NULL, 
	agent_id INTEGER NOT NULL, 
	user_id INTEGER, 
	filename VARCHAR(255) NOT NULL, 
	original_filename VARCHAR(255), 
	file_path VARCHAR(500), 
	file_hash VARCHAR(64), 
	file_size INTEGER, 
	file_type VARCHAR(50), 
	description TEXT, 
	processing_type VARCHAR(20), 
	processing_status VARCHAR(20), 
	processing_message TEXT, 
	chunks_count INTEGER, 
	embeddings_count INTEGER, 
	questions_generated INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	processed_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(agent_id) REFERENCES agente_juridico (id), 
	FOREIGN KEY(user_id) REFERENCES "user" (id)
)

;

-- Tabela: fluxo

CREATE TABLE fluxo (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	descricao TEXT, 
	agentes TEXT, 
	conexoes TEXT, 
	configuracao TEXT, 
	ativo BOOLEAN, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	ultima_execucao TIMESTAMP WITHOUT TIME ZONE, 
	criado_por_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(criado_por_id) REFERENCES "user" (id)
)

;

-- Tabela: legal_favoritos_templates

CREATE TABLE legal_favoritos_templates (
	id SERIAL NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	template_id INTEGER NOT NULL, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id), 
	FOREIGN KEY(template_id) REFERENCES legal_templates_juridicos (id)
)

;

-- Tabela: legal_historico_uso_templates

CREATE TABLE legal_historico_uso_templates (
	id SERIAL NOT NULL, 
	template_id INTEGER NOT NULL, 
	usuario_id INTEGER, 
	ip_address VARCHAR(45), 
	user_agent TEXT, 
	usado_em TIMESTAMP WITHOUT TIME ZONE, 
	projeto_nome VARCHAR(200), 
	modificacoes_realizadas BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(template_id) REFERENCES legal_templates_juridicos (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: permissao_area_juridica

CREATE TABLE permissao_area_juridica (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	area_juridica VARCHAR(64) NOT NULL, 
	pode_visualizar BOOLEAN, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uix_user_area_juridica UNIQUE (user_id, area_juridica), 
	FOREIGN KEY(user_id) REFERENCES "user" (id)
)

;

-- Tabela: processo_juridico

CREATE TABLE processo_juridico (
	id SERIAL NOT NULL, 
	numero_processo_cnj VARCHAR(25) NOT NULL, 
	area_juridica VARCHAR(100) NOT NULL, 
	cliente VARCHAR(200) NOT NULL, 
	autor VARCHAR(200) NOT NULL, 
	parte_contraria VARCHAR(200), 
	cpf_autor VARCHAR(14), 
	cnpj VARCHAR(18), 
	advogado_do_caso VARCHAR(200) NOT NULL, 
	advogado_adverso VARCHAR(200), 
	data_registro TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	data_distribuicao TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	estado VARCHAR(50) NOT NULL, 
	comarca VARCHAR(100) NOT NULL, 
	juizo VARCHAR(200) NOT NULL, 
	resumo_dos_fatos TEXT NOT NULL, 
	valor_da_causa FLOAT NOT NULL, 
	calculo_contadores FLOAT, 
	provisao FLOAT, 
	execucao FLOAT, 
	previsao_de_pagamento TIMESTAMP WITHOUT TIME ZONE, 
	bloqueio FLOAT, 
	risco VARCHAR(50), 
	data_acordo TIMESTAMP WITHOUT TIME ZONE, 
	acordo FLOAT, 
	pagamento FLOAT, 
	deposito_recursal FLOAT, 
	funcao VARCHAR(200), 
	andamento_relatorio TEXT, 
	fase VARCHAR(100), 
	titulo VARCHAR(255), 
	ano_distribuicao INTEGER, 
	status VARCHAR(100), 
	polo VARCHAR(100), 
	empresa VARCHAR(255), 
	processo VARCHAR(50), 
	esfera VARCHAR(50), 
	pasta VARCHAR(100), 
	acao VARCHAR(255), 
	tema VARCHAR(255), 
	objeto TEXT, 
	instancia VARCHAR(100), 
	fase_processual VARCHAR(100), 
	liminar BOOLEAN, 
	valor_provisao FLOAT, 
	estimativa_desembolso TIMESTAMP WITHOUT TIME ZONE, 
	pagamentos FLOAT, 
	posicao_simplificada VARCHAR(255), 
	resultado VARCHAR(255), 
	resultado_processo VARCHAR(20), 
	observacoes TEXT, 
	acidente_de_trabalho BOOLEAN, 
	acumulo_de_funcao BOOLEAN, 
	adicional_de_periculosidade BOOLEAN, 
	adicional_de_sobreaviso BOOLEAN, 
	adicional_noturno_e_reflexos BOOLEAN, 
	ajuda_de_custo BOOLEAN, 
	aplicacao_do_artigo_467_da_clt BOOLEAN, 
	apresentacao_de_documentos BOOLEAN, 
	artigo_384_da_clt BOOLEAN, 
	beneficios_previstos_na_cct_da_2a_reclamada BOOLEAN, 
	descaracterizacao_do_cargo_de_confianca BOOLEAN, 
	devolucao_de_descontos BOOLEAN, 
	devolucao_de_descontos_lancados_no_trct BOOLEAN, 
	diferencas_de_comissoes BOOLEAN, 
	diferencas_salariais BOOLEAN, 
	dsrs BOOLEAN, 
	equiparacao_salarial BOOLEAN, 
	estabilidade BOOLEAN, 
	ferias_em_dobro BOOLEAN, 
	fgts_e_a_multa_de_40_porcento BOOLEAN, 
	horas_extras_e_reflexos BOOLEAN, 
	indenizacao_aviso_previo BOOLEAN, 
	indenizacao_por_danos_materiais BOOLEAN, 
	indenizacao_por_danos_morais BOOLEAN, 
	integracao_das_comissoes BOOLEAN, 
	integracao_das_comissoes_por_fora BOOLEAN, 
	integracao_dos_premios BOOLEAN, 
	intervalo_interjornada BOOLEAN, 
	intervalo_intrajornada BOOLEAN, 
	liberacao_das_guias_trct_e_cd_sob_pena_de_indenizacao BOOLEAN, 
	multa_convencional_ou_normativa BOOLEAN, 
	multa_do_artigo_477_da_clt BOOLEAN, 
	outros BOOLEAN, 
	plr BOOLEAN, 
	quebra_de_caixa BOOLEAN, 
	plano_de_saude BOOLEAN, 
	reconhecimento_da_remuneracao_recebida BOOLEAN, 
	reembolso_km BOOLEAN, 
	reenquadramento_sindical BOOLEAN, 
	reintegracao BOOLEAN, 
	rescisao_indireta BOOLEAN, 
	responsabilizacao_subsidiaria_da_2a_reclamada_vivo BOOLEAN, 
	reversao_do_pedido_de_demissao_em_demissao_sem_justa_causa BOOLEAN, 
	reversao_justa_causa BOOLEAN, 
	salario_substituicao BOOLEAN, 
	seguro_desemprego BOOLEAN, 
	sucumbencia BOOLEAN, 
	vale_refeicao BOOLEAN, 
	vale_transporte BOOLEAN, 
	verbas_rescisoria BOOLEAN, 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	judit_request_id VARCHAR(100), 
	judit_ultima_consulta TIMESTAMP WITHOUT TIME ZONE, 
	judit_dados_processo JSON, 
	judit_movimentacoes JSON, 
	judit_partes JSON, 
	judit_anexos JSON, 
	judit_monitoramento_id VARCHAR(100), 
	judit_status_monitoramento VARCHAR(50), 
	judit_sincronizado BOOLEAN NOT NULL, 
	situacao_id INTEGER, 
	cpf_cliente VARCHAR(14), 
	cnpj_autor VARCHAR(18), 
	penhora FLOAT, 
	data_encerramento TIMESTAMP WITHOUT TIME ZONE, 
	motivo_encerramento VARCHAR(255), 
	custas_processuais FLOAT, 
	honorarios_periciais FLOAT, 
	honorarios_sucumbencia FLOAT, 
	depositos_judiciais FLOAT, 
	valor_honorarios_contratados FLOAT, 
	valor_recuperado FLOAT, 
	data_ultimo_pagamento TIMESTAMP WITHOUT TIME ZONE, 
	recebimentos_honorarios FLOAT, 
	tempo_fixado_beneficio INTEGER, 
	tempo_tramitacao_dias INTEGER, 
	taxa_sucesso FLOAT, 
	satisfacao_cliente FLOAT, 
	produtividade_financeira FLOAT, 
	risco_concentracao FLOAT, 
	sazonalidade_mes VARCHAR(20), 
	previsao_custos_futuros FLOAT, 
	projecao_gastos_fase TEXT, 
	capital_giro_necessario FLOAT, 
	ciclo_financeiro_dias INTEGER, 
	custo_operacional_caso FLOAT, 
	margem_lucro_caso FLOAT, 
	remuneracao_cargo_colaborador FLOAT, 
	cenario_melhor_caso FLOAT, 
	cenario_pior_caso FLOAT, 
	indice_viabilidade_economica FLOAT, 
	analise_estrategica TEXT, 
	analise_tecnica TEXT, 
	analise_estatistica TEXT, 
	analise_preditiva TEXT, 
	data_analise_ia TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id), 
	FOREIGN KEY(situacao_id) REFERENCES situacao (id)
)

;

-- Tabela: relatorio_consenso

CREATE TABLE relatorio_consenso (
	id SERIAL NOT NULL, 
	uuid_relatorio VARCHAR(36) NOT NULL, 
	numero_relatorio VARCHAR(20) NOT NULL, 
	analise_numero_registro VARCHAR(20) NOT NULL, 
	titulo_relatorio VARCHAR(200) NOT NULL, 
	descricao TEXT, 
	user_id INTEGER NOT NULL, 
	consenso_geral TEXT NOT NULL, 
	nivel_concordancia FLOAT, 
	pontos_convergencia JSON, 
	pontos_divergencia JSON, 
	analise_riscos JSON NOT NULL, 
	analise_melhorias JSON, 
	estrategias_recomendadas JSON, 
	riscos_criticos JSON, 
	riscos_moderados JSON, 
	riscos_baixos JSON, 
	melhorias_urgentes JSON, 
	melhorias_importantes JSON, 
	melhorias_sugeridas JSON, 
	estrategias_curto_prazo JSON, 
	estrategias_medio_prazo JSON, 
	estrategias_longo_prazo JSON, 
	impacto_estimado VARCHAR(50), 
	viabilidade_implementacao VARCHAR(50), 
	recursos_necessarios JSON, 
	modelo_ia_utilizado VARCHAR(100), 
	tokens_consumidos INTEGER, 
	custo_estimado FLOAT, 
	tempo_processamento FLOAT, 
	status VARCHAR(50), 
	status_mensagem TEXT, 
	versao INTEGER, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	data_aprovacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (uuid_relatorio), 
	UNIQUE (numero_relatorio), 
	FOREIGN KEY(user_id) REFERENCES "user" (id)
)

;

-- Tabela: resultado_analise_multiagente

CREATE TABLE resultado_analise_multiagente (
	id VARCHAR(36) NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	documento_original TEXT NOT NULL, 
	documento_nome VARCHAR(255), 
	tipo_analise VARCHAR(50), 
	resultado_principal JSON, 
	resultados_agentes JSON, 
	agentes_utilizados JSON, 
	tempo_processamento INTEGER, 
	status VARCHAR(30), 
	provider_principal VARCHAR(50), 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: segunda_opiniao

CREATE TABLE segunda_opiniao (
	id SERIAL NOT NULL, 
	agente_original_id INTEGER NOT NULL, 
	agente_revisor_id INTEGER NOT NULL, 
	documento_id INTEGER, 
	resultado_original TEXT NOT NULL, 
	resultado_revisao TEXT NOT NULL, 
	nivel_concordancia INTEGER, 
	pontos_divergentes TEXT, 
	pontos_complementares TEXT, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(agente_original_id) REFERENCES agente_juridico (id), 
	FOREIGN KEY(agente_revisor_id) REFERENCES agente_juridico (id)
)

;

-- Tabela: system_config

CREATE TABLE system_config (
	id SERIAL NOT NULL, 
	system_name VARCHAR(200), 
	debug_mode BOOLEAN, 
	log_level VARCHAR(20), 
	max_agents INTEGER, 
	assemblyai_enabled BOOLEAN, 
	whisper_enabled BOOLEAN, 
	speaker_detection BOOLEAN, 
	auto_summary BOOLEAN, 
	openai_model VARCHAR(50), 
	anthropic_model VARCHAR(50), 
	temperature FLOAT, 
	max_tokens INTEGER, 
	session_timeout INTEGER, 
	max_login_attempts INTEGER, 
	lockout_duration INTEGER, 
	enable_monitoring BOOLEAN, 
	enable_cost_tracking BOOLEAN, 
	cost_alert_threshold FLOAT, 
	token_limit_daily INTEGER, 
	enable_pdf_export BOOLEAN, 
	enable_docx_export BOOLEAN, 
	default_font_size INTEGER, 
	last_updated TIMESTAMP WITHOUT TIME ZONE, 
	updated_by INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(updated_by) REFERENCES "user" (id)
)

;

-- Tabela: tema_pagina

CREATE TABLE tema_pagina (
	id SERIAL NOT NULL, 
	rota VARCHAR(100) NOT NULL, 
	descricao VARCHAR(255), 
	cores TEXT NOT NULL, 
	modificado_por INTEGER, 
	modificado_em TIMESTAMP WITHOUT TIME ZONE, 
	ativo BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (rota), 
	FOREIGN KEY(modificado_por) REFERENCES "user" (id)
)

;

-- Tabela: template_juridico

CREATE TABLE template_juridico (
	id SERIAL NOT NULL, 
	nome VARCHAR(200) NOT NULL, 
	descricao TEXT, 
	modulo_origem VARCHAR(50), 
	campos JSON, 
	modelo_texto TEXT, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_modificacao TIMESTAMP WITHOUT TIME ZONE, 
	tipo_documento VARCHAR(100), 
	area_juridica VARCHAR(100), 
	campos_obrigatorios JSON, 
	campos_opcionais JSON, 
	template_conteudo TEXT, 
	formatacao JSON, 
	categoria_id INTEGER, 
	nivel_complexidade VARCHAR(20), 
	tempo_estimado INTEGER, 
	ativo BOOLEAN, 
	versao VARCHAR(10), 
	aprovado BOOLEAN, 
	criado_por INTEGER, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	modificado_em TIMESTAMP WITHOUT TIME ZONE, 
	total_utilizacoes INTEGER, 
	ultima_utilizacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(categoria_id) REFERENCES categoria_template (id), 
	FOREIGN KEY(criado_por) REFERENCES "user" (id)
)

;

-- Tabela: templates_documento

CREATE TABLE templates_documento (
	id SERIAL NOT NULL, 
	nome VARCHAR(200) NOT NULL, 
	descricao TEXT, 
	categoria_id INTEGER NOT NULL, 
	template_original_id INTEGER, 
	modulo_origem VARCHAR(50), 
	modulo_nome VARCHAR(100), 
	area_juridica VARCHAR(50), 
	icone VARCHAR(50), 
	tipo_documento VARCHAR(100), 
	complexidade VARCHAR(20), 
	campos_obrigatorios JSON, 
	campos_opcionais JSON, 
	estrutura_template TEXT, 
	conteudo_template TEXT, 
	variaveis_template JSON, 
	requer_assinatura BOOLEAN, 
	permite_edicao BOOLEAN, 
	versao VARCHAR(10), 
	total_utilizacoes INTEGER, 
	ultima_utilizacao TIMESTAMP WITHOUT TIME ZONE, 
	ativo BOOLEAN, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE, 
	criado_por INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(categoria_id) REFERENCES categorias_documento (id), 
	FOREIGN KEY(criado_por) REFERENCES "user" (id)
)

;

-- Tabela: validacao_multi_agente

CREATE TABLE validacao_multi_agente (
	id VARCHAR(36) NOT NULL, 
	codigo_validacao VARCHAR(20) NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	documento_original TEXT NOT NULL, 
	documento_nome VARCHAR(255), 
	documento_tipo VARCHAR(100), 
	agentes_utilizados JSON NOT NULL, 
	total_agentes INTEGER NOT NULL, 
	areas_juridicas JSON NOT NULL, 
	status VARCHAR(30), 
	status_mensagem VARCHAR(500), 
	tempo_processamento INTEGER, 
	opiniao_consolidada TEXT, 
	pontos_criticos JSON, 
	recomendacoes_gerais TEXT, 
	configuracoes JSON, 
	PRIMARY KEY (id), 
	UNIQUE (codigo_validacao), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: validacao_multi_agente_analise

CREATE TABLE validacao_multi_agente_analise (
	id SERIAL NOT NULL, 
	uuid_analise VARCHAR(36) NOT NULL, 
	hash_sha256 VARCHAR(64) NOT NULL, 
	numero_registro VARCHAR(20) NOT NULL, 
	titulo_analise VARCHAR(200) NOT NULL, 
	descricao TEXT, 
	user_id INTEGER NOT NULL, 
	documento_original TEXT NOT NULL, 
	documento_nome VARCHAR(255), 
	documento_tipo VARCHAR(50), 
	documento_tamanho INTEGER, 
	total_agentes_utilizados INTEGER NOT NULL, 
	areas_juridicas_envolvidas JSON NOT NULL, 
	configuracao_analise JSON, 
	resultados_agentes JSON NOT NULL, 
	opiniao_consolidada TEXT, 
	pontos_criticos JSON, 
	recomendacoes_prioritarias JSON, 
	recomendacoes_importantes JSON, 
	recomendacoes_sugeridas JSON, 
	tempo_processamento_segundos FLOAT, 
	modelos_ia_utilizados JSON, 
	tokens_consumidos INTEGER, 
	custo_estimado FLOAT, 
	status VARCHAR(20), 
	status_mensagem TEXT, 
	fallback_mode BOOLEAN, 
	debug_mode BOOLEAN, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	data_conclusao TIMESTAMP WITHOUT TIME ZONE, 
	exportado_docx BOOLEAN, 
	exportado_pdf BOOLEAN, 
	exportado_txt BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (uuid_analise), 
	UNIQUE (hash_sha256), 
	UNIQUE (numero_registro), 
	FOREIGN KEY(user_id) REFERENCES "user" (id)
)

;

-- Tabela: analise_individual_agente

CREATE TABLE analise_individual_agente (
	id VARCHAR(36) NOT NULL, 
	validacao_id VARCHAR(36) NOT NULL, 
	agente_id INTEGER NOT NULL, 
	agente_nome VARCHAR(255) NOT NULL, 
	agente_especialidade VARCHAR(255) NOT NULL, 
	agente_nivel_experiencia VARCHAR(50) NOT NULL, 
	opiniao_juridica TEXT NOT NULL, 
	fundamentacao_legal TEXT, 
	jurisprudencia_citada JSON, 
	doutrina_citada JSON, 
	legislacao_aplicavel JSON, 
	pontos_positivos JSON, 
	pontos_negativos JSON, 
	riscos_identificados JSON, 
	recomendacoes TEXT, 
	nivel_confianca FLOAT, 
	complexidade_documento VARCHAR(20), 
	urgencia_recomendada VARCHAR(20), 
	data_analise TIMESTAMP WITHOUT TIME ZONE, 
	tempo_processamento INTEGER, 
	modelo_ia_utilizado VARCHAR(100), 
	tokens_utilizados INTEGER, 
	embeddings_consultados INTEGER, 
	documentos_referencia JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(validacao_id) REFERENCES validacao_multi_agente (id)
)

;

-- Tabela: analise_processo_ia

CREATE TABLE analise_processo_ia (
	id SERIAL NOT NULL, 
	processo_id INTEGER NOT NULL, 
	tipo_analise VARCHAR(100) NOT NULL, 
	modelo_ia VARCHAR(100) NOT NULL, 
	resultado JSON NOT NULL, 
	confianca FLOAT, 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	tempo_processamento INTEGER, 
	status VARCHAR(50), 
	PRIMARY KEY (id), 
	FOREIGN KEY(processo_id) REFERENCES processo_juridico (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: chunk_documento

CREATE TABLE chunk_documento (
	id SERIAL NOT NULL, 
	document_id INTEGER NOT NULL, 
	chunk_id VARCHAR(50) NOT NULL, 
	chunk_index INTEGER NOT NULL, 
	titulo VARCHAR(200), 
	subtitulo VARCHAR(200), 
	referencia VARCHAR(100), 
	conteudo TEXT NOT NULL, 
	conteudo_simplificado TEXT, 
	palavras INTEGER NOT NULL, 
	relevance_score INTEGER, 
	densidade_juridica FLOAT, 
	embedding_stored BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(document_id) REFERENCES documento_carregado (id)
)

;

-- Tabela: execucao_fluxo

CREATE TABLE execucao_fluxo (
	id SERIAL NOT NULL, 
	fluxo_id INTEGER NOT NULL, 
	usuario_id INTEGER, 
	dados_entrada TEXT, 
	resultado TEXT, 
	status VARCHAR(20) NOT NULL, 
	mensagem_erro TEXT, 
	data_inicio TIMESTAMP WITHOUT TIME ZONE, 
	data_conclusao TIMESTAMP WITHOUT TIME ZONE, 
	duracao_segundos FLOAT, 
	log_execucao TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(fluxo_id) REFERENCES fluxo (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: historico_documento

CREATE TABLE historico_documento (
	id SERIAL NOT NULL, 
	template_id INTEGER NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	titulo_documento VARCHAR(300) NOT NULL, 
	formato_exportacao VARCHAR(10), 
	tamanho_arquivo INTEGER, 
	campos_preenchidos JSON, 
	configuracoes_geracao JSON, 
	ip_usuario VARCHAR(45), 
	user_agent VARCHAR(500), 
	status VARCHAR(20), 
	caminho_arquivo VARCHAR(500), 
	gerado_em TIMESTAMP WITHOUT TIME ZONE, 
	baixado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(template_id) REFERENCES templates_documento (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: historico_template

CREATE TABLE historico_template (
	id SERIAL NOT NULL, 
	template_id INTEGER NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	campos_preenchidos JSON, 
	documento_gerado TEXT, 
	formato_saida VARCHAR(10), 
	gerado_em TIMESTAMP WITHOUT TIME ZONE, 
	ip_usuario VARCHAR(45), 
	user_agent VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(template_id) REFERENCES template_juridico (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: log_processamento_documento

CREATE TABLE log_processamento_documento (
	id SERIAL NOT NULL, 
	document_id INTEGER, 
	nivel VARCHAR(10) NOT NULL, 
	mensagem TEXT NOT NULL, 
	detalhes TEXT, 
	fase_processamento VARCHAR(50), 
	tempo_processamento FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(document_id) REFERENCES documento_carregado (id)
)

;

-- Tabela: transcricao

CREATE TABLE transcricao (
	id VARCHAR(36) NOT NULL, 
	usuario_id INTEGER, 
	arquivo_id VARCHAR(36), 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	arquivo_nome VARCHAR(255) NOT NULL, 
	arquivo_caminho VARCHAR(500), 
	arquivo_tamanho INTEGER, 
	arquivo_duracao INTEGER, 
	status VARCHAR(20), 
	provedor VARCHAR(50), 
	modelo VARCHAR(50), 
	texto TEXT, 
	metadados TEXT, 
	resultado_json TEXT, 
	sentimento VARCHAR(20), 
	score_sentimento FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id), 
	FOREIGN KEY(arquivo_id) REFERENCES arquivo_transcricao (id)
)

;

-- Tabela: versao_documento

CREATE TABLE versao_documento (
	id SERIAL NOT NULL, 
	documento_id INTEGER NOT NULL, 
	numero_versao INTEGER NOT NULL, 
	conteudo TEXT NOT NULL, 
	conteudo_html TEXT, 
	comentario VARCHAR(255), 
	usuario_id INTEGER NOT NULL, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	hash_conteudo VARCHAR(64), 
	PRIMARY KEY (id), 
	CONSTRAINT uix_versao_documento UNIQUE (documento_id, numero_versao), 
	FOREIGN KEY(documento_id) REFERENCES documento (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

-- Tabela: analise_documento

CREATE TABLE analise_documento (
	id SERIAL NOT NULL, 
	documento_id INTEGER NOT NULL, 
	versao_id INTEGER, 
	agente_id INTEGER NOT NULL, 
	conteudo_analise TEXT NOT NULL, 
	conteudo_analise_html TEXT, 
	data_analise TIMESTAMP WITHOUT TIME ZONE, 
	metadados TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(documento_id) REFERENCES documento (id), 
	FOREIGN KEY(versao_id) REFERENCES versao_documento (id), 
	FOREIGN KEY(agente_id) REFERENCES agente_juridico (id)
)

;

-- Tabela: entidade_documento

CREATE TABLE entidade_documento (
	id SERIAL NOT NULL, 
	documento_id INTEGER NOT NULL, 
	versao_id INTEGER, 
	tipo_entidade VARCHAR(50) NOT NULL, 
	nome_entidade VARCHAR(200) NOT NULL, 
	contexto TEXT, 
	metadados TEXT, 
	data_extracao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(documento_id) REFERENCES documento (id), 
	FOREIGN KEY(versao_id) REFERENCES versao_documento (id)
)

;

-- Tabela: pergunta_chunk

CREATE TABLE pergunta_chunk (
	id SERIAL NOT NULL, 
	chunk_id INTEGER NOT NULL, 
	question_id VARCHAR(50) NOT NULL, 
	group_index INTEGER NOT NULL, 
	nivel VARCHAR(20) NOT NULL, 
	pergunta TEXT NOT NULL, 
	contexto TEXT, 
	generated_by VARCHAR(50), 
	confidence_score FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(chunk_id) REFERENCES chunk_documento (id)
)

;

-- Tabela: analise_comparativa

CREATE TABLE analise_comparativa (
	id SERIAL NOT NULL, 
	analise_principal_id INTEGER NOT NULL, 
	analise_comparada_id INTEGER NOT NULL, 
	resultado_comparacao TEXT NOT NULL, 
	resultado_comparacao_html TEXT, 
	nivel_concordancia INTEGER, 
	pontos_concordantes TEXT, 
	pontos_divergentes TEXT, 
	pontos_complementares TEXT, 
	data_comparacao TIMESTAMP WITHOUT TIME ZONE, 
	usuario_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(analise_principal_id) REFERENCES analise_documento (id), 
	FOREIGN KEY(analise_comparada_id) REFERENCES analise_documento (id), 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id)
)

;

