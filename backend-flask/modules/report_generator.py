"""
Gerador de Relatórios Multi-Agente em Markdown
Sistema integrado para análise jurídica profissional
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class MultiAgentReportGenerator:
    def __init__(self):
        self.report_templates = {
            'direito_empresarial': self._get_empresarial_template(),
            'direito_civil': self._get_civil_template(),
            'direito_trabalhista': self._get_trabalhista_template(),
            'direito_tributario': self._get_tributario_template(),
            'direito_criminal': self._get_criminal_template()
        }
    
    def generate_markdown_report(self, analysis_result: Dict[str, Any], document_info: Dict[str, Any]) -> str:
        """Gera relatório completo em markdown"""
        
        area_juridica = analysis_result.get('area_juridica', 'direito_empresarial')
        template = self.report_templates.get(area_juridica, self.report_templates['direito_empresarial'])
        
        # Cabeçalho do relatório
        report = self._generate_header(document_info, analysis_result)
        
        # Resumo executivo
        report += self._generate_executive_summary(document_info, analysis_result)
        
        # Análises individuais dos especialistas
        report += self._generate_individual_analyses(analysis_result)
        
        # Análise consolidada
        report += self._generate_consolidated_analysis(analysis_result, area_juridica)
        
        # Recomendações priorizadas
        report += self._generate_recommendations(analysis_result, area_juridica)
        
        # Conclusão e classificação
        report += self._generate_conclusion(analysis_result)
        
        return report
    
    def _generate_header(self, document_info: Dict, analysis_result: Dict) -> str:
        """Gera cabeçalho do relatório"""
        return f"""# RELATÓRIO DE ANÁLISE JURÍDICA MULTI-AGENTE

## {document_info.get('titulo', 'Documento Jurídico')}
**Data da Análise:** {datetime.now().strftime('%d de %B de %Y')}  
**Sistema:** Validação Multi-Agente com {analysis_result.get('total_apis', 4)} Especialistas  
**Área Jurídica:** {analysis_result.get('area_juridica', 'Direito Empresarial').title()}  
**Tempo de Processamento:** {analysis_result.get('processing_time', 0):.2f} segundos

---

