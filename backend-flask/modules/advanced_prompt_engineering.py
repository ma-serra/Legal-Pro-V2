"""
Sistema de Prompt Engineering Avançado para Agentes Jurídicos
Implementa Chain-of-Thought especializado e Few-Shot Learning
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)

@dataclass
class LegalExample:
    """Exemplo para Few-Shot Learning jurídico"""
    input_query: str
    expected_output: str
    legal_area: str
    complexity: str
    reasoning_steps: List[str]

@dataclass 
class PromptTemplate:
    """Template de prompt com estrutura otimizada"""
    template_id: str
    name: str
    legal_area: str
    chain_of_thought: str
    few_shot_examples: List[LegalExample]
    system_prompt: str
    user_prompt_template: str
    parameters: Dict[str, Any]

class AdvancedPromptEngineering:
    """
    Sistema avançado de engenharia de prompts para análise jurídica
    Implementa Chain-of-Thought e Few-Shot Learning otimizados
    """
    
    def __init__(self):
        self.legal_areas = [
            "direito_penal", "direito_civil", "direito_tributario", 
            "direito_trabalhista", "direito_constitucional",
            "direito_administrativo", "direito_empresarial"
        ]
        
        # Template base Chain-of-Thought para análise jurídica
        self.base_chain_of_thought = """
Como especialista jurídico, analise esta questão seguindo esta estrutura rigorosa:

1. **IDENTIFICAÇÃO JURÍDICA**:
   - Qual ramo do direito está envolvido?
   - Quais institutos jurídicos são aplicáveis?
   - Há questões de competência ou procedimento?

2. **ANÁLISE NORMATIVA**:
   - Quais normas constitucionais são relevantes?
   - Qual legislação infraconstitucional se aplica?
   - Há regulamentações específicas aplicáveis?

3. **FUNDAMENTAÇÃO DOUTRINÁRIA**:
   - Qual o entendimento doutrinário consolidado?
   - Há correntes divergentes relevantes?
   - Quais autores são referência no tema?

4. **PESQUISA JURISPRUDENCIAL**:
   - Há súmulas ou precedentes vinculantes?
   - Como os tribunais superiores decidem casos similares?
   - Existem julgados recentes relevantes?

5. **APLICAÇÃO AO CASO CONCRETO**:
   - Como as normas se aplicam à situação específica?
   - Quais são os requisitos a serem observados?
   - Há particularidades que devem ser consideradas?

6. **CONCLUSÃO FUNDAMENTADA**:
   - Resposta clara e objetiva à consulta
   - Fundamentação jurídica completa
   - Eventuais ressalvas ou recomendações

Contexto Vetorial: {context}
Consulta: {query}
"""
        
        # Carregar templates especializados
        self._initialize_specialized_templates()
        
        # Carregar exemplos Few-Shot
        self._initialize_few_shot_examples()
    
    def _initialize_specialized_templates(self):
        """Inicializa templates especializados por área jurídica"""
        self.specialized_templates = {
            "direito_penal": PromptTemplate(
                template_id="penal_chain",
                name="Análise Criminal Chain-of-Thought",
                legal_area="direito_penal",
                chain_of_thought="""
Análise criminal especializada:

1. **TIPIFICAÇÃO PENAL**:
   - Qual o tipo penal aplicável?
   - Há elementares e circunstâncias específicas?
   - Verifica-se adequação típica?

2. **ANÁLISE DE ANTIJURIDICIDADE**:
   - Há excludentes de ilicitude?
   - Verifica-se legítima defesa ou estado de necessidade?

3. **CULPABILIDADE**:
   - Há imputabilidade do agente?
   - Existe consciência da ilicitude?
   - Há exigibilidade de conduta diversa?

4. **DOSIMETRIA PENAL**:
   - Análise das circunstâncias judiciais (art. 59, CP)
   - Agravantes e atenuantes aplicáveis
   - Causas de aumento/diminuição de pena

5. **ASPECTOS PROCESSUAIS**:
   - Competência jurisdicional
   - Ação penal cabível (pública/privada)
   - Prazos prescricionais

6. **CONCLUSÃO TÉCNICA**:
   - Resposta fundamentada com previsão legal
   - Citação de artigos do CP/CPP
   - Jurisprudência consolidada
