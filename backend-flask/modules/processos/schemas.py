"""
Schemas de validação para Processos
Usando Marshmallow para serialização/validação
"""
from marshmallow import Schema, fields, validates, ValidationError, post_load
from decimal import Decimal
from datetime import datetime


class ProcessoSchema(Schema):
    """Schema base para Processo"""
    id_processo = fields.Int(dump_only=True)
    uuid = fields.UUID(dump_only=True)
    tenant_id = fields.Int()
    
    # Dados básicos
    numero_cnj = fields.Str(allow_none=True)
    pasta = fields.Str(required=True)
    status_id = fields.Int(required=True)
    natureza_id = fields.Int(required=True)
    
    # Cliente
    cliente_id = fields.Int(allow_none=True)
    posicao_cliente_id = fields.Int(allow_none=True)
    
    # Classificação
    acao_id = fields.Int(allow_none=True)
    procedimento_id = fields.Int(allow_none=True)
    fase_id = fields.Int(allow_none=True)
    
    # Localização
    orgao_id = fields.Int(allow_none=True)
    comarca_id = fields.Int(allow_none=True)
    vara_turma_id = fields.Int(allow_none=True)
    
    # CNJ
    justica_cnj_id = fields.Int(allow_none=True)
    instancia_cnj_id = fields.Int(allow_none=True)
    classe_cnj_id = fields.Int(allow_none=True)
    
    # Datas
    data_distribuicao = fields.DateTime(allow_none=True)
    data_criacao = fields.DateTime(dump_only=True)
    data_atualizacao = fields.DateTime(dump_only=True)
    
    # Valores
    valor_causa = fields.Decimal(as_string=True, allow_none=True)
    valor_causa_atualizado = fields.Decimal(as_string=True, allow_none=True)
    valor_envolvido = fields.Decimal(as_string=True, allow_none=True)
    valor_envolvido_atualizado = fields.Decimal(as_string=True, allow_none=True)
    contingencia = fields.Decimal(as_string=True, allow_none=True)
    
    # Prognóstico
    tipo_probabilidade_id = fields.Int(allow_none=True)
    risco_id = fields.Int(allow_none=True)
    
    # Metadados
    titulo = fields.Str(allow_none=True)
    observacao_pasta = fields.Str(allow_none=True)
    ativo = fields.Bool(dump_only=True)


class ProcessoCreateSchema(Schema):
    """Schema para criar processo"""
    # Campos obrigatórios
    pasta = fields.Str(required=True)
    natureza_id = fields.Int(required=True)
    status_id = fields.Int(required=True)
    tenant_id = fields.Int()
    
    # Campos opcionais
    numero_cnj = fields.Str()
    cliente_id = fields.Int()
    posicao_cliente_id = fields.Int()
    acao_id = fields.Int()
    procedimento_id = fields.Int()
    fase_id = fields.Int()
    orgao_id = fields.Int()
    comarca_id = fields.Int()
    vara_turma_id = fields.Int()
    justica_cnj_id = fields.Int()
    instancia_cnj_id = fields.Int()
    classe_cnj_id = fields.Int()
    
    data_distribuicao = fields.DateTime()
    
    valor_causa = fields.Decimal(as_string=True)
    valor_envolvido = fields.Decimal(as_string=True)
    contingencia = fields.Decimal(as_string=True)
    
    tipo_probabilidade_id = fields.Int()
    risco_id = fields.Int()
    
    titulo = fields.Str()
    observacao_pasta = fields.Str()
    
    # Campos específicos por natureza
    campos_especificos = fields.Dict(keys=fields.Str(), values=fields.Raw())
    dados_tributario = fields.Dict(keys=fields.Str(), values=fields.Raw())
    dados_trabalhista = fields.Dict(keys=fields.Str(), values=fields.Raw())
    dados_civel = fields.Dict(keys=fields.Str(), values=fields.Raw())
    
    @validates('numero_cnj')
    def validate_numero_cnj(self, value):
        """Valida formato do número CNJ"""
        if value:
            from .validators import CNJValidator
            if not CNJValidator.validar(value):
                raise ValidationError('Número CNJ inválido')


