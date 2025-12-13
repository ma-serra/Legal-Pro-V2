-- =============================================
-- ESTRUTURA COMPLETA - 83 TABELAS
-- Legal Pro - Exportado do banco local
-- =============================================


-- Tabela: agente_conexoes
CREATE TABLE "agente_conexoes" ("id" INTEGER NOT NULL DEFAULT nextval('agente_conexoes_id_seq'::regclass), "agente_origem_id" INTEGER, "agente_destino_id" INTEGER, "tipo_conexao" VARCHAR(50) NOT NULL, "areas_colaboracao" _text[], "descricao_conexao" TEXT, "ativa" BOOLEAN DEFAULT true, "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP);
ALTER TABLE "agente_conexoes" ADD CONSTRAINT "agente_conexoes_agente_destino_id_fkey" FOREIGN KEY (agente_destino_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "agente_conexoes" ADD CONSTRAINT "agente_conexoes_agente_origem_id_fkey" FOREIGN KEY (agente_origem_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "agente_conexoes" ADD CONSTRAINT "agente_conexoes_pkey" PRIMARY KEY (id);


-- Tabela: agente_juridico
CREATE TABLE "agente_juridico" ("id" INTEGER NOT NULL DEFAULT nextval('agente_juridico_id_seq'::regclass), "nome" VARCHAR(100) NOT NULL, "classe" VARCHAR(100) NOT NULL, "descricao" TEXT, "detalhes_tecnicos" TEXT, "categoria_id" INTEGER, "nivel_especializacao" INTEGER, "ativo" BOOLEAN, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "nivel" VARCHAR(50), "modelo_ai" VARCHAR(50), "temperatura" DOUBLE PRECISION, "top_p" DOUBLE PRECISION, "top_k" INTEGER, "max_tokens" INTEGER, "icone" VARCHAR(100), "cor_destaque" VARCHAR(20), "template_prompt" TEXT, "modo_fragmentacao" VARCHAR(20), "identificador_segmento" VARCHAR(10), "comprimento_max_fragmento" INTEGER, "sobreposicao_blocos" INTEGER, "comprimento_fragmento_filho" INTEGER, "preprocessamento_texto" BOOLEAN, "capacidades" JSON, "provider" VARCHAR(50), "tokens_entrada_max" INTEGER, "tokens_saida_max" INTEGER, "timeout" INTEGER, "retry_attempts" INTEGER, "max_tokens_resposta" INTEGER, "filho_pedaco_recuperacao" INTEGER, "ai_description" TEXT, "ai_assistant_ativo" BOOLEAN, "base_vetorial_ativa" BOOLEAN, "processamento_inteligente" BOOLEAN, "documentos_contexto" INTEGER, "threshold_relevancia" DOUBLE PRECISION, "max_tokens_contexto" INTEGER);
ALTER TABLE "agente_juridico" ADD CONSTRAINT "agente_juridico_categoria_id_fkey" FOREIGN KEY (categoria_id) REFERENCES "categoria_juridica" (id);
ALTER TABLE "agente_juridico" ADD CONSTRAINT "agente_juridico_pkey" PRIMARY KEY (id);


-- Tabela: agente_mensagens
CREATE TABLE "agente_mensagens" ("id" INTEGER NOT NULL DEFAULT nextval('agente_mensagens_id_seq'::regclass), "agente_origem_id" INTEGER, "agente_destino_id" INTEGER, "tipo_mensagem" VARCHAR(50), "conteudo_mensagem" TEXT, "prioridade" VARCHAR(20) DEFAULT 'normal'::character varying, "lida" BOOLEAN DEFAULT false, "data_envio" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "data_leitura" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "agente_mensagens" ADD CONSTRAINT "agente_mensagens_agente_destino_id_fkey" FOREIGN KEY (agente_destino_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "agente_mensagens" ADD CONSTRAINT "agente_mensagens_agente_origem_id_fkey" FOREIGN KEY (agente_origem_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "agente_mensagens" ADD CONSTRAINT "agente_mensagens_pkey" PRIMARY KEY (id);


-- Tabela: agente_processo
CREATE TABLE "agente_processo" ("id" INTEGER NOT NULL DEFAULT nextval('agente_processo_id_seq'::regclass), "agente_id" INTEGER NOT NULL, "processo_id" INTEGER NOT NULL, "permissao_tipo" VARCHAR(50) DEFAULT 'acesso_completo'::character varying, "data_vinculo" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "ativo" BOOLEAN DEFAULT true, "observacoes" TEXT);
ALTER TABLE "agente_processo" ADD CONSTRAINT "agente_processo_agente_id_fkey" FOREIGN KEY (agente_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "agente_processo" ADD CONSTRAINT "agente_processo_agente_id_processo_id_key" UNIQUE (agente_id, agente_id, processo_id, processo_id);
ALTER TABLE "agente_processo" ADD CONSTRAINT "agente_processo_pkey" PRIMARY KEY (id);
ALTER TABLE "agente_processo" ADD CONSTRAINT "agente_processo_processo_id_fkey" FOREIGN KEY (processo_id) REFERENCES "processo_juridico" (id);


-- Tabela: analise_comparativa
CREATE TABLE "analise_comparativa" ("id" INTEGER NOT NULL DEFAULT nextval('analise_comparativa_id_seq'::regclass), "analise_principal_id" INTEGER NOT NULL, "analise_comparada_id" INTEGER NOT NULL, "resultado_comparacao" TEXT NOT NULL, "resultado_comparacao_html" TEXT, "nivel_concordancia" INTEGER, "pontos_concordantes" TEXT, "pontos_divergentes" TEXT, "pontos_complementares" TEXT, "data_comparacao" TIMESTAMP WITHOUT TIME ZONE, "usuario_id" INTEGER);
ALTER TABLE "analise_comparativa" ADD CONSTRAINT "analise_comparativa_analise_comparada_id_fkey" FOREIGN KEY (analise_comparada_id) REFERENCES "analise_documento" (id);
ALTER TABLE "analise_comparativa" ADD CONSTRAINT "analise_comparativa_analise_principal_id_fkey" FOREIGN KEY (analise_principal_id) REFERENCES "analise_documento" (id);
ALTER TABLE "analise_comparativa" ADD CONSTRAINT "analise_comparativa_pkey" PRIMARY KEY (id);
ALTER TABLE "analise_comparativa" ADD CONSTRAINT "analise_comparativa_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: analise_documento
CREATE TABLE "analise_documento" ("id" INTEGER NOT NULL DEFAULT nextval('analise_documento_id_seq'::regclass), "documento_id" INTEGER NOT NULL, "versao_id" INTEGER, "agente_id" INTEGER NOT NULL, "conteudo_analise" TEXT NOT NULL, "conteudo_analise_html" TEXT, "data_analise" TIMESTAMP WITHOUT TIME ZONE, "metadados" TEXT);
ALTER TABLE "analise_documento" ADD CONSTRAINT "analise_documento_agente_id_fkey" FOREIGN KEY (agente_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "analise_documento" ADD CONSTRAINT "analise_documento_pkey" PRIMARY KEY (id);
ALTER TABLE "analise_documento" ADD CONSTRAINT "analise_documento_versao_id_fkey" FOREIGN KEY (versao_id) REFERENCES "versao_documento" (id);


-- Tabela: analise_especialista_individual
CREATE TABLE "analise_especialista_individual" ("id" VARCHAR(36) NOT NULL, "codigo_analise" VARCHAR(20) NOT NULL, "usuario_id" INTEGER NOT NULL, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "documento_original" TEXT NOT NULL, "documento_nome" VARCHAR(255), "documento_tipo" VARCHAR(100), "agente_id" INTEGER NOT NULL, "agente_nome" VARCHAR(255) NOT NULL, "agente_especialidade" VARCHAR(255) NOT NULL, "agente_nivel_experiencia" VARCHAR(50) NOT NULL, "area_juridica" VARCHAR(255) NOT NULL, "opiniao_juridica" TEXT NOT NULL, "fundamentacao_legal" TEXT, "jurisprudencia_citada" JSON, "doutrina_citada" JSON, "legislacao_aplicavel" JSON, "pontos_positivos" JSON, "pontos_negativos" JSON, "riscos_identificados" JSON, "recomendacoes" TEXT, "conclusao_geral" TEXT, "nivel_confianca" DOUBLE PRECISION, "complexidade_documento" VARCHAR(20), "urgencia_recomendada" VARCHAR(20), "status" VARCHAR(30), "tempo_processamento" INTEGER, "modelo_ia_utilizado" VARCHAR(100), "tokens_utilizados" INTEGER, "embeddings_consultados" INTEGER, "documentos_referencia" JSON);
ALTER TABLE "analise_especialista_individual" ADD CONSTRAINT "analise_especialista_individual_codigo_analise_key" UNIQUE (codigo_analise);
ALTER TABLE "analise_especialista_individual" ADD CONSTRAINT "analise_especialista_individual_pkey" PRIMARY KEY (id);
ALTER TABLE "analise_especialista_individual" ADD CONSTRAINT "analise_especialista_individual_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: analise_individual_agente
CREATE TABLE "analise_individual_agente" ("id" VARCHAR(36) NOT NULL, "validacao_id" VARCHAR(36) NOT NULL, "agente_id" INTEGER NOT NULL, "agente_nome" VARCHAR(255) NOT NULL, "agente_especialidade" VARCHAR(255) NOT NULL, "agente_nivel_experiencia" VARCHAR(50) NOT NULL, "opiniao_juridica" TEXT NOT NULL, "fundamentacao_legal" TEXT, "jurisprudencia_citada" JSON, "doutrina_citada" JSON, "legislacao_aplicavel" JSON, "pontos_positivos" JSON, "pontos_negativos" JSON, "riscos_identificados" JSON, "recomendacoes" TEXT, "nivel_confianca" DOUBLE PRECISION, "complexidade_documento" VARCHAR(20), "urgencia_recomendada" VARCHAR(20), "data_analise" TIMESTAMP WITHOUT TIME ZONE, "tempo_processamento" INTEGER, "modelo_ia_utilizado" VARCHAR(100), "tokens_utilizados" INTEGER, "embeddings_consultados" INTEGER, "documentos_referencia" JSON);
ALTER TABLE "analise_individual_agente" ADD CONSTRAINT "analise_individual_agente_pkey" PRIMARY KEY (id);
ALTER TABLE "analise_individual_agente" ADD CONSTRAINT "analise_individual_agente_validacao_id_fkey" FOREIGN KEY (validacao_id) REFERENCES "validacao_multi_agente" (id);


-- Tabela: analise_juridica
CREATE TABLE "analise_juridica" ("id" INTEGER NOT NULL DEFAULT nextval('analise_juridica_id_seq'::regclass), "numero_registro" VARCHAR(50) NOT NULL, "usuario_id" INTEGER NOT NULL, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "texto_original" TEXT NOT NULL, "resultados_json" TEXT NOT NULL, "total_agentes" INTEGER NOT NULL, "status" VARCHAR(20));
ALTER TABLE "analise_juridica" ADD CONSTRAINT "analise_juridica_numero_registro_key" UNIQUE (numero_registro);
ALTER TABLE "analise_juridica" ADD CONSTRAINT "analise_juridica_pkey" PRIMARY KEY (id);
ALTER TABLE "analise_juridica" ADD CONSTRAINT "analise_juridica_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: analise_processo_ia
CREATE TABLE "analise_processo_ia" ("id" INTEGER NOT NULL DEFAULT nextval('analise_processo_ia_id_seq'::regclass), "processo_id" INTEGER NOT NULL, "tipo_analise" VARCHAR(50) NOT NULL, "modelo_ia" VARCHAR(50) NOT NULL, "resultado" JSON NOT NULL, "confianca" DOUBLE PRECISION, "criado_em" TIMESTAMP WITHOUT TIME ZONE, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE, "usuario_id" INTEGER NOT NULL, "tempo_processamento" INTEGER, "status" VARCHAR(20));
ALTER TABLE "analise_processo_ia" ADD CONSTRAINT "analise_processo_ia_pkey" PRIMARY KEY (id);
ALTER TABLE "analise_processo_ia" ADD CONSTRAINT "analise_processo_ia_processo_id_fkey" FOREIGN KEY (processo_id) REFERENCES "processo_juridico" (id);
ALTER TABLE "analise_processo_ia" ADD CONSTRAINT "analise_processo_ia_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: arquivo_relacional
CREATE TABLE "arquivo_relacional" ("id" INTEGER NOT NULL DEFAULT nextval('arquivo_relacional_id_seq'::regclass), "filename" VARCHAR(255) NOT NULL, "original_filename" VARCHAR(255) NOT NULL, "file_type" VARCHAR(10) NOT NULL, "file_size" INTEGER NOT NULL, "file_path" VARCHAR(500) NOT NULL, "category" VARCHAR(50), "description" TEXT, "uploaded_by" INTEGER NOT NULL, "created_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "arquivo_relacional" ADD CONSTRAINT "arquivo_relacional_pkey" PRIMARY KEY (id);
ALTER TABLE "arquivo_relacional" ADD CONSTRAINT "arquivo_relacional_uploaded_by_fkey" FOREIGN KEY (uploaded_by) REFERENCES "user" (id);


-- Tabela: arquivo_transcricao
CREATE TABLE "arquivo_transcricao" ("id" VARCHAR(36) NOT NULL, "usuario_id" INTEGER NOT NULL, "data_upload" TIMESTAMP WITHOUT TIME ZONE, "arquivo_nome" VARCHAR(255) NOT NULL, "arquivo_path" VARCHAR(500) NOT NULL, "arquivo_tipo" VARCHAR(100) NOT NULL, "arquivo_tamanho" INTEGER NOT NULL, "hash_arquivo" VARCHAR(64), "duracao" INTEGER, "taxa_amostragem" INTEGER, "bitrate" INTEGER, "canais" INTEGER, "metadados" TEXT, "status" VARCHAR(30), "status_mensagem" VARCHAR(255), "prioridade" INTEGER, "configuracoes" TEXT);
ALTER TABLE "arquivo_transcricao" ADD CONSTRAINT "arquivo_transcricao_pkey" PRIMARY KEY (id);
ALTER TABLE "arquivo_transcricao" ADD CONSTRAINT "arquivo_transcricao_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: assistente_prompt_templates
CREATE TABLE "assistente_prompt_templates" ("id" INTEGER NOT NULL DEFAULT nextval('assistente_prompt_templates_id_seq'::regclass), "nome" VARCHAR(255) NOT NULL, "descricao" VARCHAR(500), "modelo_llm" VARCHAR(100) NOT NULL, "template_sistema" TEXT NOT NULL, "contexto_padrao" TEXT, "config_json" TEXT, "temperatura" DOUBLE PRECISION, "top_p" DOUBLE PRECISION, "top_k" INTEGER, "ativo" BOOLEAN, "criado_em" TIMESTAMP WITHOUT TIME ZONE, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE, "criado_por" VARCHAR(100));
ALTER TABLE "assistente_prompt_templates" ADD CONSTRAINT "assistente_prompt_templates_pkey" PRIMARY KEY (id);


-- Tabela: audio_transcriptions
CREATE TABLE "audio_transcriptions" ("id" INTEGER NOT NULL DEFAULT nextval('audio_transcriptions_id_seq'::regclass), "user_id" INTEGER, "filename" VARCHAR(500), "file_size" BIGINT, "status" VARCHAR(20) DEFAULT 'processing'::character varying, "transcript_text" TEXT, "duration" DOUBLE PRECISION, "speaker_detection" BOOLEAN DEFAULT true, "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "completed_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "audio_transcriptions" ADD CONSTRAINT "audio_transcriptions_pkey" PRIMARY KEY (id);
ALTER TABLE "audio_transcriptions" ADD CONSTRAINT "audio_transcriptions_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user" (id);


-- Tabela: audit_log
CREATE TABLE "audit_log" ("id" INTEGER NOT NULL DEFAULT nextval('audit_log_id_seq'::regclass), "timestamp" TIMESTAMP WITHOUT TIME ZONE, "user_id" INTEGER, "action" VARCHAR(50) NOT NULL, "entity_type" VARCHAR(50), "entity_id" VARCHAR(50), "details" TEXT, "ip_address" VARCHAR(45));
ALTER TABLE "audit_log" ADD CONSTRAINT "audit_log_pkey" PRIMARY KEY (id);
ALTER TABLE "audit_log" ADD CONSTRAINT "audit_log_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user" (id);


-- Tabela: auto_chapters
CREATE TABLE "auto_chapters" ("id" INTEGER NOT NULL DEFAULT nextval('auto_chapters_id_seq'::regclass), "transcricao_id" INTEGER, "gist" VARCHAR(500), "headline" VARCHAR(255), "summary" TEXT, "start_time" INTEGER, "end_time" INTEGER);
ALTER TABLE "auto_chapters" ADD CONSTRAINT "auto_chapters_pkey" PRIMARY KEY (id);
ALTER TABLE "auto_chapters" ADD CONSTRAINT "auto_chapters_transcricao_id_fkey" FOREIGN KEY (transcricao_id) REFERENCES "transcricoes_video" (id);


-- Tabela: auto_highlights
CREATE TABLE "auto_highlights" ("id" INTEGER NOT NULL DEFAULT nextval('auto_highlights_id_seq'::regclass), "transcricao_id" INTEGER, "text" TEXT, "count" INTEGER, "rank" DOUBLE PRECISION, "timestamps" JSONB);
ALTER TABLE "auto_highlights" ADD CONSTRAINT "auto_highlights_pkey" PRIMARY KEY (id);
ALTER TABLE "auto_highlights" ADD CONSTRAINT "auto_highlights_transcricao_id_fkey" FOREIGN KEY (transcricao_id) REFERENCES "transcricoes_video" (id);


-- Tabela: avaliacao_agente
CREATE TABLE "avaliacao_agente" ("id" INTEGER NOT NULL DEFAULT nextval('avaliacao_agente_id_seq'::regclass), "agente_id" INTEGER NOT NULL, "usuario_id" INTEGER NOT NULL, "documento_id" INTEGER, "rating" INTEGER NOT NULL, "comentario" TEXT, "data_avaliacao" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "avaliacao_agente" ADD CONSTRAINT "avaliacao_agente_agente_id_fkey" FOREIGN KEY (agente_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "avaliacao_agente" ADD CONSTRAINT "avaliacao_agente_pkey" PRIMARY KEY (id);
ALTER TABLE "avaliacao_agente" ADD CONSTRAINT "avaliacao_agente_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: cache_resposta_api
CREATE TABLE "cache_resposta_api" ("id" INTEGER NOT NULL DEFAULT nextval('cache_resposta_api_id_seq'::regclass), "provedor" VARCHAR(50) NOT NULL, "modelo" VARCHAR(50) NOT NULL, "hash_prompt" VARCHAR(64) NOT NULL, "prompt" TEXT NOT NULL, "resposta" TEXT NOT NULL, "parametros" TEXT, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_expiracao" TIMESTAMP WITHOUT TIME ZONE, "contador_uso" INTEGER);
ALTER TABLE "cache_resposta_api" ADD CONSTRAINT "cache_resposta_api_pkey" PRIMARY KEY (id);


-- Tabela: cadastro_clientes
CREATE TABLE "cadastro_clientes" ("id" INTEGER NOT NULL DEFAULT nextval('cadastro_clientes_id_seq'::regclass), "tipo_pessoa" VARCHAR(20), "nome_completo" TEXT, "cpf" VARCHAR(14), "cnpj" VARCHAR(18), "email" VARCHAR(255), "telefone" VARCHAR(20), "endereco" TEXT, "data_cadastro" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "ativo" BOOLEAN DEFAULT true);
ALTER TABLE "cadastro_clientes" ADD CONSTRAINT "cadastro_clientes_pkey" PRIMARY KEY (id);


-- Tabela: cash_flow_categoria
CREATE TABLE "cash_flow_categoria" ("id" INTEGER NOT NULL DEFAULT nextval('cash_flow_categoria_id_seq'::regclass), "nome" VARCHAR(100) NOT NULL, "tipo" VARCHAR(20) NOT NULL, "descricao" TEXT, "ativa" BOOLEAN, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "criado_por_id" INTEGER);
ALTER TABLE "cash_flow_categoria" ADD CONSTRAINT "cash_flow_categoria_criado_por_id_fkey" FOREIGN KEY (criado_por_id) REFERENCES "user" (id);
ALTER TABLE "cash_flow_categoria" ADD CONSTRAINT "cash_flow_categoria_nome_key" UNIQUE (nome);
ALTER TABLE "cash_flow_categoria" ADD CONSTRAINT "cash_flow_categoria_pkey" PRIMARY KEY (id);


-- Tabela: cash_flow_lancamento
CREATE TABLE "cash_flow_lancamento" ("id" INTEGER NOT NULL DEFAULT nextval('cash_flow_lancamento_id_seq'::regclass), "data_lancamento" TIMESTAMP WITHOUT TIME ZONE NOT NULL, "descricao" VARCHAR(255) NOT NULL, "valor" DOUBLE PRECISION NOT NULL, "tipo" VARCHAR(20) NOT NULL, "categoria_id" INTEGER, "processo_id" INTEGER, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "criado_por_id" INTEGER);
ALTER TABLE "cash_flow_lancamento" ADD CONSTRAINT "cash_flow_lancamento_categoria_id_fkey" FOREIGN KEY (categoria_id) REFERENCES "cash_flow_categoria" (id);
ALTER TABLE "cash_flow_lancamento" ADD CONSTRAINT "cash_flow_lancamento_criado_por_id_fkey" FOREIGN KEY (criado_por_id) REFERENCES "user" (id);
ALTER TABLE "cash_flow_lancamento" ADD CONSTRAINT "cash_flow_lancamento_pkey" PRIMARY KEY (id);
ALTER TABLE "cash_flow_lancamento" ADD CONSTRAINT "cash_flow_lancamento_processo_id_fkey" FOREIGN KEY (processo_id) REFERENCES "processo_juridico" (id);


-- Tabela: cash_flow_operacional
CREATE TABLE "cash_flow_operacional" ("id" INTEGER NOT NULL DEFAULT nextval('cash_flow_operacional_id_seq'::regclass), "ano" INTEGER NOT NULL, "mes" INTEGER NOT NULL, "honorarios_processos" DOUBLE PRECISION NOT NULL, "consultorias" DOUBLE PRECISION NOT NULL, "due_diligence" DOUBLE PRECISION NOT NULL, "pareceres_juridicos" DOUBLE PRECISION NOT NULL, "contratos_especiais" DOUBLE PRECISION NOT NULL, "outras_receitas" DOUBLE PRECISION NOT NULL, "custos_processuais" DOUBLE PRECISION NOT NULL, "despesas_operacionais" DOUBLE PRECISION NOT NULL, "pagamento_colaboradores" DOUBLE PRECISION NOT NULL, "impostos_taxas" DOUBLE PRECISION NOT NULL, "marketing_captacao" DOUBLE PRECISION NOT NULL, "tecnologia_sistemas" DOUBLE PRECISION NOT NULL, "outras_despesas" DOUBLE PRECISION NOT NULL, "total_entradas" DOUBLE PRECISION NOT NULL, "total_saidas" DOUBLE PRECISION NOT NULL, "resultado_operacional" DOUBLE PRECISION NOT NULL, "margem_operacional" DOUBLE PRECISION NOT NULL, "processos_quantidade" INTEGER NOT NULL, "ciclo_medio_dias" INTEGER NOT NULL, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "criado_por_id" INTEGER);
ALTER TABLE "cash_flow_operacional" ADD CONSTRAINT "cash_flow_operacional_criado_por_id_fkey" FOREIGN KEY (criado_por_id) REFERENCES "user" (id);
ALTER TABLE "cash_flow_operacional" ADD CONSTRAINT "cash_flow_operacional_pkey" PRIMARY KEY (id);
ALTER TABLE "cash_flow_operacional" ADD CONSTRAINT "uk_cashflow_ano_mes" UNIQUE (ano, ano, mes, mes);


-- Tabela: categoria_juridica
CREATE TABLE "categoria_juridica" ("id" INTEGER NOT NULL DEFAULT nextval('categoria_juridica_id_seq'::regclass), "nome" VARCHAR(100) NOT NULL, "descricao" TEXT, "icone" VARCHAR(50), "cor" VARCHAR(20), "ativa" BOOLEAN, "created_at" TIMESTAMP WITHOUT TIME ZONE, "updated_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "categoria_juridica" ADD CONSTRAINT "categoria_juridica_nome_key" UNIQUE (nome);
ALTER TABLE "categoria_juridica" ADD CONSTRAINT "categoria_juridica_pkey" PRIMARY KEY (id);


-- Tabela: categoria_template
CREATE TABLE "categoria_template" ("id" INTEGER NOT NULL DEFAULT nextval('categoria_template_id_seq'::regclass), "nome" VARCHAR(100) NOT NULL, "descricao" TEXT, "icone" VARCHAR(50), "cor" VARCHAR(20), "ordem" INTEGER, "ativa" BOOLEAN, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_modificacao" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "categoria_template" ADD CONSTRAINT "categoria_template_nome_key" UNIQUE (nome);
ALTER TABLE "categoria_template" ADD CONSTRAINT "categoria_template_pkey" PRIMARY KEY (id);


-- Tabela: categorias_documento
CREATE TABLE "categorias_documento" ("id" INTEGER NOT NULL DEFAULT nextval('categorias_documento_id_seq'::regclass), "nome" VARCHAR(100) NOT NULL, "descricao" VARCHAR(255), "icone" VARCHAR(50), "cor_tema" VARCHAR(7), "ativo" BOOLEAN, "criado_em" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "categorias_documento" ADD CONSTRAINT "categorias_documento_nome_key" UNIQUE (nome);
ALTER TABLE "categorias_documento" ADD CONSTRAINT "categorias_documento_pkey" PRIMARY KEY (id);


-- Tabela: chunk_documento
CREATE TABLE "chunk_documento" ("id" INTEGER NOT NULL DEFAULT nextval('chunk_documento_id_seq'::regclass), "document_id" INTEGER NOT NULL, "chunk_id" VARCHAR(50) NOT NULL, "chunk_index" INTEGER NOT NULL, "titulo" VARCHAR(200), "subtitulo" VARCHAR(200), "referencia" VARCHAR(100), "conteudo" TEXT NOT NULL, "conteudo_simplificado" TEXT, "palavras" INTEGER NOT NULL, "relevance_score" INTEGER, "densidade_juridica" DOUBLE PRECISION, "embedding_stored" BOOLEAN, "created_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "chunk_documento" ADD CONSTRAINT "chunk_documento_pkey" PRIMARY KEY (id);


-- Tabela: comparacao_documento
CREATE TABLE "comparacao_documento" ("id" VARCHAR(36) NOT NULL, "titulo" VARCHAR(200) NOT NULL, "area_processo" VARCHAR(100) NOT NULL, "descricao_area" VARCHAR(100), "documento_cliente" VARCHAR(20), "user_id" INTEGER, "data_comparacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "resultado_html_lado_a" TEXT NOT NULL, "resultado_html_lado_b" TEXT NOT NULL, "resultado_editado_a" TEXT, "resultado_editado_b" TEXT, "total_diferencas" INTEGER, "total_adicoes" INTEGER, "total_remocoes" INTEGER, "percentual_similaridade" DOUBLE PRECISION, "formato_exportacao" VARCHAR(10), "incluir_marcacoes" BOOLEAN, "status" VARCHAR(20), "status_mensagem" TEXT, "analise_ia" TEXT);
ALTER TABLE "comparacao_documento" ADD CONSTRAINT "comparacao_documento_pkey" PRIMARY KEY (id);
ALTER TABLE "comparacao_documento" ADD CONSTRAINT "comparacao_documento_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user" (id);


-- Tabela: componente_editor
CREATE TABLE "componente_editor" ("id" INTEGER NOT NULL DEFAULT nextval('componente_editor_id_seq'::regclass), "nome" VARCHAR(200) NOT NULL, "categoria" VARCHAR(100) NOT NULL, "tipo" VARCHAR(100) NOT NULL, "descricao" TEXT, "descricao_detalhada" TEXT, "icone" VARCHAR(100), "cor" VARCHAR(20), "ativo" BOOLEAN, "configuracao" JSON, "prompt_sistema" TEXT, "prompt_usuario" TEXT, "capacidades" JSON, "parametros" JSON, "base_conhecimento" VARCHAR(200), "temperatura" DOUBLE PRECISION, "max_tokens" INTEGER, "top_k" INTEGER, "chunk_size" INTEGER, "chunk_overlap" INTEGER, "criado_em" TIMESTAMP WITHOUT TIME ZONE, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "componente_editor" ADD CONSTRAINT "componente_editor_pkey" PRIMARY KEY (id);


-- Tabela: content_safety
CREATE TABLE "content_safety" ("id" INTEGER NOT NULL DEFAULT nextval('content_safety_id_seq'::regclass), "transcricao_id" INTEGER, "text" TEXT, "label" VARCHAR(100), "confidence" DOUBLE PRECISION, "severity" DOUBLE PRECISION, "start_time" INTEGER, "end_time" INTEGER);
ALTER TABLE "content_safety" ADD CONSTRAINT "content_safety_pkey" PRIMARY KEY (id);
ALTER TABLE "content_safety" ADD CONSTRAINT "content_safety_transcricao_id_fkey" FOREIGN KEY (transcricao_id) REFERENCES "transcricoes_video" (id);


-- Tabela: documento
CREATE TABLE "documento" ("id" INTEGER NOT NULL DEFAULT nextval('documento_id_seq'::regclass), "titulo" VARCHAR(200) NOT NULL, "descricao" TEXT, "tipo" VARCHAR(50), "usuario_id" INTEGER NOT NULL, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "tags" VARCHAR(255), "hash_conteudo" VARCHAR(64));
ALTER TABLE "documento" ADD CONSTRAINT "documento_pkey" PRIMARY KEY (id);
ALTER TABLE "documento" ADD CONSTRAINT "documento_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: documento_carregado
CREATE TABLE "documento_carregado" ("id" INTEGER NOT NULL DEFAULT nextval('documento_carregado_id_seq'::regclass), "agent_id" INTEGER NOT NULL, "user_id" INTEGER, "filename" VARCHAR(255) NOT NULL, "original_filename" VARCHAR(255), "file_path" VARCHAR(500), "file_hash" VARCHAR(64), "file_size" INTEGER, "file_type" VARCHAR(50), "description" TEXT, "processing_type" VARCHAR(20), "processing_status" VARCHAR(20), "processing_message" TEXT, "chunks_count" INTEGER, "embeddings_count" INTEGER, "questions_generated" INTEGER, "created_at" TIMESTAMP WITHOUT TIME ZONE, "processed_at" TIMESTAMP WITHOUT TIME ZONE, "updated_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "documento_carregado" ADD CONSTRAINT "documento_carregado_agent_id_fkey" FOREIGN KEY (agent_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "documento_carregado" ADD CONSTRAINT "documento_carregado_pkey" PRIMARY KEY (id);
ALTER TABLE "documento_carregado" ADD CONSTRAINT "documento_carregado_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user" (id);


-- Tabela: entidade_documento
CREATE TABLE "entidade_documento" ("id" INTEGER NOT NULL DEFAULT nextval('entidade_documento_id_seq'::regclass), "documento_id" INTEGER NOT NULL, "versao_id" INTEGER, "tipo_entidade" VARCHAR(50) NOT NULL, "nome_entidade" VARCHAR(200) NOT NULL, "contexto" TEXT, "metadados" TEXT, "data_extracao" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "entidade_documento" ADD CONSTRAINT "entidade_documento_documento_id_fkey" FOREIGN KEY (documento_id) REFERENCES "documento" (id);
ALTER TABLE "entidade_documento" ADD CONSTRAINT "entidade_documento_pkey" PRIMARY KEY (id);
ALTER TABLE "entidade_documento" ADD CONSTRAINT "entidade_documento_versao_id_fkey" FOREIGN KEY (versao_id) REFERENCES "versao_documento" (id);


-- Tabela: entities
CREATE TABLE "entities" ("id" INTEGER NOT NULL DEFAULT nextval('entities_id_seq'::regclass), "transcricao_id" INTEGER, "entity_type" VARCHAR(100), "text" VARCHAR(255), "start_time" INTEGER, "end_time" INTEGER, "confidence" DOUBLE PRECISION);
ALTER TABLE "entities" ADD CONSTRAINT "entities_pkey" PRIMARY KEY (id);
ALTER TABLE "entities" ADD CONSTRAINT "entities_transcricao_id_fkey" FOREIGN KEY (transcricao_id) REFERENCES "transcricoes_video" (id);


-- Tabela: execucao_fluxo
CREATE TABLE "execucao_fluxo" ("id" INTEGER NOT NULL DEFAULT nextval('execucao_fluxo_id_seq'::regclass), "fluxo_id" INTEGER NOT NULL, "usuario_id" INTEGER, "dados_entrada" TEXT, "resultado" TEXT, "status" VARCHAR(20) NOT NULL, "mensagem_erro" TEXT, "data_inicio" TIMESTAMP WITHOUT TIME ZONE, "data_conclusao" TIMESTAMP WITHOUT TIME ZONE, "duracao_segundos" DOUBLE PRECISION, "log_execucao" TEXT);
ALTER TABLE "execucao_fluxo" ADD CONSTRAINT "execucao_fluxo_fluxo_id_fkey" FOREIGN KEY (fluxo_id) REFERENCES "fluxo" (id);
ALTER TABLE "execucao_fluxo" ADD CONSTRAINT "execucao_fluxo_pkey" PRIMARY KEY (id);
ALTER TABLE "execucao_fluxo" ADD CONSTRAINT "execucao_fluxo_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: fluxo
CREATE TABLE "fluxo" ("id" INTEGER NOT NULL DEFAULT nextval('fluxo_id_seq'::regclass), "nome" VARCHAR(100) NOT NULL, "descricao" TEXT, "agentes" TEXT, "conexoes" TEXT, "configuracao" TEXT, "ativo" BOOLEAN, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "ultima_execucao" TIMESTAMP WITHOUT TIME ZONE, "criado_por_id" INTEGER, "user_id" INTEGER, "title" VARCHAR(500), "area_juridica" VARCHAR(100), "status" VARCHAR(50) DEFAULT 'ativo'::character varying, "metadata" JSONB DEFAULT '{}'::jsonb, "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP);
ALTER TABLE "fluxo" ADD CONSTRAINT "fluxo_criado_por_id_fkey" FOREIGN KEY (criado_por_id) REFERENCES "user" (id);
ALTER TABLE "fluxo" ADD CONSTRAINT "fluxo_pkey" PRIMARY KEY (id);


-- Tabela: fluxo_resultado
CREATE TABLE "fluxo_resultado" ("id" INTEGER NOT NULL DEFAULT nextval('fluxo_resultado_id_seq'::regclass), "fluxo_id" INTEGER, "execucao_id" INTEGER, "resultado_json" JSONB, "tempo_execucao" DOUBLE PRECISION, "status" VARCHAR(20), "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "flow_id" INTEGER, "result_type" VARCHAR(100), "title" VARCHAR(500), "content" TEXT, "analysis" JSONB, "execution_time" NUMERIC(10,2));
ALTER TABLE "fluxo_resultado" ADD CONSTRAINT "fluxo_resultado_execucao_id_fkey" FOREIGN KEY (execucao_id) REFERENCES "execucao_fluxo" (id);
ALTER TABLE "fluxo_resultado" ADD CONSTRAINT "fluxo_resultado_fluxo_id_fkey" FOREIGN KEY (fluxo_id) REFERENCES "fluxo" (id);
ALTER TABLE "fluxo_resultado" ADD CONSTRAINT "fluxo_resultado_pkey" PRIMARY KEY (id);


-- Tabela: historico_documento
CREATE TABLE "historico_documento" ("id" INTEGER NOT NULL DEFAULT nextval('historico_documento_id_seq'::regclass), "template_id" INTEGER NOT NULL, "usuario_id" INTEGER NOT NULL, "titulo_documento" VARCHAR(300) NOT NULL, "formato_exportacao" VARCHAR(10), "tamanho_arquivo" INTEGER, "campos_preenchidos" JSON, "configuracoes_geracao" JSON, "ip_usuario" VARCHAR(45), "user_agent" VARCHAR(500), "status" VARCHAR(20), "caminho_arquivo" VARCHAR(500), "gerado_em" TIMESTAMP WITHOUT TIME ZONE, "baixado_em" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "historico_documento" ADD CONSTRAINT "historico_documento_pkey" PRIMARY KEY (id);
ALTER TABLE "historico_documento" ADD CONSTRAINT "historico_documento_template_id_fkey" FOREIGN KEY (template_id) REFERENCES "templates_documento" (id);
ALTER TABLE "historico_documento" ADD CONSTRAINT "historico_documento_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: historico_pagamentos
CREATE TABLE "historico_pagamentos" ("id" INTEGER NOT NULL DEFAULT nextval('historico_pagamentos_id_seq'::regclass), "processo_id" INTEGER NOT NULL, "data_pagamento" TIMESTAMP WITHOUT TIME ZONE NOT NULL, "tipo_pagamento" VARCHAR(100) NOT NULL, "valor" DOUBLE PRECISION NOT NULL, "descricao" TEXT, "status" VARCHAR(50) NOT NULL, "forma_pagamento" VARCHAR(50), "comprovante" VARCHAR(255), "observacoes" TEXT, "criado_em" TIMESTAMP WITHOUT TIME ZONE NOT NULL, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE NOT NULL, "criado_por_id" INTEGER NOT NULL);
ALTER TABLE "historico_pagamentos" ADD CONSTRAINT "historico_pagamentos_criado_por_id_fkey" FOREIGN KEY (criado_por_id) REFERENCES "user" (id);
ALTER TABLE "historico_pagamentos" ADD CONSTRAINT "historico_pagamentos_pkey" PRIMARY KEY (id);
ALTER TABLE "historico_pagamentos" ADD CONSTRAINT "historico_pagamentos_processo_id_fkey" FOREIGN KEY (processo_id) REFERENCES "processo_juridico" (id);


-- Tabela: historico_template
CREATE TABLE "historico_template" ("id" INTEGER NOT NULL DEFAULT nextval('historico_template_id_seq'::regclass), "template_id" INTEGER NOT NULL, "usuario_id" INTEGER NOT NULL, "campos_preenchidos" JSON, "documento_gerado" TEXT, "formato_saida" VARCHAR(10), "gerado_em" TIMESTAMP WITHOUT TIME ZONE, "ip_usuario" VARCHAR(45), "user_agent" VARCHAR(255));
ALTER TABLE "historico_template" ADD CONSTRAINT "historico_template_pkey" PRIMARY KEY (id);
ALTER TABLE "historico_template" ADD CONSTRAINT "historico_template_template_id_fkey" FOREIGN KEY (template_id) REFERENCES "template_juridico" (id);
ALTER TABLE "historico_template" ADD CONSTRAINT "historico_template_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: iab_categories
CREATE TABLE "iab_categories" ("id" INTEGER NOT NULL DEFAULT nextval('iab_categories_id_seq'::regclass), "transcricao_id" INTEGER, "label" VARCHAR(255), "relevance" DOUBLE PRECISION, "timestamp" INTEGER);
ALTER TABLE "iab_categories" ADD CONSTRAINT "iab_categories_pkey" PRIMARY KEY (id);
ALTER TABLE "iab_categories" ADD CONSTRAINT "iab_categories_transcricao_id_fkey" FOREIGN KEY (transcricao_id) REFERENCES "transcricoes_video" (id);


-- Tabela: inadimplencia_por_area
CREATE TABLE "inadimplencia_por_area" ("id" INTEGER NOT NULL DEFAULT nextval('inadimplencia_por_area_id_seq'::regclass), "area_juridica" VARCHAR(100) NOT NULL, "ano" INTEGER NOT NULL, "mes" INTEGER, "total_casos" INTEGER, "casos_inadimplentes" INTEGER, "taxa_inadimplencia" DOUBLE PRECISION, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "inadimplencia_por_area" ADD CONSTRAINT "inadimplencia_por_area_pkey" PRIMARY KEY (id);
ALTER TABLE "inadimplencia_por_area" ADD CONSTRAINT "uk_inadimplencia_area_periodo" UNIQUE (area_juridica, area_juridica, area_juridica, ano, ano, ano, mes, mes, mes);


-- Tabela: indicador_fluxo
CREATE TABLE "indicador_fluxo" ("id" INTEGER NOT NULL DEFAULT nextval('indicador_fluxo_id_seq'::regclass), "ano" INTEGER NOT NULL, "mes" INTEGER NOT NULL, "honorarios_processos" DOUBLE PRECISION NOT NULL, "repasse_pagamentos_custas" DOUBLE PRECISION NOT NULL, "recebimentos_acordos" DOUBLE PRECISION NOT NULL, "execucoes_realizadas" DOUBLE PRECISION NOT NULL, "custos_operacionais_processos" DOUBLE PRECISION NOT NULL, "custas_processuais_pagas" DOUBLE PRECISION NOT NULL, "despesas_cartorio" DOUBLE PRECISION NOT NULL, "honorarios_peritos" DOUBLE PRECISION NOT NULL, "total_entradas_fluxo" DOUBLE PRECISION NOT NULL, "total_saidas_fluxo" DOUBLE PRECISION NOT NULL, "saldo_liquido" DOUBLE PRECISION NOT NULL, "margem_percentual" DOUBLE PRECISION NOT NULL, "quantidade_processos" INTEGER NOT NULL, "processos_concluidos" INTEGER NOT NULL, "processos_em_andamento" INTEGER NOT NULL, "ticket_medio_processo" DOUBLE PRECISION NOT NULL, "tempo_medio_conclusao" INTEGER NOT NULL, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "criado_por_id" INTEGER);
ALTER TABLE "indicador_fluxo" ADD CONSTRAINT "indicador_fluxo_criado_por_id_fkey" FOREIGN KEY (criado_por_id) REFERENCES "user" (id);
ALTER TABLE "indicador_fluxo" ADD CONSTRAINT "indicador_fluxo_pkey" PRIMARY KEY (id);
ALTER TABLE "indicador_fluxo" ADD CONSTRAINT "uk_indicador_fluxo_ano_mes" UNIQUE (ano, ano, mes, mes);


-- Tabela: indicadores_estrategicos
CREATE TABLE "indicadores_estrategicos" ("id" INTEGER NOT NULL DEFAULT nextval('indicadores_estrategicos_id_seq'::regclass), "tipo_indicador" VARCHAR(50) NOT NULL, "area_juridica" VARCHAR(100), "mes" INTEGER, "ano" INTEGER NOT NULL, "valor_principal" DOUBLE PRECISION, "valor_secundario" DOUBLE PRECISION, "quantidade" INTEGER, "percentual" DOUBLE PRECISION, "roi" DOUBLE PRECISION, "ticket_medio" DOUBLE PRECISION, "dias_medio" INTEGER, "risco_concentracao" DOUBLE PRECISION, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "indicadores_estrategicos" ADD CONSTRAINT "indicadores_estrategicos_pkey" PRIMARY KEY (id);
ALTER TABLE "indicadores_estrategicos" ADD CONSTRAINT "uk_indicador_tipo_area_periodo" UNIQUE (tipo_indicador, tipo_indicador, tipo_indicador, tipo_indicador, area_juridica, area_juridica, area_juridica, area_juridica, ano, ano, ano, ano, mes, mes, mes, mes);


-- Tabela: lawyer_metrics
CREATE TABLE "lawyer_metrics" ("id" INTEGER NOT NULL DEFAULT nextval('lawyer_metrics_id_seq'::regclass), "advogado_nome" VARCHAR(200) NOT NULL, "total_casos" INTEGER, "eficiencia" DOUBLE PRECISION, "carteira_total" DOUBLE PRECISION, "remuneracao" DOUBLE PRECISION, "produtividade_financeira" DOUBLE PRECISION, "margem_media" DOUBLE PRECISION, "produtividade_tecnica" DOUBLE PRECISION, "roi_individual" DOUBLE PRECISION, "casos_por_milhao" DOUBLE PRECISION, "eficiencia_geral" DOUBLE PRECISION, "capital_giro_necessario" DOUBLE PRECISION, "provisao_vs_pagamento" DOUBLE PRECISION, "taxa_sucesso" DOUBLE PRECISION, "tempo_medio_conclusao" INTEGER, "honorarios_faturados" DOUBLE PRECISION, "custos_operacionais" DOUBLE PRECISION, "margem_liquida" DOUBLE PRECISION, "ticket_medio" DOUBLE PRECISION, "updated_at" TIMESTAMP WITHOUT TIME ZONE, "created_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "lawyer_metrics" ADD CONSTRAINT "lawyer_metrics_advogado_nome_key" UNIQUE (advogado_nome);
ALTER TABLE "lawyer_metrics" ADD CONSTRAINT "lawyer_metrics_pkey" PRIMARY KEY (id);


-- Tabela: legal_areas
CREATE TABLE "legal_areas" ("id" INTEGER NOT NULL DEFAULT nextval('legal_areas_id_seq'::regclass), "nome" VARCHAR(100) NOT NULL, "icone" VARCHAR(50), "cor" VARCHAR(7), "descricao" TEXT, "ativo" BOOLEAN, "criado_em" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "legal_areas" ADD CONSTRAINT "legal_areas_pkey" PRIMARY KEY (id);


-- Tabela: legal_areas_juridicas
CREATE TABLE "legal_areas_juridicas" ("id" INTEGER NOT NULL DEFAULT nextval('legal_areas_juridicas_id_seq'::regclass), "nome" VARCHAR(100) NOT NULL, "icone" VARCHAR(50) NOT NULL, "descricao" TEXT, "cor_tema" VARCHAR(7), "ativo" BOOLEAN, "ordem_exibicao" INTEGER, "criado_em" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "legal_areas_juridicas" ADD CONSTRAINT "legal_areas_juridicas_nome_key" UNIQUE (nome);
ALTER TABLE "legal_areas_juridicas" ADD CONSTRAINT "legal_areas_juridicas_pkey" PRIMARY KEY (id);


-- Tabela: legal_design_pieces
CREATE TABLE "legal_design_pieces" ("id" INTEGER NOT NULL DEFAULT nextval('legal_design_pieces_id_seq'::regclass), "titulo" VARCHAR(255) NOT NULL, "tipo_peca" VARCHAR(50), "conteudo" TEXT, "categoria" VARCHAR(50), "template_base_id" INTEGER, "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "flow_id" INTEGER, "element_type" VARCHAR(100), "title" VARCHAR(500), "content" TEXT, "position_x" NUMERIC(10,2), "position_y" NUMERIC(10,2), "order_index" INTEGER, "properties" JSONB DEFAULT '{}'::jsonb);
ALTER TABLE "legal_design_pieces" ADD CONSTRAINT "legal_design_pieces_pkey" PRIMARY KEY (id);


-- Tabela: legal_favoritos_templates
CREATE TABLE "legal_favoritos_templates" ("id" INTEGER NOT NULL DEFAULT nextval('legal_favoritos_templates_id_seq'::regclass), "usuario_id" INTEGER NOT NULL, "template_id" INTEGER NOT NULL, "criado_em" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "legal_favoritos_templates" ADD CONSTRAINT "legal_favoritos_templates_pkey" PRIMARY KEY (id);
ALTER TABLE "legal_favoritos_templates" ADD CONSTRAINT "legal_favoritos_templates_template_id_fkey" FOREIGN KEY (template_id) REFERENCES "legal_templates_juridicos" (id);
ALTER TABLE "legal_favoritos_templates" ADD CONSTRAINT "legal_favoritos_templates_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: legal_historico_uso_templates
CREATE TABLE "legal_historico_uso_templates" ("id" INTEGER NOT NULL DEFAULT nextval('legal_historico_uso_templates_id_seq'::regclass), "template_id" INTEGER NOT NULL, "usuario_id" INTEGER, "ip_address" VARCHAR(45), "user_agent" TEXT, "usado_em" TIMESTAMP WITHOUT TIME ZONE, "projeto_nome" VARCHAR(200), "modificacoes_realizadas" BOOLEAN);
ALTER TABLE "legal_historico_uso_templates" ADD CONSTRAINT "legal_historico_uso_templates_pkey" PRIMARY KEY (id);
ALTER TABLE "legal_historico_uso_templates" ADD CONSTRAINT "legal_historico_uso_templates_template_id_fkey" FOREIGN KEY (template_id) REFERENCES "legal_templates_juridicos" (id);
ALTER TABLE "legal_historico_uso_templates" ADD CONSTRAINT "legal_historico_uso_templates_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: legal_templates_juridicos
CREATE TABLE "legal_templates_juridicos" ("id" INTEGER NOT NULL DEFAULT nextval('legal_templates_juridicos_id_seq'::regclass), "nome" VARCHAR(200) NOT NULL, "descricao" TEXT, "conteudo_html" TEXT NOT NULL, "conteudo_texto" TEXT, "area_juridica_id" INTEGER NOT NULL, "tipo_documento_id" INTEGER NOT NULL, "palavras_chave" TEXT, "complexidade" VARCHAR(20), "tempo_estimado" INTEGER, "versao" VARCHAR(10), "criado_por" VARCHAR(100), "modificado_por" VARCHAR(100), "criado_em" TIMESTAMP WITHOUT TIME ZONE, "modificado_em" TIMESTAMP WITHOUT TIME ZONE, "ativo" BOOLEAN, "uso_contador" INTEGER, "favorito" BOOLEAN);
ALTER TABLE "legal_templates_juridicos" ADD CONSTRAINT "legal_templates_juridicos_area_juridica_id_fkey" FOREIGN KEY (area_juridica_id) REFERENCES "legal_areas_juridicas" (id);
ALTER TABLE "legal_templates_juridicos" ADD CONSTRAINT "legal_templates_juridicos_pkey" PRIMARY KEY (id);
ALTER TABLE "legal_templates_juridicos" ADD CONSTRAINT "legal_templates_juridicos_tipo_documento_id_fkey" FOREIGN KEY (tipo_documento_id) REFERENCES "legal_tipos_documento" (id);


-- Tabela: legal_templates_v2
CREATE TABLE "legal_templates_v2" ("id" INTEGER NOT NULL DEFAULT nextval('legal_templates_v2_id_seq'::regclass), "nome" VARCHAR(200) NOT NULL, "descricao" TEXT, "conteudo_html" TEXT NOT NULL, "area_id" INTEGER NOT NULL, "tipo_documento" VARCHAR(100), "complexidade" VARCHAR(20), "tempo_estimado" INTEGER, "uso_contador" INTEGER, "palavras_chave" TEXT, "ativo" BOOLEAN, "criado_em" TIMESTAMP WITHOUT TIME ZONE, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "legal_templates_v2" ADD CONSTRAINT "legal_templates_v2_area_id_fkey" FOREIGN KEY (area_id) REFERENCES "legal_areas" (id);
ALTER TABLE "legal_templates_v2" ADD CONSTRAINT "legal_templates_v2_pkey" PRIMARY KEY (id);


-- Tabela: legal_tipos_documento
CREATE TABLE "legal_tipos_documento" ("id" INTEGER NOT NULL DEFAULT nextval('legal_tipos_documento_id_seq'::regclass), "nome" VARCHAR(100) NOT NULL, "categoria" VARCHAR(50) NOT NULL, "descricao" TEXT, "icone" VARCHAR(50), "ativo" BOOLEAN, "criado_em" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "legal_tipos_documento" ADD CONSTRAINT "legal_tipos_documento_pkey" PRIMARY KEY (id);


-- Tabela: log_processamento_documento
CREATE TABLE "log_processamento_documento" ("id" INTEGER NOT NULL DEFAULT nextval('log_processamento_documento_id_seq'::regclass), "document_id" INTEGER, "nivel" VARCHAR(10) NOT NULL, "mensagem" TEXT NOT NULL, "detalhes" TEXT, "fase_processamento" VARCHAR(50), "tempo_processamento" DOUBLE PRECISION, "created_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "log_processamento_documento" ADD CONSTRAINT "log_processamento_documento_pkey" PRIMARY KEY (id);


-- Tabela: modelo_estatistico
CREATE TABLE "modelo_estatistico" ("id" INTEGER NOT NULL DEFAULT nextval('modelo_estatistico_id_seq'::regclass), "nome" VARCHAR(200) NOT NULL, "tipo" VARCHAR(50) NOT NULL, "descricao" TEXT, "configuracao" JSON NOT NULL, "parametros" JSON, "versao" VARCHAR(20), "ativo" BOOLEAN, "publico" BOOLEAN, "criado_em" TIMESTAMP WITHOUT TIME ZONE, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE, "criado_por_id" INTEGER NOT NULL);
ALTER TABLE "modelo_estatistico" ADD CONSTRAINT "modelo_estatistico_criado_por_id_fkey" FOREIGN KEY (criado_por_id) REFERENCES "user" (id);
ALTER TABLE "modelo_estatistico" ADD CONSTRAINT "modelo_estatistico_pkey" PRIMARY KEY (id);


-- Tabela: perfis_profissionais
CREATE TABLE "perfis_profissionais" ("id" INTEGER NOT NULL DEFAULT nextval('perfis_profissionais_id_seq'::regclass), "user_id" INTEGER, "nome_completo" VARCHAR(255), "oab_numero" VARCHAR(20), "oab_uf" VARCHAR(2), "especializacao" _text[], "areas_atuacao" _text[], "biografia" TEXT, "foto_url" VARCHAR(500), "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP);
ALTER TABLE "perfis_profissionais" ADD CONSTRAINT "perfis_profissionais_pkey" PRIMARY KEY (id);
ALTER TABLE "perfis_profissionais" ADD CONSTRAINT "perfis_profissionais_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user" (id);


-- Tabela: performance_financeira_advogado
CREATE TABLE "performance_financeira_advogado" ("id" INTEGER NOT NULL DEFAULT nextval('performance_financeira_advogado_id_seq'::regclass), "advogado_nome" VARCHAR(255) NOT NULL, "periodo_ano" INTEGER NOT NULL, "periodo_mes" INTEGER, "total_casos" INTEGER, "carteira_total" DOUBLE PRECISION, "provisao_total" DOUBLE PRECISION, "pagamento_total" DOUBLE PRECISION, "honorarios_recebidos" DOUBLE PRECISION, "margem_media" DOUBLE PRECISION, "eficiencia_media" DOUBLE PRECISION, "produtividade_financeira" DOUBLE PRECISION, "capital_giro_necessario" DOUBLE PRECISION, "ticket_medio_caso" DOUBLE PRECISION, "casos_alto_risco" INTEGER, "casos_medio_risco" INTEGER, "casos_baixo_risco" INTEGER, "valor_total_risco" DOUBLE PRECISION, "tempo_medio_conclusao" INTEGER, "taxa_sucesso" DOUBLE PRECISION, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "performance_financeira_advogado" ADD CONSTRAINT "performance_financeira_advogado_pkey" PRIMARY KEY (id);
ALTER TABLE "performance_financeira_advogado" ADD CONSTRAINT "uk_performance_advogado_periodo" UNIQUE (advogado_nome, advogado_nome, advogado_nome, periodo_ano, periodo_ano, periodo_ano, periodo_mes, periodo_mes, periodo_mes);


-- Tabela: pergunta_chunk
CREATE TABLE "pergunta_chunk" ("id" INTEGER NOT NULL DEFAULT nextval('pergunta_chunk_id_seq'::regclass), "chunk_id" INTEGER NOT NULL, "question_id" VARCHAR(50) NOT NULL, "group_index" INTEGER NOT NULL, "nivel" VARCHAR(20) NOT NULL, "pergunta" TEXT NOT NULL, "contexto" TEXT, "generated_by" VARCHAR(50), "confidence_score" DOUBLE PRECISION, "created_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "pergunta_chunk" ADD CONSTRAINT "pergunta_chunk_chunk_id_fkey" FOREIGN KEY (chunk_id) REFERENCES "chunk_documento" (id);
ALTER TABLE "pergunta_chunk" ADD CONSTRAINT "pergunta_chunk_pkey" PRIMARY KEY (id);


-- Tabela: permissao_area_juridica
CREATE TABLE "permissao_area_juridica" ("id" INTEGER NOT NULL DEFAULT nextval('permissao_area_juridica_id_seq'::regclass), "user_id" INTEGER NOT NULL, "area_juridica" VARCHAR(64) NOT NULL, "pode_visualizar" BOOLEAN, "criado_em" TIMESTAMP WITHOUT TIME ZONE, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "permissao_area_juridica" ADD CONSTRAINT "permissao_area_juridica_pkey" PRIMARY KEY (id);
ALTER TABLE "permissao_area_juridica" ADD CONSTRAINT "permissao_area_juridica_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user" (id);
ALTER TABLE "permissao_area_juridica" ADD CONSTRAINT "uix_user_area_juridica" UNIQUE (user_id, user_id, area_juridica, area_juridica);


-- Tabela: permission
CREATE TABLE "permission" ("id" INTEGER NOT NULL DEFAULT nextval('permission_id_seq'::regclass), "name" VARCHAR(64) NOT NULL, "code" VARCHAR(64) NOT NULL, "description" TEXT, "created_at" TIMESTAMP WITHOUT TIME ZONE, "updated_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "permission" ADD CONSTRAINT "permission_code_key" UNIQUE (code);
ALTER TABLE "permission" ADD CONSTRAINT "permission_name_key" UNIQUE (name);
ALTER TABLE "permission" ADD CONSTRAINT "permission_pkey" PRIMARY KEY (id);


-- Tabela: processo_juridico
CREATE TABLE "processo_juridico" ("id" INTEGER NOT NULL DEFAULT nextval('processo_juridico_id_seq'::regclass), "situacao_id" INTEGER, "numero_processo_cnj" VARCHAR(25) NOT NULL, "area_juridica" VARCHAR(100) NOT NULL, "cliente" VARCHAR(200) NOT NULL, "cpf_cliente" VARCHAR(14), "autor" VARCHAR(200) NOT NULL, "cpf_autor" VARCHAR(14), "cnpj_autor" VARCHAR(18), "cnpj" VARCHAR(18), "advogado_do_caso" VARCHAR(200) NOT NULL, "advogado_adverso" VARCHAR(200), "data_registro" TIMESTAMP WITHOUT TIME ZONE NOT NULL, "data_distribuicao" TIMESTAMP WITHOUT TIME ZONE NOT NULL, "estado" VARCHAR(50) NOT NULL, "comarca" VARCHAR(100) NOT NULL, "juizo" VARCHAR(200) NOT NULL, "resumo_dos_fatos" TEXT NOT NULL, "valor_da_causa" DOUBLE PRECISION NOT NULL, "calculo_contadores" DOUBLE PRECISION, "provisao" DOUBLE PRECISION, "execucao" DOUBLE PRECISION, "previsao_de_pagamento" TIMESTAMP WITHOUT TIME ZONE, "bloqueio" DOUBLE PRECISION, "risco" VARCHAR(50), "data_acordo" TIMESTAMP WITHOUT TIME ZONE, "acordo" DOUBLE PRECISION, "pagamento" DOUBLE PRECISION, "deposito_recursal" DOUBLE PRECISION, "funcao" VARCHAR(200), "andamento_relatorio" TEXT, "titulo" VARCHAR(255), "ano_distribuicao" INTEGER, "status" VARCHAR(100), "polo" VARCHAR(100), "empresa" VARCHAR(255), "processo" VARCHAR(50), "esfera" VARCHAR(50), "acao" VARCHAR(255), "tema" VARCHAR(255), "objeto" TEXT, "instancia" VARCHAR(100), "fase_processual" VARCHAR(100), "liminar" BOOLEAN, "valor_provisao" DOUBLE PRECISION, "estimativa_desembolso" TIMESTAMP WITHOUT TIME ZONE, "pagamentos" DOUBLE PRECISION, "posicao_simplificada" VARCHAR(255), "resultado" VARCHAR(255), "observacoes" TEXT, "penhora" DOUBLE PRECISION, "previsao_custos_futuros" DOUBLE PRECISION, "honorarios_periciais" DOUBLE PRECISION, "depositos_judiciais" DOUBLE PRECISION, "custas_processuais" DOUBLE PRECISION, "acidente_de_trabalho" BOOLEAN, "acumulo_de_funcao" BOOLEAN, "adicional_de_periculosidade" BOOLEAN, "adicional_de_sobreaviso" BOOLEAN, "adicional_noturno_e_reflexos" BOOLEAN, "ajuda_de_custo" BOOLEAN, "aplicacao_do_artigo_467_da_clt" BOOLEAN, "apresentacao_de_documentos" BOOLEAN, "artigo_384_da_clt" BOOLEAN, "beneficios_previstos_na_cct_da_2a_reclamada" BOOLEAN, "descaracterizacao_do_cargo_de_confianca" BOOLEAN, "devolucao_de_descontos" BOOLEAN, "devolucao_de_descontos_lancados_no_trct" BOOLEAN, "diferencas_de_comissoes" BOOLEAN, "diferencas_salariais" BOOLEAN, "dsrs" BOOLEAN, "equiparacao_salarial" BOOLEAN, "estabilidade" BOOLEAN, "ferias_em_dobro" BOOLEAN, "fgts_e_a_multa_de_40_porcento" BOOLEAN, "horas_extras_e_reflexos" BOOLEAN, "indenizacao_aviso_previo" BOOLEAN, "indenizacao_por_danos_materiais" BOOLEAN, "indenizacao_por_danos_morais" BOOLEAN, "integracao_das_comissoes" BOOLEAN, "integracao_das_comissoes_por_fora" BOOLEAN, "integracao_dos_premios" BOOLEAN, "intervalo_interjornada" BOOLEAN, "intervalo_intrajornada" BOOLEAN, "liberacao_das_guias_trct_e_cd_sob_pena_de_indenizacao" BOOLEAN, "multa_convencional_ou_normativa" BOOLEAN, "multa_do_artigo_477_da_clt" BOOLEAN, "outros" BOOLEAN, "plr" BOOLEAN, "quebra_de_caixa" BOOLEAN, "plano_de_saude" BOOLEAN, "reconhecimento_da_remuneracao_recebida" BOOLEAN, "reembolso_km" BOOLEAN, "reenquadramento_sindical" BOOLEAN, "reintegracao" BOOLEAN, "rescisao_indireta" BOOLEAN, "responsabilizacao_subsidiaria_da_2a_reclamada_vivo" BOOLEAN, "reversao_do_pedido_de_demissao_em_demissao_sem_justa_causa" BOOLEAN, "reversao_justa_causa" BOOLEAN, "salario_substituicao" BOOLEAN, "seguro_desemprego" BOOLEAN, "sucumbencia" BOOLEAN, "vale_refeicao" BOOLEAN, "vale_transporte" BOOLEAN, "verbas_rescisoria" BOOLEAN, "resultado_processo" VARCHAR(20), "data_encerramento" TIMESTAMP WITHOUT TIME ZONE, "valor_recuperado" DOUBLE PRECISION, "taxa_sucesso" DOUBLE PRECISION, "tempo_tramitacao_dias" INTEGER, "honorarios_sucumbencia" DOUBLE PRECISION, "motivo_encerramento" VARCHAR(200), "satisfacao_cliente" INTEGER, "judit_request_id" VARCHAR(100), "judit_ultima_consulta" TIMESTAMP WITHOUT TIME ZONE, "judit_dados_processo" JSON, "judit_movimentacoes" JSON, "judit_partes" JSON, "judit_anexos" JSON, "judit_monitoramento_id" VARCHAR(100), "judit_status_monitoramento" VARCHAR(50), "judit_sincronizado" BOOLEAN NOT NULL, "remuneracao_cargo_colaborador" DOUBLE PRECISION, "criado_em" TIMESTAMP WITHOUT TIME ZONE NOT NULL, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE NOT NULL, "usuario_id" INTEGER NOT NULL, "data_ultimo_pagamento" TIMESTAMP WITHOUT TIME ZONE, "projecao_gastos_fase" TEXT, "cenario_melhor_caso" DOUBLE PRECISION, "cenario_pior_caso" DOUBLE PRECISION, "indice_viabilidade_economica" DOUBLE PRECISION, "recebimentos_honorarios" DOUBLE PRECISION, "ciclo_financeiro_dias" INTEGER, "capital_giro_necessario" DOUBLE PRECISION, "sazonalidade_mes" INTEGER, "produtividade_financeira" DOUBLE PRECISION, "risco_concentracao" DOUBLE PRECISION, "margem_lucro_caso" DOUBLE PRECISION, "custo_operacional_caso" DOUBLE PRECISION, "valor_honorarios_contratados" DOUBLE PRECISION, "fase" VARCHAR(100), "campos_especificos" JSONB DEFAULT '{}'::jsonb, "tempo_fixado_beneficio" INTEGER, "pasta" VARCHAR(100), "parte_contraria" VARCHAR(200), "analise_estrategica" TEXT, "analise_tecnica" TEXT, "analise_estatistica" TEXT, "analise_preditiva" TEXT, "data_analise_ia" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "processo_juridico" ADD CONSTRAINT "processo_juridico_pkey" PRIMARY KEY (id);
ALTER TABLE "processo_juridico" ADD CONSTRAINT "processo_juridico_situacao_id_fkey" FOREIGN KEY (situacao_id) REFERENCES "situacao" (id);
ALTER TABLE "processo_juridico" ADD CONSTRAINT "processo_juridico_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: propriedades_rurais
CREATE TABLE "propriedades_rurais" ("id" INTEGER NOT NULL DEFAULT nextval('propriedades_rurais_id_seq'::regclass), "nome_propriedade" VARCHAR(255), "matricula" VARCHAR(50), "municipio" VARCHAR(100), "uf" VARCHAR(2), "ccir" VARCHAR(20), "car" VARCHAR(20), "proprietario_nome" VARCHAR(255), "proprietario_cpf" VARCHAR(14), "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP);
ALTER TABLE "propriedades_rurais" ADD CONSTRAINT "propriedades_rurais_pkey" PRIMARY KEY (id);


-- Tabela: relatorio_consenso
CREATE TABLE "relatorio_consenso" ("id" INTEGER NOT NULL DEFAULT nextval('relatorio_consenso_id_seq'::regclass), "uuid_relatorio" VARCHAR(36) NOT NULL, "numero_relatorio" VARCHAR(20) NOT NULL, "analise_numero_registro" VARCHAR(20) NOT NULL, "titulo_relatorio" VARCHAR(200) NOT NULL, "descricao" TEXT, "user_id" INTEGER NOT NULL, "consenso_geral" TEXT NOT NULL, "nivel_concordancia" DOUBLE PRECISION, "pontos_convergencia" JSON, "pontos_divergencia" JSON, "analise_riscos" JSON NOT NULL, "analise_melhorias" JSON NOT NULL, "estrategias_recomendadas" JSON NOT NULL, "riscos_criticos" JSON, "riscos_moderados" JSON, "riscos_baixos" JSON, "melhorias_urgentes" JSON, "melhorias_importantes" JSON, "melhorias_sugeridas" JSON, "estrategias_curto_prazo" JSON, "estrategias_medio_prazo" JSON, "estrategias_longo_prazo" JSON, "impacto_estimado" VARCHAR(20), "viabilidade_implementacao" VARCHAR(20), "recursos_necessarios" JSON, "modelo_ia_utilizado" VARCHAR(100), "tokens_consumidos" INTEGER, "custo_estimado" DOUBLE PRECISION, "tempo_processamento" DOUBLE PRECISION, "status" VARCHAR(20), "status_mensagem" TEXT, "versao" INTEGER, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "data_aprovacao" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "relatorio_consenso" ADD CONSTRAINT "relatorio_consenso_numero_relatorio_key" UNIQUE (numero_relatorio);
ALTER TABLE "relatorio_consenso" ADD CONSTRAINT "relatorio_consenso_pkey" PRIMARY KEY (id);
ALTER TABLE "relatorio_consenso" ADD CONSTRAINT "relatorio_consenso_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user" (id);
ALTER TABLE "relatorio_consenso" ADD CONSTRAINT "relatorio_consenso_uuid_relatorio_key" UNIQUE (uuid_relatorio);


-- Tabela: resultado_analise_multiagente
CREATE TABLE "resultado_analise_multiagente" ("id" VARCHAR(36) NOT NULL, "usuario_id" INTEGER NOT NULL, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "documento_original" TEXT NOT NULL, "documento_nome" VARCHAR(255), "tipo_analise" VARCHAR(50), "resultado_principal" JSON, "resultados_agentes" JSON, "agentes_utilizados" JSON, "tempo_processamento" INTEGER, "status" VARCHAR(30), "provider_principal" VARCHAR(50));
ALTER TABLE "resultado_analise_multiagente" ADD CONSTRAINT "resultado_analise_multiagente_pkey" PRIMARY KEY (id);
ALTER TABLE "resultado_analise_multiagente" ADD CONSTRAINT "resultado_analise_multiagente_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: role
CREATE TABLE "role" ("id" INTEGER NOT NULL DEFAULT nextval('role_id_seq'::regclass), "name" VARCHAR(64) NOT NULL, "description" TEXT, "created_at" TIMESTAMP WITHOUT TIME ZONE, "updated_at" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "role" ADD CONSTRAINT "role_name_key" UNIQUE (name);
ALTER TABLE "role" ADD CONSTRAINT "role_pkey" PRIMARY KEY (id);


-- Tabela: role_permissions
CREATE TABLE "role_permissions" ("role_id" INTEGER NOT NULL, "permission_id" INTEGER NOT NULL);
ALTER TABLE "role_permissions" ADD CONSTRAINT "role_permissions_permission_id_fkey" FOREIGN KEY (permission_id) REFERENCES "permission" (id);
ALTER TABLE "role_permissions" ADD CONSTRAINT "role_permissions_pkey" PRIMARY KEY (role_id, role_id, permission_id, permission_id);
ALTER TABLE "role_permissions" ADD CONSTRAINT "role_permissions_role_id_fkey" FOREIGN KEY (role_id) REFERENCES "role" (id);


-- Tabela: segunda_opiniao
CREATE TABLE "segunda_opiniao" ("id" INTEGER NOT NULL DEFAULT nextval('segunda_opiniao_id_seq'::regclass), "agente_original_id" INTEGER NOT NULL, "agente_revisor_id" INTEGER NOT NULL, "documento_id" INTEGER, "resultado_original" TEXT NOT NULL, "resultado_revisao" TEXT NOT NULL, "nivel_concordancia" INTEGER, "pontos_divergentes" TEXT, "pontos_complementares" TEXT, "data_criacao" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "segunda_opiniao" ADD CONSTRAINT "segunda_opiniao_agente_original_id_fkey" FOREIGN KEY (agente_original_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "segunda_opiniao" ADD CONSTRAINT "segunda_opiniao_agente_revisor_id_fkey" FOREIGN KEY (agente_revisor_id) REFERENCES "agente_juridico" (id);
ALTER TABLE "segunda_opiniao" ADD CONSTRAINT "segunda_opiniao_pkey" PRIMARY KEY (id);


-- Tabela: sessoes_colaborativas
CREATE TABLE "sessoes_colaborativas" ("id" INTEGER NOT NULL DEFAULT nextval('sessoes_colaborativas_id_seq'::regclass), "titulo" VARCHAR(255), "descricao" TEXT, "criador_id" INTEGER, "status" VARCHAR(20) DEFAULT 'ativa'::character varying, "data_inicio" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "data_fim" TIMESTAMP WITHOUT TIME ZONE, "participantes_ids" _int4[]);
ALTER TABLE "sessoes_colaborativas" ADD CONSTRAINT "sessoes_colaborativas_criador_id_fkey" FOREIGN KEY (criador_id) REFERENCES "user" (id);
ALTER TABLE "sessoes_colaborativas" ADD CONSTRAINT "sessoes_colaborativas_pkey" PRIMARY KEY (id);


-- Tabela: situacao
CREATE TABLE "situacao" ("id" INTEGER NOT NULL DEFAULT nextval('situacao_id_seq'::regclass), "nome" VARCHAR(50) NOT NULL, "descricao" VARCHAR(255), "criado_em" TIMESTAMP WITHOUT TIME ZONE NOT NULL);
ALTER TABLE "situacao" ADD CONSTRAINT "situacao_pkey" PRIMARY KEY (id);


-- Tabela: speaker_segments
CREATE TABLE "speaker_segments" ("id" INTEGER NOT NULL DEFAULT nextval('speaker_segments_id_seq'::regclass), "transcricao_id" INTEGER, "speaker" VARCHAR(50), "speaker_confidence" DOUBLE PRECISION, "text" TEXT, "start_time" INTEGER, "end_time" INTEGER, "confidence" DOUBLE PRECISION, "words_count" INTEGER, "channel" INTEGER);
ALTER TABLE "speaker_segments" ADD CONSTRAINT "speaker_segments_pkey" PRIMARY KEY (id);
ALTER TABLE "speaker_segments" ADD CONSTRAINT "speaker_segments_transcricao_id_fkey" FOREIGN KEY (transcricao_id) REFERENCES "transcricoes_video" (id);


-- Tabela: system_config
CREATE TABLE "system_config" ("id" INTEGER NOT NULL DEFAULT nextval('system_config_id_seq'::regclass), "system_name" VARCHAR(200), "debug_mode" BOOLEAN, "log_level" VARCHAR(20), "max_agents" INTEGER, "assemblyai_enabled" BOOLEAN, "whisper_enabled" BOOLEAN, "speaker_detection" BOOLEAN, "auto_summary" BOOLEAN, "openai_model" VARCHAR(50), "anthropic_model" VARCHAR(50), "temperature" DOUBLE PRECISION, "max_tokens" INTEGER, "session_timeout" INTEGER, "max_login_attempts" INTEGER, "lockout_duration" INTEGER, "enable_monitoring" BOOLEAN, "enable_cost_tracking" BOOLEAN, "cost_alert_threshold" DOUBLE PRECISION, "token_limit_daily" INTEGER, "enable_pdf_export" BOOLEAN, "enable_docx_export" BOOLEAN, "default_font_size" INTEGER, "last_updated" TIMESTAMP WITHOUT TIME ZONE, "updated_by" INTEGER);
ALTER TABLE "system_config" ADD CONSTRAINT "system_config_pkey" PRIMARY KEY (id);
ALTER TABLE "system_config" ADD CONSTRAINT "system_config_updated_by_fkey" FOREIGN KEY (updated_by) REFERENCES "user" (id);


-- Tabela: tema_pagina
CREATE TABLE "tema_pagina" ("id" INTEGER NOT NULL DEFAULT nextval('tema_pagina_id_seq'::regclass), "rota" VARCHAR(100) NOT NULL, "descricao" VARCHAR(255), "cores" TEXT NOT NULL, "modificado_por" INTEGER, "modificado_em" TIMESTAMP WITHOUT TIME ZONE, "ativo" BOOLEAN);
ALTER TABLE "tema_pagina" ADD CONSTRAINT "tema_pagina_modificado_por_fkey" FOREIGN KEY (modificado_por) REFERENCES "user" (id);
ALTER TABLE "tema_pagina" ADD CONSTRAINT "tema_pagina_pkey" PRIMARY KEY (id);
ALTER TABLE "tema_pagina" ADD CONSTRAINT "tema_pagina_rota_key" UNIQUE (rota);


-- Tabela: template_juridico
CREATE TABLE "template_juridico" ("id" INTEGER NOT NULL DEFAULT nextval('template_juridico_id_seq'::regclass), "nome" VARCHAR(200) NOT NULL, "descricao" TEXT, "modulo_origem" VARCHAR(50), "campos" JSON, "modelo_texto" TEXT, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_modificacao" TIMESTAMP WITHOUT TIME ZONE, "tipo_documento" VARCHAR(100), "area_juridica" VARCHAR(100), "campos_obrigatorios" JSON, "campos_opcionais" JSON, "template_conteudo" TEXT, "formatacao" JSON, "categoria_id" INTEGER, "nivel_complexidade" VARCHAR(20), "tempo_estimado" INTEGER, "ativo" BOOLEAN, "versao" VARCHAR(10), "aprovado" BOOLEAN, "criado_por" INTEGER, "criado_em" TIMESTAMP WITHOUT TIME ZONE, "modificado_em" TIMESTAMP WITHOUT TIME ZONE, "total_utilizacoes" INTEGER, "ultima_utilizacao" TIMESTAMP WITHOUT TIME ZONE);
ALTER TABLE "template_juridico" ADD CONSTRAINT "template_juridico_categoria_id_fkey" FOREIGN KEY (categoria_id) REFERENCES "categoria_template" (id);
ALTER TABLE "template_juridico" ADD CONSTRAINT "template_juridico_criado_por_fkey" FOREIGN KEY (criado_por) REFERENCES "user" (id);
ALTER TABLE "template_juridico" ADD CONSTRAINT "template_juridico_pkey" PRIMARY KEY (id);


-- Tabela: templates_documento
CREATE TABLE "templates_documento" ("id" INTEGER NOT NULL DEFAULT nextval('templates_documento_id_seq'::regclass), "nome" VARCHAR(200) NOT NULL, "descricao" TEXT, "categoria_id" INTEGER NOT NULL, "template_original_id" INTEGER, "modulo_origem" VARCHAR(50), "modulo_nome" VARCHAR(100), "area_juridica" VARCHAR(50), "icone" VARCHAR(50), "tipo_documento" VARCHAR(100), "complexidade" VARCHAR(20), "campos_obrigatorios" JSON, "campos_opcionais" JSON, "estrutura_template" TEXT, "conteudo_template" TEXT, "variaveis_template" JSON, "requer_assinatura" BOOLEAN, "permite_edicao" BOOLEAN, "versao" VARCHAR(10), "total_utilizacoes" INTEGER, "ultima_utilizacao" TIMESTAMP WITHOUT TIME ZONE, "ativo" BOOLEAN, "criado_em" TIMESTAMP WITHOUT TIME ZONE, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE, "criado_por" INTEGER);
ALTER TABLE "templates_documento" ADD CONSTRAINT "templates_documento_categoria_id_fkey" FOREIGN KEY (categoria_id) REFERENCES "categorias_documento" (id);
ALTER TABLE "templates_documento" ADD CONSTRAINT "templates_documento_criado_por_fkey" FOREIGN KEY (criado_por) REFERENCES "user" (id);
ALTER TABLE "templates_documento" ADD CONSTRAINT "templates_documento_pkey" PRIMARY KEY (id);


-- Tabela: tons_voz
CREATE TABLE "tons_voz" ("id" INTEGER NOT NULL DEFAULT nextval('tons_voz_id_seq'::regclass), "nome" VARCHAR(50) NOT NULL, "titulo" VARCHAR(100), "descricao" TEXT, "instrucao_prompt" TEXT, "velocidade_resposta" VARCHAR(20) DEFAULT 'normal'::character varying, "estrutura_resposta" VARCHAR(20) DEFAULT 'topicos'::character varying, "nivel_detalhe" VARCHAR(20) DEFAULT 'equilibrado'::character varying, "icone" VARCHAR(50), "cor_secundaria" VARCHAR(20), "ativo" BOOLEAN DEFAULT true, "criado_em" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "atualizado_em" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP);
ALTER TABLE "tons_voz" ADD CONSTRAINT "tons_voz_nome_key" UNIQUE (nome);
ALTER TABLE "tons_voz" ADD CONSTRAINT "tons_voz_pkey" PRIMARY KEY (id);


-- Tabela: transcricao
CREATE TABLE "transcricao" ("id" VARCHAR(36) NOT NULL, "usuario_id" INTEGER, "arquivo_id" VARCHAR(36), "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "arquivo_nome" VARCHAR(255) NOT NULL, "arquivo_caminho" VARCHAR(500), "arquivo_tamanho" INTEGER, "arquivo_duracao" INTEGER, "status" VARCHAR(20), "provedor" VARCHAR(50), "modelo" VARCHAR(50), "texto" TEXT, "metadados" TEXT, "resultado_json" TEXT, "sentimento" VARCHAR(20), "score_sentimento" DOUBLE PRECISION);
ALTER TABLE "transcricao" ADD CONSTRAINT "transcricao_arquivo_id_fkey" FOREIGN KEY (arquivo_id) REFERENCES "arquivo_transcricao" (id);
ALTER TABLE "transcricao" ADD CONSTRAINT "transcricao_pkey" PRIMARY KEY (id);
ALTER TABLE "transcricao" ADD CONSTRAINT "transcricao_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: transcricoes_audio
CREATE TABLE "transcricoes_audio" ("id" VARCHAR(255) NOT NULL, "filename" VARCHAR(500) NOT NULL, "file_size" BIGINT NOT NULL, "file_type" VARCHAR(10) NOT NULL, "user_id" INTEGER NOT NULL, "status" VARCHAR(20) DEFAULT 'processing'::character varying, "speaker_detection" BOOLEAN DEFAULT true, "speaker_count" INTEGER DEFAULT 15, "transcript_data" TEXT, "duration" DOUBLE PRECISION, "error_message" TEXT, "started_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "completed_at" TIMESTAMP WITHOUT TIME ZONE, "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP);
ALTER TABLE "transcricoes_audio" ADD CONSTRAINT "transcricoes_audio_pkey" PRIMARY KEY (id);
ALTER TABLE "transcricoes_audio" ADD CONSTRAINT "transcricoes_audio_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user" (id);


-- Tabela: transcricoes_video
CREATE TABLE "transcricoes_video" ("id" INTEGER NOT NULL DEFAULT nextval('transcricoes_video_id_seq'::regclass), "filename" VARCHAR(255), "file_size" INTEGER, "file_type" VARCHAR(50), "transcript_id" VARCHAR(100), "status" VARCHAR(50), "text" TEXT, "confidence" DOUBLE PRECISION, "duration" INTEGER, "audio_duration" DOUBLE PRECISION, "speaker_count" INTEGER, "word_count" INTEGER, "utterance_count" INTEGER, "summary" TEXT, "summary_type" VARCHAR(50), "config" JSONB, "audio_url" VARCHAR(500), "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, "processed_at" TIMESTAMP WITHOUT TIME ZONE, "started_at" TIMESTAMP WITHOUT TIME ZONE, "completed_at" TIMESTAMP WITHOUT TIME ZONE, "error_message" TEXT, "retry_count" INTEGER DEFAULT 0);
ALTER TABLE "transcricoes_video" ADD CONSTRAINT "transcricoes_video_pkey" PRIMARY KEY (id);


-- Tabela: transcript_words
CREATE TABLE "transcript_words" ("id" INTEGER NOT NULL DEFAULT nextval('transcript_words_id_seq'::regclass), "transcricao_id" INTEGER, "speaker_segment_id" INTEGER, "word" VARCHAR(255), "start_time" INTEGER, "end_time" INTEGER, "confidence" DOUBLE PRECISION, "speaker" VARCHAR(50), "punctuated_word" VARCHAR(255));
ALTER TABLE "transcript_words" ADD CONSTRAINT "transcript_words_pkey" PRIMARY KEY (id);
ALTER TABLE "transcript_words" ADD CONSTRAINT "transcript_words_speaker_segment_id_fkey" FOREIGN KEY (speaker_segment_id) REFERENCES "speaker_segments" (id);
ALTER TABLE "transcript_words" ADD CONSTRAINT "transcript_words_transcricao_id_fkey" FOREIGN KEY (transcricao_id) REFERENCES "transcricoes_video" (id);


-- Tabela: user
CREATE TABLE "user" ("id" INTEGER NOT NULL DEFAULT nextval('user_id_seq'::regclass), "username" VARCHAR(64) NOT NULL, "email" VARCHAR(120) NOT NULL, "password_hash" VARCHAR(256) NOT NULL, "first_name" VARCHAR(64), "last_name" VARCHAR(64), "active" BOOLEAN, "is_admin" BOOLEAN, "last_login" TIMESTAMP WITHOUT TIME ZONE, "created_at" TIMESTAMP WITHOUT TIME ZONE, "updated_at" TIMESTAMP WITHOUT TIME ZONE, "role_id" INTEGER);
ALTER TABLE "user" ADD CONSTRAINT "user_email_key" UNIQUE (email);
ALTER TABLE "user" ADD CONSTRAINT "user_pkey" PRIMARY KEY (id);
ALTER TABLE "user" ADD CONSTRAINT "user_role_id_fkey" FOREIGN KEY (role_id) REFERENCES "role" (id);
ALTER TABLE "user" ADD CONSTRAINT "user_username_key" UNIQUE (username);


-- Tabela: validacao_multi_agente
CREATE TABLE "validacao_multi_agente" ("id" VARCHAR(36) NOT NULL, "codigo_validacao" VARCHAR(20) NOT NULL, "usuario_id" INTEGER NOT NULL, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "documento_original" TEXT NOT NULL, "documento_nome" VARCHAR(255), "documento_tipo" VARCHAR(100), "agentes_utilizados" JSON NOT NULL, "total_agentes" INTEGER NOT NULL, "areas_juridicas" JSON NOT NULL, "status" VARCHAR(30), "status_mensagem" VARCHAR(500), "tempo_processamento" INTEGER, "opiniao_consolidada" TEXT, "pontos_criticos" JSON, "recomendacoes_gerais" TEXT, "configuracoes" JSON);
ALTER TABLE "validacao_multi_agente" ADD CONSTRAINT "validacao_multi_agente_codigo_validacao_key" UNIQUE (codigo_validacao);
ALTER TABLE "validacao_multi_agente" ADD CONSTRAINT "validacao_multi_agente_pkey" PRIMARY KEY (id);
ALTER TABLE "validacao_multi_agente" ADD CONSTRAINT "validacao_multi_agente_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- Tabela: validacao_multi_agente_analise
CREATE TABLE "validacao_multi_agente_analise" ("id" INTEGER NOT NULL DEFAULT nextval('validacao_multi_agente_analise_id_seq'::regclass), "uuid_analise" VARCHAR(36) NOT NULL, "hash_sha256" VARCHAR(64) NOT NULL, "numero_registro" VARCHAR(20) NOT NULL, "titulo_analise" VARCHAR(200) NOT NULL, "descricao" TEXT, "user_id" INTEGER NOT NULL, "documento_original" TEXT NOT NULL, "documento_nome" VARCHAR(255), "documento_tipo" VARCHAR(50), "documento_tamanho" INTEGER, "total_agentes_utilizados" INTEGER NOT NULL, "areas_juridicas_envolvidas" JSON NOT NULL, "configuracao_analise" JSON, "resultados_agentes" JSON NOT NULL, "opiniao_consolidada" TEXT, "pontos_criticos" JSON, "recomendacoes_prioritarias" JSON, "recomendacoes_importantes" JSON, "recomendacoes_sugeridas" JSON, "tempo_processamento_segundos" DOUBLE PRECISION, "modelos_ia_utilizados" JSON, "tokens_consumidos" INTEGER, "custo_estimado" DOUBLE PRECISION, "status" VARCHAR(20), "status_mensagem" TEXT, "fallback_mode" BOOLEAN, "debug_mode" BOOLEAN, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "data_atualizacao" TIMESTAMP WITHOUT TIME ZONE, "data_conclusao" TIMESTAMP WITHOUT TIME ZONE, "exportado_pdf" BOOLEAN, "exportado_docx" BOOLEAN, "exportado_txt" BOOLEAN);
ALTER TABLE "validacao_multi_agente_analise" ADD CONSTRAINT "validacao_multi_agente_analise_hash_sha256_key" UNIQUE (hash_sha256);
ALTER TABLE "validacao_multi_agente_analise" ADD CONSTRAINT "validacao_multi_agente_analise_numero_registro_key" UNIQUE (numero_registro);
ALTER TABLE "validacao_multi_agente_analise" ADD CONSTRAINT "validacao_multi_agente_analise_pkey" PRIMARY KEY (id);
ALTER TABLE "validacao_multi_agente_analise" ADD CONSTRAINT "validacao_multi_agente_analise_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user" (id);
ALTER TABLE "validacao_multi_agente_analise" ADD CONSTRAINT "validacao_multi_agente_analise_uuid_analise_key" UNIQUE (uuid_analise);


-- Tabela: versao_documento
CREATE TABLE "versao_documento" ("id" INTEGER NOT NULL DEFAULT nextval('versao_documento_id_seq'::regclass), "documento_id" INTEGER NOT NULL, "numero_versao" INTEGER NOT NULL, "conteudo" TEXT NOT NULL, "conteudo_html" TEXT, "comentario" VARCHAR(255), "usuario_id" INTEGER NOT NULL, "data_criacao" TIMESTAMP WITHOUT TIME ZONE, "hash_conteudo" VARCHAR(64));
ALTER TABLE "versao_documento" ADD CONSTRAINT "uix_versao_documento" UNIQUE (documento_id, documento_id, numero_versao, numero_versao);
ALTER TABLE "versao_documento" ADD CONSTRAINT "versao_documento_pkey" PRIMARY KEY (id);
ALTER TABLE "versao_documento" ADD CONSTRAINT "versao_documento_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES "user" (id);


-- =============================================
-- TOTAL: 83 TABELAS CRIADAS
-- =============================================