""",
                few_shot_examples=[],
                system_prompt="Você é um especialista em Direito Penal com vasta experiência em análise de tipos penais e dosimetria.",
                user_prompt_template="Analise a seguinte questão criminal: {query}\nContexto: {context}",
                parameters={"temperature": 0.1, "max_tokens": 2000}
            ),
            
            "direito_civil": PromptTemplate(
                template_id="civil_chain",
                name="Análise Civilística Chain-of-Thought", 
                legal_area="direito_civil",
                chain_of_thought="""
Análise civilística especializada:

1. **RELAÇÃO JURÍDICA**:
   - Identificar sujeitos da relação jurídica
   - Objeto da relação (prestação/bem jurídico)
   - Fato jurídico gerador

2. **CAPACIDADE E LEGITIMIDADE**:
   - Análise da capacidade das partes
   - Legitimidade para o ato jurídico
   - Representação ou assistência necessária

3. **REQUISITOS DE VALIDADE**:
   - Agente capaz
   - Objeto lícito, possível e determinável
   - Forma prescrita ou não defesa em lei

4. **EFEITOS JURÍDICOS**:
   - Direitos e obrigações gerados
   - Eficácia temporal e espacial
   - Consequências do inadimplemento

5. **RESPONSABILIDADE CIVIL**:
   - Ato ilícito e dano
   - Nexo de causalidade
   - Excludentes de responsabilidade

6. **SOLUÇÃO JURÍDICA**:
   - Aplicação do Código Civil
   - Precedentes dos tribunais superiores
   - Medidas judiciais cabíveis
""",
                few_shot_examples=[],
                system_prompt="Você é um civilista experiente, especializado em obrigações, contratos e responsabilidade civil.",
                user_prompt_template="Analise a questão civil: {query}\nContexto jurídico: {context}",
                parameters={"temperature": 0.15, "max_tokens": 2500}
            ),
            
            "direito_tributario": PromptTemplate(
                template_id="tributario_chain",
                name="Análise Tributária Chain-of-Thought",
                legal_area="direito_tributario", 
                chain_of_thought="""
Análise tributária especializada:

1. **COMPETÊNCIA TRIBUTÁRIA**:
   - Identificar ente competente (União, Estado, Município)
   - Fundamento constitucional da competência
   - Limites constitucionais ao poder de tributar

2. **HIPÓTESE DE INCIDÊNCIA**:
   - Fato gerador do tributo
   - Aspectos material, temporal, espacial, quantitativo e pessoal
   - Classificação do tributo (imposto, taxa, contribuição)

3. **OBRIGAÇÃO TRIBUTÁRIA**:
   - Sujeito ativo e passivo
   - Base de cálculo e alíquota
   - Momento da ocorrência do fato gerador

4. **LANÇAMENTO TRIBUTÁRIO**:
   - Modalidade de lançamento aplicável
   - Decadência e prescrição
   - Procedimentos de cobrança

5. **DEFESAS TRIBUTÁRIAS**:
   - Imunidades constitucionais aplicáveis
   - Isenções legais pertinentes
   - Não incidência por ausência dos requisitos

6. **ORIENTAÇÃO PRÁTICA**:
   - Calculadora dos tributos devidos
   - Prazos para pagamento ou contestação
   - Jurisprudência do STJ e STF
""",
                few_shot_examples=[],
                system_prompt="Você é um tributarista experiente, especializado no Sistema Tributário Nacional e contencioso fiscal.",
                user_prompt_template="Analise a questão tributária: {query}\nContexto: {context}",
                parameters={"temperature": 0.1, "max_tokens": 2200}
            )
        }
    
    def _initialize_few_shot_examples(self):
        """Inicializa exemplos de Few-Shot Learning por área"""
        self.few_shot_examples = {
            "direito_penal": [
                LegalExample(
                    input_query="João subtraiu um celular avaliado em R$ 800,00 de uma loja. Qual o crime e a pena?",
                    expected_output="""**ANÁLISE CRIMINAL**:

1. **TIPIFICAÇÃO**: Art. 155, caput, CP - Furto simples
2. **ELEMENTARES**: 
   - Subtrair: retirar coisa de quem a detém
   - Coisa móvel: celular
   - Alheia: pertencente à loja
   - Para si: intenção de apropriação
3. **PENA**: Reclusão de 1 a 4 anos, e multa
4. **VALOR**: R$ 800,00 não configura furto qualificado pelo valor
5. **JURISPRUDÊNCIA**: STJ entende aplicável o princípio da insignificância quando o valor for ínfimo