class ProcessoUpdateSchema(Schema):
    """Schema para atualizar processo"""
    pasta = fields.Str()
    numero_cnj = fields.Str()
    status_id = fields.Int()
    natureza_id = fields.Int()
    cliente_id = fields.Int()
    posicao_cliente_id = fields.Int()
    acao_id = fields.Int()
    procedimento_id = fields.Int()
    fase_id = fields.Int()
    orgao_id = fields.Int()
    comarca_id = fields.Int()
    vara_turma_id = fields.Int()
    justica_cnj_id = fields.Int()
    instancia_cnj_id = fields.Int()
    classe_cnj_id = fields.Int()
    
    data_distribuicao = fields.DateTime()
    
    valor_causa = fields.Decimal(as_string=True)
    valor_envolvido = fields.Decimal(as_string=True)
    contingencia = fields.Decimal(as_string=True)
    
    tipo_probabilidade_id = fields.Int()
    risco_id = fields.Int()
    
    titulo = fields.Str()
    observacao_pasta = fields.Str()
    
    campos_especificos = fields.Dict(keys=fields.Str(), values=fields.Raw())


class TributoSchema(Schema):
    """Schema para Tributo"""
    id_tributo = fields.Int(dump_only=True)
    codigo = fields.Str(required=True)
    nome = fields.Str(required=True)
    descricao = fields.Str()
    esfera = fields.Str()
    ativo = fields.Bool()


class TeseTributariaSchema(Schema):
    """Schema para Tese Tributária"""
    id_tese = fields.Int(dump_only=True)
    codigo = fields.Str(required=True)
    titulo = fields.Str(required=True)
    descricao = fields.Str()
    tributo_id = fields.Int()
    
    tema_repercussao_geral = fields.Str()
    tema_repetitivo = fields.Str()
    tribunal_origem = fields.Str()
    
    probabilidade_sucesso = fields.Decimal(as_string=True)
    fundamentacao = fields.Str()
    situacao = fields.Str()
    ativo = fields.Bool()


class ProcessoTributarioSchema(Schema):
    """Schema para Processo Tributário"""
    id_processo_tributario = fields.Int(dump_only=True)
    processo_id = fields.Int(required=True)
    tributo_id = fields.Int()
    
    numero_aiim = fields.Str()
    numero_cda = fields.Str()
    data_lancamento = fields.DateTime()
    
    valor_inscrito_cda = fields.Decimal(as_string=True)
    valor_principal = fields.Decimal(as_string=True)
    valor_multa = fields.Decimal(as_string=True)
    percentual_multa = fields.Decimal(as_string=True)
    base_calculo_multa = fields.Str()
    
    valor_juros = fields.Decimal(as_string=True)
    indice_juros = fields.Str()
    descricao_indice_juros = fields.Str()


class IndiceMonetarioSchema(Schema):
    """Schema para Índice Monetário"""
    id_indice = fields.Int(dump_only=True)
    nome = fields.Str(required=True)
    descricao = fields.Str()
    fonte_oficial = fields.Str()
    ativo = fields.Bool()


class FiltroPesquisaSchema(Schema):
    """Schema para filtros de pesquisa"""
    numero_cnj = fields.Str()
    pasta = fields.Str()
    natureza_id = fields.Int()
    status_id = fields.Int()
    cliente_id = fields.Int()
    data_inicio = fields.DateTime()
    data_fim = fields.DateTime()
    busca = fields.Str()
    
    # Novos Filtros
    advogado_id = fields.Int()
    fase_id = fields.Int()
    comarca_id = fields.Int()
    
    # Paginação
    page = fields.Int(missing=1)
    per_page = fields.Int(missing=20)
    ordenacao = fields.Str(missing='data_criacao')
    ordem = fields.Str(missing='desc')
