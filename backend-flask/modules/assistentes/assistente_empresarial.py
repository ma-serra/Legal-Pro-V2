"""
Assistente Jurídico Especializado em Direito Empresarial
"""
from typing import Dict, List, Any
from .assistente_base import AssistenteBase

class AssistenteEmpresarial(AssistenteBase):
    """Assistente especializado em Direito Empresarial"""
    
    def __init__(self):
        super().__init__("empresarial")
        self.nome = "Assistente Empresarial"
        self.descricao = "Especialista em Direito Empresarial e Societário"
        self.areas_especializacao = [
            "Constituição de Empresas",
            "Contratos Empresariais",
            "Direito Societário",
            "Compliance Corporativo",
            "Fusões e Aquisições",
            "Propriedade Intelectual"
        ]
    
    def processar_consulta_completa(self, pergunta: str, api_escolhida: str = "openai", 
                                  estilo: str = "juridico_tecnico", 
                                  usar_base_vetorial: bool = True):
        """Processa consulta completa usando assistente base"""
        try:
            return super().processar_consulta_completa(pergunta, api_escolhida, estilo, usar_base_vetorial)
        except Exception as e:
            return {
                'resposta': f"Erro ao processar consulta: {str(e)}",
                'contexto_usado': False,
                'resultados_busca': [],
                'api_utilizada': api_escolhida,
                'status': 'erro'
            }
    
    def obter_templates_area(self) -> List[Dict]:
        return [
            {
                'id': 'contrato_social',
                'nome': 'Contrato Social',
                'categoria': 'Constituição',
                'descricao': 'Contrato para constituição de sociedade limitada',
                'campos': ['socios', 'capital_social', 'objeto_social', 'administracao', 'sede']
            },
            {
                'id': 'acordo_acionistas',
                'nome': 'Acordo de Acionistas',
                'categoria': 'Societário',
                'descricao': 'Acordo entre acionistas de sociedade anônima',
                'campos': ['acionistas', 'participacoes', 'governanca', 'transferencia_acoes']
            }
        ]
    
    def obter_prompts_especializados(self) -> Dict[str, str]:
        return {
            'analise_contrato': "Analise o contrato empresarial sob aspectos de compliance e riscos jurídicos...",
            'due_diligence': "Realize due diligence jurídica focando em aspectos societários e contratuais...",
            'estrutura_societaria': "Avalie a estrutura societária proposta considerando eficiência fiscal..."
        }