**CONCLUSÃO**: Crime de furto simples, pena de 1 a 4 anos de reclusão.""",
                    legal_area="direito_penal",
                    complexity="basic",
                    reasoning_steps=["Identificação do tipo", "Análise das elementares", "Fixação da pena", "Consideração de jurisprudência"]
                ),
                
                LegalExample(
                    input_query="Empresa deixou de recolher ICMS no valor de R$ 50.000,00. Há crime?",
                    expected_output="""**ANÁLISE DE CRIME TRIBUTÁRIO**:

1. **TIPIFICAÇÃO**: Possível art. 2°, I, Lei 8.137/90
2. **REQUISITOS**:
   - Sonegação de tributo devido
   - Valor superior ao mínimo legal
   - Dolo específico de não pagar
3. **VALOR MÍNIMO**: R$ 20.000,00 (art. 1°, I, Lei 8.137/90)
4. **PENA**: Reclusão de 2 a 5 anos e multa
5. **EXTINÇÃO**: Pagamento antes do recebimento da denúncia extingue punibilidade

**CONCLUSÃO**: Há crime tributário. Recomenda-se pagamento imediato para extinção da punibilidade.""",
                    legal_area="direito_penal",
                    complexity="complex",
                    reasoning_steps=["Verificação de tipo específico", "Análise de valor mínimo", "Condições de extinção"]
                )
            ],
            
            "direito_civil": [
                LegalExample(
                    input_query="Comprei um carro com defeito oculto. Posso devolver?",
                    expected_output="""**ANÁLISE DE VÍCIO OCULTO**:

1. **FUNDAMENTO**: Art. 441, CC - Vício redibitório
2. **REQUISITOS**:
   - Defeito oculto que diminua valor/utilidade
   - Anterior à tradição
   - Desconhecido do adquirente
3. **DIREITOS**: 
   - Redibir contrato (devolução) - art. 441
   - Abatimento proporcional - art. 442
4. **PRAZO**: 30 dias (bem móvel) após descoberto - art. 445
5. **BOA-FÉ**: Vendedor de boa-fé responde pelo preço; má-fé responde por perdas e danos