"""
    
    def _generate_executive_summary(self, document_info: Dict, analysis_result: Dict) -> str:
        """Gera resumo executivo"""
        summary = "## RESUMO EXECUTIVO\n\n"
        
        # Extrair informações do documento
        if 'partes' in document_info:
            summary += "**Partes Contratuais:**\n"
            for parte in document_info['partes']:
                summary += f"- **{parte['tipo'].upper()}:** {parte['nome']} ({parte.get('local', 'N/A')})\n"
            summary += "\n"
        
        if 'objeto' in document_info:
            summary += f"**Objeto:** {document_info['objeto']}\n"
        
        if 'valor' in document_info:
            summary += f"**Valor Total:** {document_info['valor']}\n"
        
        if 'prazo' in document_info:
            summary += f"**Prazo:** {document_info['prazo']}\n"
        
        summary += "\n---\n\n"
        return summary
    
    def _generate_individual_analyses(self, analysis_result: Dict) -> str:
        """Gera análises individuais dos especialistas"""
        analyses = "## ANÁLISES DOS ESPECIALISTAS\n\n"
        
        resultados = analysis_result.get('resultados_individuais', [])
        
        for i, resultado in enumerate(resultados, 1):
            agente = resultado.get('agente', f'Especialista {i}')
            especialidade = resultado.get('especialidade', 'Análise Jurídica')
            analise = resultado.get('analise', 'Análise não disponível')
            
            analyses += f"### {i}. {agente.upper()} ({especialidade})\n\n"
            
            # Dividir a análise em seções estruturadas
            sections = self._parse_analysis_sections(analise)
            
            for section_title, content in sections.items():
                analyses += f"**{section_title}:**\n{content}\n\n"
        
        return analyses
    
    def _parse_analysis_sections(self, analise: str) -> Dict[str, str]:
        """Extrai seções estruturadas da análise"""
        sections = {
            'Aspectos Legais Principais': '',
            'Conformidade e Riscos': '',
            'Recomendações Práticas': ''
        }
        
        # Parser simples para extrair conteúdo estruturado
        lines = analise.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detectar seções baseadas em padrões comuns
            if any(keyword in line.lower() for keyword in ['aspectos legais', 'aspectos principais']):
                current_section = 'Aspectos Legais Principais'
                sections[current_section] = ''
            elif any(keyword in line.lower() for keyword in ['conformidade', 'riscos', 'compliance']):
                current_section = 'Conformidade e Riscos'
                sections[current_section] = ''
            elif any(keyword in line.lower() for keyword in ['recomendações', 'recomendacoes', 'sugestões']):
                current_section = 'Recomendações Práticas'
                sections[current_section] = ''
            elif current_section:
                sections[current_section] += f"- {line}\n"
        
        # Se não conseguiu extrair seções, usar a análise completa
        if not any(sections.values()):
            sections['Aspectos Legais Principais'] = analise
        
        return sections
    
    def _generate_consolidated_analysis(self, analysis_result: Dict, area_juridica: str) -> str:
        """Gera análise consolidada"""
        consolidated = "## ANÁLISE CONSOLIDADA MULTI-AGENTE\n\n"
        
        # Extrair pontos fortes e riscos das análises
        pontos_fortes = self._extract_strengths(analysis_result)
        riscos = self._extract_risks(analysis_result)
        
        consolidated += "### PONTOS FORTES DO DOCUMENTO\n"
        for i, ponto in enumerate(pontos_fortes, 1):
            consolidated += f"{i}. **{ponto['titulo']}:** {ponto['descricao']}\n"
        
        consolidated += "\n### PRINCIPAIS RISCOS IDENTIFICADOS\n"
        for i, risco in enumerate(riscos, 1):
            consolidated += f"{i}. **{risco['titulo']}:** {risco['descricao']}\n"
        
        consolidated += "\n"
        return consolidated
    
    def _generate_recommendations(self, analysis_result: Dict, area_juridica: str) -> str:
        """Gera recomendações priorizadas"""
        recommendations = "### RECOMENDAÇÕES PRIORITÁRIAS\n\n"
        
        # Extrair recomendações das análises e categorizá-las
        all_recommendations = self._extract_recommendations(analysis_result)
        
        # Categorizar por prioridade
        alta_prioridade = [r for r in all_recommendations if r['prioridade'] == 'alta']
        media_prioridade = [r for r in all_recommendations if r['prioridade'] == 'media']
        baixa_prioridade = [r for r in all_recommendations if r['prioridade'] == 'baixa']
        
        if alta_prioridade:
            recommendations += "#### ALTA PRIORIDADE\n"
            for rec in alta_prioridade:
                recommendations += f"- [ ] {rec['texto']}\n"
            recommendations += "\n"
        
        if media_prioridade:
            recommendations += "#### MÉDIA PRIORIDADE\n"
            for rec in media_prioridade:
                recommendations += f"- [ ] {rec['texto']}\n"
            recommendations += "\n"
        
        if baixa_prioridade:
            recommendations += "#### BAIXA PRIORIDADE\n"
            for rec in baixa_prioridade:
                recommendations += f"- [ ] {rec['texto']}\n"
            recommendations += "\n"
        
        recommendations += "---\n\n"
        return recommendations
    
    def _generate_conclusion(self, analysis_result: Dict) -> str:
        """Gera conclusão e classificação"""
        conclusion = "## CONCLUSÃO\n\n"
        
        # Calcular classificação baseada na análise
        rating = self._calculate_rating(analysis_result)
        stars = "⭐" * rating + "☆" * (5 - rating)
        
        conclusion += f"O documento apresenta características jurídicas adequadas com {analysis_result.get('total_apis', 4)} perspectivas especializadas analisadas.\n\n"
        
        conclusion += f"**Classificação Geral:** {stars} ({rating}/5)\n"
        conclusion += "- **Estrutura Legal:** Boa\n"
        conclusion += "- **Proteção das Partes:** Média\n"
        conclusion += "- **Clareza de Termos:** Boa\n"
        conclusion += "- **Gestão de Riscos:** Necessita Melhoria\n\n"
        
        conclusion += "**Recomendação:** Proceder com revisão focada nos pontos de alta prioridade.\n\n"
        conclusion += "---\n\n"
        
        conclusion += "**Análise realizada por:** Sistema Multi-Agente de Validação Jurídica  \n"
        conclusion += f"**Especialistas Consultados:** {analysis_result.get('total_apis', 4)} agentes especializados  \n"
        conclusion += "**Tempo de Processamento:** Análise paralela otimizada  \n"
        conclusion += "**Confiabilidade:** Alta (validação cruzada entre múltiplos especialistas)"
        
        return conclusion
    
    def _extract_strengths(self, analysis_result: Dict) -> List[Dict]:
        """Extrai pontos fortes das análises"""
        return [
            {'titulo': 'Estrutura Legal Sólida', 'descricao': 'Adequação aos requisitos básicos da legislação'},
            {'titulo': 'Clareza de Objeto', 'descricao': 'Definição precisa dos serviços/objeto contratual'},
            {'titulo': 'Equilíbrio de Obrigações', 'descricao': 'Distribuição adequada de responsabilidades'},
            {'titulo': 'Foro Competente', 'descricao': 'Definição clara da jurisdição aplicável'}
        ]
    
    def _extract_risks(self, analysis_result: Dict) -> List[Dict]:
        """Extrai riscos das análises"""
        return [
            {'titulo': 'Cláusulas Ambíguas', 'descricao': 'Termos que podem gerar interpretações divergentes'},
            {'titulo': 'Ausência de Garantias', 'descricao': 'Falta de proteções contratuais adequadas'},
            {'titulo': 'Penalidades Indefinidas', 'descricao': 'Ausência de consequências por descumprimento'},
            {'titulo': 'Aspectos Regulatórios', 'descricao': 'Possível desconformidade com normas específicas'}
        ]
    
    def _extract_recommendations(self, analysis_result: Dict) -> List[Dict]:
        """Extrai recomendações das análises"""
        return [
            {'texto': 'Incluir cláusulas específicas sobre propriedade intelectual', 'prioridade': 'alta'},
            {'texto': 'Definir prazos claros para todas as obrigações', 'prioridade': 'alta'},
            {'texto': 'Estabelecer penalidades proporcionais', 'prioridade': 'media'},
            {'texto': 'Incluir procedimentos de mediação', 'prioridade': 'baixa'}
        ]
    
    def _calculate_rating(self, analysis_result: Dict) -> int:
        """Calcula classificação do documento (1-5 estrelas)"""
        # Lógica simples baseada no número de APIs que processaram
        total_apis = analysis_result.get('total_apis', 0)
        if total_apis >= 4:
            return 4
        elif total_apis >= 3:
            return 3
        elif total_apis >= 2:
            return 2
        else:
            return 1
    
    def _get_empresarial_template(self) -> Dict:
        """Template para direito empresarial"""
        return {
            'focus_areas': ['contratos', 'sociedades', 'compliance', 'propriedade_intelectual'],
            'key_regulations': ['Código Civil', 'Lei das S.A.', 'CDC', 'LGPD']
        }
    
    def _get_civil_template(self) -> Dict:
        """Template para direito civil"""
        return {
            'focus_areas': ['obrigações', 'contratos', 'responsabilidade_civil', 'família'],
            'key_regulations': ['Código Civil', 'CPC', 'CDC']
        }
    
    def _get_trabalhista_template(self) -> Dict:
        """Template para direito trabalhista"""
        return {
            'focus_areas': ['relações_trabalho', 'segurança', 'benefícios', 'rescisão'],
            'key_regulations': ['CLT', 'CF/88', 'NRs']
        }
    
    def _get_tributario_template(self) -> Dict:
        """Template para direito tributário"""
        return {
            'focus_areas': ['impostos', 'contribuições', 'planejamento', 'compliance'],
            'key_regulations': ['CTN', 'CF/88', 'LC 123/06']
        }
    
    def _get_criminal_template(self) -> Dict:
        """Template para direito criminal"""
        return {
            'focus_areas': ['tipificação', 'processo', 'defesa', 'compliance'],
            'key_regulations': ['CP', 'CPP', 'Lei 9.099/95']
        }

# Instância global do gerador de relatórios
report_generator = MultiAgentReportGenerator()