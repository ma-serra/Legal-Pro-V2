"""
Sistema de Formulários Dinâmicos
Gera schemas JSON por natureza de processo
"""
from typing import Dict, List, Optional, Any
from models import ConfiguracaoFormulario


class FormularioDinamicoService:
    """
    Service para forms dinâmicos por natureza
    """
    
    # Schemas padrão por natureza (fallback caso não exista na DB)
    SCHEMAS_PADRAO = {
        1: {  # Tributário
            'natureza': 'Tributário',
            'campos_obrigatorios': [
                {
                    'name': 'tributo_id',
                    'label': 'Tributo',
                    'type': 'select',
                    'options_endpoint': '/api/processos/tributos'
                },
                {
                    'name': 'valor_principal',
                    'label': 'Valor Principal',
                    'type': 'currency',
                    'validation': {'min': 0}
                }
            ],
            'campos_opcionais': [
                {
                    'name': 'numero_aiim',
                    'label': 'Número AIIM',
                    'type': 'text'
                },
                {
                    'name': 'numero_cda',
                    'label': 'Número CDA',
                    'type': 'text'
                },
                {
                    'name': 'data_lancamento',
                    'label': 'Data Lançamento',
                    'type': 'date'
                },
                {
                    'name': 'valor_multa',
                    'label': 'Valor da Multa',
                    'type': 'currency'
                },
                {
                    'name': 'percentual_multa',
                    'label': 'Percentual Multa (%)',
                    'type': 'percentage'
                },
                {
                    'name': 'valor_juros',
                    'label': 'Valor dos Juros',
                    'type': 'currency'
                },
                {
                    'name': 'indice_juros',
                    'label': 'Índice de Juros',
                    'type': 'select',
                    'options': ['SELIC', 'Lei 13918', 'IPCA', 'CDI', 'Outro']
                }
            ],
            'layout': {
                'sections': [
                    {
                        'title': 'Dados Fiscais',
                        'fields': ['tributo_id', 'numero_aiim', 'numero_cda', 'data_lancamento']
                    },
                    {
                        'title': 'Valores',
                        'fields': ['valor_principal', 'valor_multa', 'percentual_multa', 'valor_juros', 'indice_juros']
                    }
                ]
            }
        },
        2: {  # Trabalhista
            'natureza': 'Trabalhista',
            'campos_obrigatorios': [],
            'campos_opcionais': [
                {
                    'name': 'tolerancia_acordo',
                    'label': 'Tolerância para Acordo',
                    'type': 'currency'
                },
                {
                    'name': 'acordo_realizado',
                    'label': 'Valor do Acordo Realizado',
                    'type': 'currency'
                },
                {
                    'name': 'data_acordo',
                    'label': 'Data do Acordo',
                    'type': 'date'
                },
                {
                    'name': 'observacoes_acordo',
                    'label': 'Observações do Acordo',
                    'type': 'textarea'
                }
            ],
            'layout': {
                'sections': [
                    {
                        'title': 'Acordo',
                        'fields': ['tolerancia_acordo', 'acordo_realizado', 'data_acordo', 'observacoes_acordo']
                    }
                ]
            }
        },
        3: {  # Cível
            'natureza': 'Cível',
            'campos_obrigatorios': [],
            'campos_opcionais': [
                {
                    'name': 'tolerancia_acordo',
                    'label': 'Tolerância para Acordo',
                    'type': 'currency'
                },
                {
                    'name': 'acordo_realizado',
                    'label': 'Valor do Acordo Realizado',
                    'type': 'currency'
                },
                {
                    'name': 'data_acordo',
                    'label': 'Data do Acordo',
                    'type': 'date'
                },
                {
                    'name': 'observacoes_acordo',
                    'label': 'Observações do Acordo',
                    'type': 'textarea'
                }
            ],
            'layout': {
                'sections': [
                    {
                        'title': 'Acordo',
                        'fields': ['tolerancia_acordo', 'acordo_realizado', 'data_acordo', 'observacoes_acordo']
                    }
                ]
            }
        }
    }
    
    @staticmethod
    def obter_schema_por_natureza(natureza_id: int, versao: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Obtém schema dinâmico de formulário
        
        Args:
            natureza_id: ID da natureza
            versao: Versão específica (última se None)
            
        Returns:
            Schema JSON ou None
        """
        # Tentar buscar da DB
        query = ConfiguracaoFormulario.query.filter_by(
            natureza_id=natureza_id,
            ativo=True
        )
        
        if versao:
            query = query.filter_by(versao=versao)
        
        config = query.order_by(ConfiguracaoFormulario.versao.desc()).first()
        
        if config:
            return {
                'natureza_id': natureza_id,
                'versao': config.versao,
                'campos_obrigatorios': config.campos_obrigatorios,
                'campos_opcionais': config.campos_opcionais,
                'validacoes': config.validacoes,
                'layout': config.layout
            }
        
        # Fallback para schema padrão
        return FormularioDinamicoService.SCHEMAS_PADRAO.get(natureza_id)
    
    @staticmethod
    def validar_dados_contra_schema(
        natureza_id: int,
        dados: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Valida dados contra schema dinâmico
        
        Args:
            natureza_id: ID da natureza
            dados: Dados a validar
            
        Returns:
            (válido: bool, erros: List[str])
        """
        schema = FormularioDinamicoService.obter_schema_por_natureza(natureza_id)
        
        if not schema:
            return False, [f"Schema não encontrado para natureza {natureza_id}"]
        
        erros = []
        
        # Validar campos obrigatórios
        for campo in schema.get('campos_obrigatorios', []):
            nome_campo = campo['name']
            if nome_campo not in dados or dados[nome_campo] is None:
                erros.append(f"Campo obrigatório ausente: {campo['label']}")
        
        # Validar tipos e regras
        validacoes = schema.get('validacoes', {})
        for campo_nome, regras in validacoes.items():
            if campo_nome in dados:
                valor = dados[campo_nome]
                
                # Validar min
                if 'min' in regras and valor < regras['min']:
                    erros.append(f"{campo_nome}: valor mínimo é {regras['min']}")
                
                # Validar max
                if 'max' in regras and valor > regras['max']:
                    erros.append(f"{campo_nome}: valor máximo é {regras['max']}")
                
                # Validar pattern (regex)
                if 'pattern' in regras:
                    import re
                    if not re.match(regras['pattern'], str(valor)):
                        erros.append(f"{campo_nome}: formato inválido")
        
        return len(erros) == 0, erros
    
    @staticmethod
    def criar_schema_personalizado(
        tenant_id: int,
        natureza_id: int,
        campos_obrigatorios: List[Dict],
        campos_opcionais: List[Dict],
        validacoes: Dict,
        layout: Dict
    ) -> ConfiguracaoFormulario:
        """
        Cria schema personalizado para um tenant
        
        Args:
            tenant_id: ID do tenant
            natureza_id: ID da natureza
            campos_obrigatorios: Lista de campos obrigatórios
            campos_opcionais: Lista de campos opcionais
            validacoes: Regras de validação
            layout: Layout do form
            
        Returns:
            ConfiguracaoFormulario criada
        """
        from main import db
        
        # Determinar próxima versão
        ultima_versao = db.session.query(
            db.func.max(ConfiguracaoFormulario.versao)
        ).filter_by(
            tenant_id=tenant_id,
            natureza_id=natureza_id
        ).scalar() or 0
        
        nova_versao = ultima_versao + 1
        
        config = ConfiguracaoFormulario(
            tenant_id=tenant_id,
            natureza_id=natureza_id,
            campos_obrigatorios=campos_obrigatorios,
            campos_opcionais=campos_opcionais,
            validacoes=validacoes,
            layout=layout,
            versao=nova_versao,
            ativo=True
        )
        
        db.session.add(config)
        db.session.commit()
        
        return config