**CONCLUSÃO**: Direito à devolução dentro do prazo decadencial de 30 dias.""",
                    legal_area="direito_civil",
                    complexity="basic",
                    reasoning_steps=["Identificação do instituto", "Verificação de requisitos", "Prazos aplicáveis", "Consequências"]
                )
            ]
        }
    
    def get_specialized_prompt(self, legal_area: str, query: str, context: str) -> str:
        """
        Gera prompt especializado baseado na área jurídica
        """
        if legal_area in self.specialized_templates:
            template = self.specialized_templates[legal_area]
            
            # Construir prompt com Chain-of-Thought
            full_prompt = f"{template.system_prompt}\n\n"
            full_prompt += template.chain_of_thought + "\n\n"
            
            # Adicionar exemplos Few-Shot se disponível
            if legal_area in self.few_shot_examples:
                full_prompt += "**EXEMPLOS DE ANÁLISE**:\n\n"
                
                # Selecionar exemplos relevantes (máximo 2)
                examples = self.few_shot_examples[legal_area][:2]
                
                for i, example in enumerate(examples, 1):
                    full_prompt += f"Exemplo {i}:\n"
                    full_prompt += f"Consulta: {example.input_query}\n"
                    full_prompt += f"Análise: {example.expected_output}\n\n"
            
            # Aplicar template final
            final_prompt = full_prompt + template.user_prompt_template.format(
                query=query,
                context=context
            )
            
            return final_prompt
        
        else:
            # Usar template genérico
            return self.base_chain_of_thought.format(
                context=context,
                query=query
            )
    
    def enhance_query_with_legal_context(self, query: str, legal_area: str) -> str:
        """
        Enriquece a consulta com contexto jurídico específico
        """
        # Identificar elementos jurídicos na consulta
        legal_elements = self._extract_legal_elements(query)
        
        enhanced_query = f"**ÁREA JURÍDICA**: {legal_area.replace('_', ' ').title()}\n\n"
        enhanced_query += f"**CONSULTA ORIGINAL**: {query}\n\n"
        
        if legal_elements:
            enhanced_query += "**ELEMENTOS JURÍDICOS IDENTIFICADOS**:\n"
            for element in legal_elements:
                enhanced_query += f"- {element}\n"
            enhanced_query += "\n"
        
        # Adicionar direcionamento específico
        area_guidance = {
            "direito_penal": "Analise sob aspectos de tipicidade, antijuridicidade, culpabilidade e punibilidade.",
            "direito_civil": "Considere relações jurídicas, capacidade, validade e eficácia dos atos.",
            "direito_tributario": "Examine competência, fato gerador, obrigação tributária e defesas aplicáveis.",
            "direito_trabalhista": "Avalie relação empregatícia, direitos trabalhistas e aspectos processuais.",
            "direito_constitucional": "Analise sob ótica dos princípios constitucionais e hierarquia normativa.",
            "direito_administrativo": "Considere princípios administrativos, competência e processo administrativo."
        }
        
        if legal_area in area_guidance:
            enhanced_query += f"**DIRECIONAMENTO TÉCNICO**: {area_guidance[legal_area]}\n\n"
        
        enhanced_query += "**ANÁLISE SOLICITADA**: Forneça resposta técnica fundamentada com citações legais e jurisprudenciais."
        
        return enhanced_query
    
    def _extract_legal_elements(self, query: str) -> List[str]:
        """
        Extrai elementos jurídicos específicos da consulta
        """
        elements = []
        
        # Padrões para identificar elementos jurídicos
        patterns = {
            "artigos_lei": r"art\.?\s*\d+|artigo\s+\d+",
            "numeros_processo": r"\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}|\d+\.\d+\.\d+\.\d+\.\d+",
            "valores_monetarios": r"R\$\s*[\d.,]+",
            "prazos": r"\d+\s*(dias?|meses?|anos?)",
            "tribunais": r"STF|STJ|TST|TSE|STM|TRF|TRT|TRE|TJSP|TJRJ|TJMG",
            "institutos_juridicos": r"(danos? morais?|lucros? cessantes?|responsabilidade civil|prisão preventiva)"
        }
        
        for element_type, pattern in patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                elements.append(f"{element_type.replace('_', ' ').title()}: {', '.join(matches)}")
        
        return elements
    
    def optimize_parameters_for_complexity(self, query: str, legal_area: str) -> Dict[str, Any]:
        """
        Otimiza parâmetros do modelo baseado na complexidade da consulta
        """
        # Analisar complexidade
        complexity_indicators = {
            "basic": ["o que é", "definir", "conceito", "significado"],
            "complex": ["analisar", "interpretar", "aplicar", "casos", "precedentes"],
            "critical": ["parecer", "recurso", "defesa", "ação judicial", "urgente"]
        }
        
        query_lower = query.lower()
        complexity = "basic"
        
        for level, indicators in complexity_indicators.items():
            for indicator in indicators:
                if indicator in query_lower:
                    complexity = level
        
        # Parâmetros otimizados por complexidade e área
        base_params = {
            "basic": {
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 20,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.1,
                "max_tokens": 1500
            },
            "complex": {
                "temperature": 0.3,
                "top_p": 0.85,
                "top_k": 30,
                "presence_penalty": 0.1,
                "frequency_penalty": 0.1,
                "max_tokens": 2500
            },
            "critical": {
                "temperature": 0.1,
                "top_p": 0.7,
                "top_k": 15,
                "presence_penalty": 0.2,
                "frequency_penalty": 0.2,
                "max_tokens": 3000
            }
        }
        
        params = base_params[complexity].copy()
        
        # Ajustes específicos por área jurídica
        area_adjustments = {
            "direito_penal": {"temperature": params["temperature"] - 0.1},  # Mais preciso
            "direito_tributario": {"temperature": params["temperature"] - 0.05},  # Técnico
            "direito_constitucional": {"max_tokens": params["max_tokens"] + 500}  # Mais extenso
        }
        
        if legal_area in area_adjustments:
            params.update(area_adjustments[legal_area])
        
        # Garantir limites mínimos e máximos
        params["temperature"] = max(0.1, min(1.0, params["temperature"]))
        params["max_tokens"] = max(1000, min(4000, params["max_tokens"]))
        
        logger.info(f"📊 Parâmetros otimizados para {legal_area} - Complexidade: {complexity}")
        
        return params
    
    def get_prompt_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do sistema de prompts"""
        return {
            "available_areas": self.legal_areas,
            "specialized_templates": len(self.specialized_templates),
            "few_shot_examples": {area: len(examples) for area, examples in self.few_shot_examples.items()},
            "chain_of_thought_enabled": True,
            "last_updated": datetime.now().isoformat()
        }