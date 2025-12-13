"""
Assistente Jurídico Especializado em Direito Digital
"""
from typing import Dict, List, Any
from .assistente_base import AssistenteBase

class AssistenteDigital(AssistenteBase):
    """Assistente especializado em Direito Digital"""
    
    def __init__(self):
        super().__init__("digital")
        self.nome = "Assistente Digital"
        self.descricao = "Especialista em Direito Digital, Proteção de Dados e Tecnologia"
        self.areas_especializacao = [
            "LGPD - Lei Geral de Proteção de Dados",
            "Marco Civil da Internet",
            "Crimes Cibernéticos",
            "Proteção de Dados Pessoais",
            "Contratos Digitais",
            "E-commerce e Marketplace",
            "Propriedade Intelectual Digital",
            "Compliance Digital",
            "Segurança da Informação",
            "Direito da Informática",
            "Certificação Digital",
            "Assinatura Eletrônica"
        ]
    
    def obter_templates_area(self) -> List[Dict]:
        """Retorna templates específicos para Direito Digital"""
        return [
            {
                'id': 'politica_privacidade',
                'nome': 'Política de Privacidade LGPD',
                'categoria': 'Compliance',
                'descricao': 'Política de privacidade em conformidade com a LGPD',
                'campos': ['empresa', 'dados_coletados', 'finalidades', 'base_legal', 'direitos_titular', 'dpo_contato']
            },
            {
                'id': 'termo_uso_digital',
                'nome': 'Termos de Uso Digital',
                'categoria': 'Contratos',
                'descricao': 'Termos de uso para plataformas digitais e aplicativos',
                'campos': ['plataforma', 'servicos_oferecidos', 'responsabilidades', 'limitacoes', 'propriedade_intelectual']
            },
            {
                'id': 'contrato_desenvolvimento',
                'nome': 'Contrato de Desenvolvimento de Software',
                'categoria': 'Contratos',
                'descricao': 'Contrato para desenvolvimento de sistemas e aplicações',
                'campos': ['desenvolvedor', 'cliente', 'especificacoes', 'prazo', 'valor', 'propriedade_codigo', 'manutencao']
            },
            {
                'id': 'notificacao_vazamento',
                'nome': 'Notificação de Vazamento de Dados',
                'categoria': 'Compliance',
                'descricao': 'Comunicação obrigatória à ANPD sobre incidentes de segurança',
                'campos': ['empresa', 'incidente_descricao', 'dados_afetados', 'medidas_tomadas', 'timeline', 'impacto']
            },
            {
                'id': 'acao_crimes_digitais',
                'nome': 'Ação por Crimes Digitais',
                'categoria': 'Litígio',
                'descricao': 'Petição inicial para crimes praticados no ambiente digital',
                'campos': ['vitima', 'criminoso', 'crime_tipificacao', 'evidencias', 'danos', 'pedidos']
            },
            {
                'id': 'contrato_cloud',
                'nome': 'Contrato de Serviços em Nuvem',
                'categoria': 'Contratos',
                'descricao': 'Contrato para prestação de serviços de computação em nuvem',
                'campos': ['provedor', 'cliente', 'servicos', 'sla', 'seguranca', 'localizacao_dados', 'backup']
            },
            {
                'id': 'cessao_direitos_digitais',
                'nome': 'Cessão de Direitos Digitais',
                'categoria': 'Propriedade Intelectual',
                'descricao': 'Contrato de cessão de direitos sobre conteúdo digital',
                'campos': ['cedente', 'cessionario', 'obra_digital', 'direitos_cedidos', 'territorio', 'prazo', 'remuneracao']
            },
            {
                'id': 'licenca_software',
                'nome': 'Licença de Uso de Software',
                'categoria': 'Propriedade Intelectual',
                'descricao': 'Contrato de licenciamento de software personalizado',
                'campos': ['licenciador', 'licenciado', 'software', 'tipo_licenca', 'restricoes', 'suporte', 'atualizacoes']
            },
            {
                'id': 'termo_consentimento',
                'nome': 'Termo de Consentimento LGPD',
                'categoria': 'Compliance',
                'descricao': 'Termo específico para coleta de consentimento',
                'campos': ['finalidade_especifica', 'dados_solicitados', 'prazo_tratamento', 'opcoes_consentimento', 'revogacao']
            },
            {
                'id': 'acordo_nda_tech',
                'nome': 'NDA para Projetos Tecnológicos',
                'categoria': 'Contratos',
                'descricao': 'Acordo de confidencialidade para desenvolvimento tecnológico',
                'campos': ['partes', 'informacoes_confidenciais', 'prazo_confidencialidade', 'excecoes', 'penalidades']
            }
        ]
    
    def processar_consulta_especializada(self, consulta: str, contexto: Dict) -> Dict:
        """Processa consultas específicas de Direito Digital"""
        
        # Palavras-chave específicas da área
        palavras_chave_lgpd = ['lgpd', 'proteção de dados', 'dados pessoais', 'consentimento', 'anpd']
        palavras_chave_crimes = ['crime digital', 'hacker', 'phishing', 'fraude online', 'invasão']
        palavras_chave_contratos = ['contrato digital', 'e-commerce', 'marketplace', 'plataforma']
        
        consulta_lower = consulta.lower()
        
        if any(palavra in consulta_lower for palavra in palavras_chave_lgpd):
            return self._processar_consulta_lgpd(consulta, contexto)
        elif any(palavra in consulta_lower for palavra in palavras_chave_crimes):
            return self._processar_consulta_crimes_digitais(consulta, contexto)
        elif any(palavra in consulta_lower for palavra in palavras_chave_contratos):
            return self._processar_consulta_contratos_digitais(consulta, contexto)
        else:
            return self._processar_consulta_geral_digital(consulta, contexto)
    
    def _processar_consulta_lgpd(self, consulta: str, contexto: Dict) -> Dict:
        """Processa consultas sobre LGPD"""
        return {
            'area_especializada': 'LGPD',
            'sugestoes_templates': ['politica_privacidade', 'notificacao_vazamento', 'termo_consentimento'],
            'legislacao_aplicavel': ['Lei 13.709/2018 (LGPD)', 'Decreto 10.474/2020'],
            'orgaos_competentes': ['ANPD - Autoridade Nacional de Proteção de Dados'],
            'prazo_resposta': '15 dias para resposta ao titular'
        }
    
    def _processar_consulta_crimes_digitais(self, consulta: str, contexto: Dict) -> Dict:
        """Processa consultas sobre crimes digitais"""
        return {
            'area_especializada': 'Crimes Cibernéticos',
            'sugestoes_templates': ['acao_crimes_digitais'],
            'legislacao_aplicavel': ['Lei 12.737/2012 (Lei Carolina Dieckmann)', 'Código Penal', 'Marco Civil da Internet'],
            'orgaos_competentes': ['Polícia Civil', 'Ministério Público', 'CERT.br'],
            'prazo_resposta': 'Imediato para preservação de evidências'
        }
    
    def _processar_consulta_contratos_digitais(self, consulta: str, contexto: Dict) -> Dict:
        """Processa consultas sobre contratos digitais"""
        return {
            'area_especializada': 'Contratos Digitais',
            'sugestoes_templates': ['contrato_desenvolvimento', 'termo_uso_digital', 'licenca_software'],
            'legislacao_aplicavel': ['Código Civil', 'Marco Civil da Internet', 'Lei de Software'],
            'consideracoes_especiais': ['Assinatura eletrônica', 'Validade jurídica', 'Jurisdição aplicável']
        }
    
    def _processar_consulta_geral_digital(self, consulta: str, contexto: Dict) -> Dict:
        """Processa consultas gerais de direito digital"""
        return {
            'area_especializada': 'Direito Digital Geral',
            'sugestoes_templates': ['contrato_cloud', 'cessao_direitos_digitais', 'acordo_nda_tech'],
            'legislacao_aplicavel': ['Marco Civil da Internet', 'LGPD', 'Código Civil'],
            'tendencias': ['IA e Direito', 'Blockchain', 'IoT', 'Criptomoedas']
        }
    
    def obter_checklist_compliance(self) -> List[Dict]:
        """Retorna checklist de compliance digital"""
        return [
            {
                'categoria': 'LGPD',
                'itens': [
                    'Mapeamento de dados pessoais',
                    'Base legal definida',
                    'Política de privacidade atualizada',
                    'Processo de consentimento',
                    'DPO designado',
                    'Relatório de impacto (quando aplicável)'
                ]
            },
            {
                'categoria': 'Segurança',
                'itens': [
                    'Criptografia implementada',
                    'Controle de acesso',
                    'Backup e recuperação',
                    'Monitoramento de segurança',
                    'Plano de resposta a incidentes'
                ]
            },
            {
                'categoria': 'Contratos',
                'itens': [
                    'Termos de uso atualizados',
                    'Política de privacidade',
                    'SLA definido',
                    'Responsabilidades claras',
                    'Resolução de disputas'
                ]
            }
        ]
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
