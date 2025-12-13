"""
Schemas de validação para campos específicos de cada área jurídica
Versão Python espelhada do campos_especificos_areas.js para validação server-side
"""

CAMPOS_ESPECIFICOS_SCHEMAS = {
    "Direito Agrário": {
        "tipo_imovel_rural": {"type": "string", "required": True, "options": ["Fazenda", "Sítio", "Chácara", "Área de Assentamento", "Terras Indígenas", "Quilombola", "Outro"]},
        "area_hectares": {"type": "float", "required": True},
        "matricula_imovel": {"type": "string", "required": False},
        "incra_envolvido": {"type": "boolean", "required": False},
        "conflito_posse": {"type": "boolean", "required": False},
        "regularizacao_fundiaria": {"type": "boolean", "required": False}
    },
    
    "Direito Civil": {
        "tipo_acao_civil": {"type": "string", "required": True, "options": ["Indenização", "Cobrança", "Rescisão Contratual", "Divórcio", "Inventário", "Usucapião", "Outro"]},
        "dano_moral_pedido": {"type": "float", "required": False},
        "dano_material_pedido": {"type": "float", "required": False},
        "prescricao_aplicavel": {"type": "int", "required": False},
        "testemunhas": {"type": "int", "required": False}
    },
    
    "Direito Trabalhista": {
        "pedido_verba": {"type": "list", "required": True},
        "data_admissao": {"type": "date", "required": True},
        "data_demissao": {"type": "date", "required": False},
        "salario_mensal": {"type": "float", "required": True},
        "funcao_exercida": {"type": "string", "required": True}
    },
    
    "Direito Penal": {
        "tipo_crime": {"type": "string", "required": True, "options": ["Furto", "Roubo", "Estelionato", "Homicídio", "Lesão Corporal", "Tráfico de Drogas", "Porte Ilegal de Arma", "Corrupção", "Outro"]},
        "fase_penal": {"type": "string", "required": True, "options": ["Inquérito Policial", "Denúncia", "Instrução", "Alegações Finais", "Sentença", "Recurso", "Trânsito em Julgado"]},
        "pena_maxima": {"type": "int", "required": False},
        "regime_prisional": {"type": "string", "required": False, "options": ["Fechado", "Semi-Aberto", "Aberto", "Não Aplicável"]},
        "preso_provisorio": {"type": "boolean", "required": False},
        "medida_cautelar": {"type": "boolean", "required": False}
    },
    
    "Direito Administrativo": {
        "tipo_acao_administrativa": {"type": "string", "required": True, "options": ["Mandado de Segurança", "Ação Anulatória", "Ação de Improbidade", "Desapropriação", "Licitação", "Concurso Público", "Servidores Públicos", "Outro"]},
        "orgao_publico": {"type": "string", "required": True},
        "ato_administrativo": {"type": "string", "required": False},
        "prazo_decadencial": {"type": "int", "required": False},
        "liminar_concedida": {"type": "boolean", "required": False}
    },
    
    "Direito Tributário": {
        "tipo_tributo": {"type": "string", "required": True, "options": ["ICMS", "ISS", "PIS/COFINS", "IRPJ", "CSLL", "INSS", "FGTS", "IPTU", "IPVA", "ITR", "IPI", "II", "IE", "IOF", "Outro"]},
        "valor_autuacao": {"type": "float", "required": False},
        "processo_administrativo": {"type": "string", "required": False},
        "parcelamento": {"type": "boolean", "required": False},
        "discussao_constitucionalidade": {"type": "boolean", "required": False},
        "repercussao_geral": {"type": "string", "required": False}
    },
    
    "Direito Empresarial": {
        "tipo_societario": {"type": "string", "required": True, "options": ["LTDA", "S/A", "EIRELI", "SLU", "Sociedade Simples", "Cooperativa", "Outro"]},
        "objeto_social": {"type": "string", "required": False},
        "capital_social": {"type": "float", "required": False},
        "recuperacao_judicial": {"type": "boolean", "required": False},
        "falencia": {"type": "boolean", "required": False},
        "dissolucao_societaria": {"type": "boolean", "required": False}
    },
    
    "Direito do Consumidor": {
        "tipo_relacao_consumo": {"type": "string", "required": True, "options": ["Produto Defeituoso", "Serviço Defeituoso", "Cobrança Indevida", "Propaganda Enganosa", "Vício do Produto", "Vício do Serviço", "Outro"]},
        "fornecedor": {"type": "string", "required": True},
        "valor_produto_servico": {"type": "float", "required": False},
        "procon_acionado": {"type": "boolean", "required": False},
        "inversao_onus_prova": {"type": "boolean", "required": False}
    },
    
    "Direito Previdenciário": {
        "tipo_beneficio": {"type": "string", "required": True, "options": ["Aposentadoria por Idade", "Aposentadoria por Tempo de Contribuição", "Aposentadoria por Invalidez", "Pensão por Morte", "Auxílio-Doença", "Auxílio-Acidente", "BPC/LOAS", "Salário-Maternidade", "Outro"]},
        "numero_beneficio": {"type": "string", "required": False},
        "tempo_contribuicao": {"type": "float", "required": False},
        "data_der": {"type": "date", "required": False},
        "rmi_calculado": {"type": "float", "required": False},
        "revisao_beneficio": {"type": "boolean", "required": False}
    },
    
    "Direito Imobiliário": {
        "tipo_imovel": {"type": "string", "required": True, "options": ["Residencial", "Comercial", "Industrial", "Terreno", "Rural", "Misto", "Outro"]},
        "matricula_registro": {"type": "string", "required": False},
        "valor_imovel": {"type": "float", "required": False},
        "financiamento": {"type": "boolean", "required": False},
        "despejo": {"type": "boolean", "required": False},
        "usucapiao": {"type": "boolean", "required": False}
    },
    
    "Direito Ambiental": {
        "tipo_dano_ambiental": {"type": "string", "required": True, "options": ["Poluição Hídrica", "Poluição Atmosférica", "Desmatamento", "Fauna", "Resíduos Sólidos", "Licenciamento", "APP", "Reserva Legal", "Outro"]},
        "orgao_fiscalizador": {"type": "string", "required": False, "options": ["IBAMA", "ICMBio", "CETESB", "INEMA", "SEMAD", "IMA", "Outro"]},
        "auto_infracao": {"type": "string", "required": False},
        "valor_multa_ambiental": {"type": "float", "required": False},
        "tac_firmado": {"type": "boolean", "required": False},
        "area_protegida": {"type": "float", "required": False}
    },
    
    "Direito Digital": {
        "tipo_caso_digital": {"type": "string", "required": True, "options": ["Vazamento de Dados", "LGPD", "Crimes Cibernéticos", "Direitos Autorais Digital", "E-commerce", "Contratos Digitais", "Fake News", "Difamação Online", "Outro"]},
        "plataforma_envolvida": {"type": "string", "required": False},
        "dados_sensiveis": {"type": "boolean", "required": False},
        "anpd_notificada": {"type": "boolean", "required": False},
        "titulares_afetados": {"type": "int", "required": False},
        "valor_dano_digital": {"type": "float", "required": False}
    },
    
    "Direito Bancário": {
        "tipo_operacao_bancaria": {"type": "string", "required": True, "options": ["Empréstimo", "Financiamento", "Cartão de Crédito", "Cheque Especial", "Conta Corrente", "Investimento", "CDC", "Leasing", "Outro"]},
        "instituicao_financeira": {"type": "string", "required": True},
        "numero_contrato_bancario": {"type": "string", "required": False},
        "taxa_juros_aplicada": {"type": "float", "required": False},
        "saldo_devedor": {"type": "float", "required": False},
        "revisao_contrato": {"type": "boolean", "required": False}
    },
    
    "Direito Securitário": {
        "tipo_seguro": {"type": "string", "required": True, "options": ["Vida", "Saúde", "Auto", "Residencial", "Empresarial", "Responsabilidade Civil", "Previdência Privada", "Outro"]},
        "seguradora": {"type": "string", "required": True},
        "numero_apolice": {"type": "string", "required": False},
        "numero_sinistro": {"type": "string", "required": False},
        "valor_indenizacao_pedido": {"type": "float", "required": False},
        "negativa_cobertura": {"type": "boolean", "required": False}
    },
    
    "Negociação e Conflitos": {
        "metodo_resolucao": {"type": "string", "required": True, "options": ["Mediação", "Conciliação", "Arbitragem", "Negociação Direta", "Outro"]},
        "valor_acordo_proposto": {"type": "float", "required": False},
        "prazo_negociacao": {"type": "int", "required": False},
        "camara_arbitragem": {"type": "string", "required": False},
        "acordo_homologado": {"type": "boolean", "required": False}
    }
}


def validar_campos_especificos(area_juridica: str, campos: dict, sanitizar: bool = True) -> tuple[bool, list[str]]:
    """
    Valida os campos específicos de uma área jurídica
    
    Args:
        area_juridica: Nome da área jurídica
        campos: Dicionário com os campos a validar
        sanitizar: Se True, remove campos não definidos no schema
        
    Returns:
        Tupla (is_valid, errors) onde is_valid é booleano e errors é lista de mensagens
    """
    errors = []
    
    # Verificar se área existe
    if area_juridica not in CAMPOS_ESPECIFICOS_SCHEMAS:
        errors.append(f"Área jurídica '{area_juridica}' não possui schema definido")
        return False, errors
    
    schema = CAMPOS_ESPECIFICOS_SCHEMAS[area_juridica]
    
    # Sanitizar: remover campos não definidos no schema
    if sanitizar:
        campos_invalidos = [k for k in campos.keys() if k not in schema]
        for campo in campos_invalidos:
            del campos[campo]
            errors.append(f"Campo '{campo}' não definido para área {area_juridica} - removido")
    
    # Validar campos obrigatórios
    for campo_nome, campo_config in schema.items():
        if campo_config.get("required", False):
            if campo_nome not in campos or campos[campo_nome] in [None, "", []]:
                errors.append(f"Campo obrigatório '{campo_nome}' não fornecido ou vazio")
    
    # Validar tipos e valores
    for campo_nome, valor in campos.items():
        # Ignorar campos não definidos no schema (permite flexibilidade)
        if campo_nome not in schema:
            continue
            
        campo_config = schema[campo_nome]
        tipo_esperado = campo_config.get("type")
        
        # Pular validação se valor é None/vazio e campo não é obrigatório
        if valor in [None, "", []] and not campo_config.get("required", False):
            continue
        
        # Validar tipo
        if tipo_esperado == "string":
            if not isinstance(valor, str):
                errors.append(f"Campo '{campo_nome}' deve ser string, recebido {type(valor).__name__}")
            # Validar opções se definidas
            elif "options" in campo_config and valor not in campo_config["options"]:
                errors.append(f"Campo '{campo_nome}' possui valor inválido. Opções permitidas: {campo_config['options']}")
                
        elif tipo_esperado == "int":
            if not isinstance(valor, int) and not (isinstance(valor, str) and valor.isdigit()):
                errors.append(f"Campo '{campo_nome}' deve ser inteiro")
                
        elif tipo_esperado == "float":
            if not isinstance(valor, (int, float)):
                errors.append(f"Campo '{campo_nome}' deve ser número")
                
        elif tipo_esperado == "boolean":
            if not isinstance(valor, bool):
                errors.append(f"Campo '{campo_nome}' deve ser booleano")
                
        elif tipo_esperado == "list":
            if not isinstance(valor, list):
                errors.append(f"Campo '{campo_nome}' deve ser lista")
                
        elif tipo_esperado == "date":
            # Aceitar string no formato ISO
            if not isinstance(valor, str):
                errors.append(f"Campo '{campo_nome}' deve ser string de data (YYYY-MM-DD)")
            else:
                # Validar formato básico
                from datetime import datetime
                try:
                    datetime.strptime(valor, "%Y-%m-%d")
                except ValueError:
                    errors.append(f"Campo '{campo_nome}' possui formato de data inválido. Use YYYY-MM-DD")
    
    return len(errors) == 0, errors
