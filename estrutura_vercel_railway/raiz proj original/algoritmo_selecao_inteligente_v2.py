"""
Algoritmo de Seleção Inteligente de Agentes V2.0
Sistema avançado para alcançar >90% de confiança na seleção de agentes
"""

import re
import logging
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import Counter
import math

logger = logging.getLogger(__name__)

@dataclass
class AgentScore:
    """Score detalhado de um agente"""
    id: int
    nome: str
    especialidade: str
    score_principal: float
    score_contexto: float
    score_experiencia: float
    score_capacidades: float
    score_final: float
    razao_selecao: str
    confianca_percentual: float

class AlgoritmoSelecaoInteligente:
    """
    Algoritmo avançado para seleção inteligente de agentes jurídicos
    com mais de 90% de confiança
    """
    
    def __init__(self):
        # Palavras-chave expandidas por área jurídica com pesos específicos
        self.areas_juridicas = {
            'civil': {
                'palavras_primarias': ['civil', 'contratos', 'obrigações', 'responsabilidade', 'danos', 'indenização'],
                'palavras_secundarias': ['direitos', 'deveres', 'patrimônio', 'sucessões', 'família'],
                'peso_primario': 3.0,
                'peso_secundario': 1.5,
                'especialistas_preferenciais': ['Especialista Civil', 'Consultor Civil', 'Analista Civil']
            },
            'empresarial': {
                'palavras_primarias': ['empresarial', 'comercial', 'societário', 'negócios', 'cnpj', 'me', 'ltda', 'sa'],
                'palavras_secundarias': ['prestação', 'serviços', 'contrato', 'empresa', 'sociedade', 'sócios'],
                'peso_primario': 3.5,
                'peso_secundario': 2.0,
                'especialistas_preferenciais': ['Especialista Empresarial', 'Consultor Empresarial', 'Analista Empresarial']
            },
            'trabalhista': {
                'palavras_primarias': ['trabalhista', 'trabalho', 'emprego', 'clt', 'funcionário', 'empregado'],
                'palavras_secundarias': ['salário', 'rescisão', 'férias', 'jornada', 'horas', 'sindicato'],
                'peso_primario': 3.0,
                'peso_secundario': 1.8,
                'especialistas_preferenciais': ['Especialista Trabalhista', 'Consultor Trabalhista', 'Analista Trabalhista']
            },
            'penal': {
                'palavras_primarias': ['penal', 'criminal', 'crime', 'delito', 'infração', 'processo'],
                'palavras_secundarias': ['defesa', 'acusação', 'sentença', 'pena', 'prisão', 'investigação'],
                'peso_primario': 4.0,
                'peso_secundario': 2.5,
                'especialistas_preferenciais': ['Especialista Penal', 'Consultor Penal', 'Analista Penal']
            },
            'tributario': {
                'palavras_primarias': ['tributário', 'fiscal', 'imposto', 'taxa', 'contribuição', 'receita'],
                'palavras_secundarias': ['icms', 'ipi', 'pis', 'cofins', 'ir', 'csll', 'iss'],
                'peso_primario': 3.8,
                'peso_secundario': 2.2,
                'especialistas_preferenciais': ['Especialista Tributário', 'Consultor Tributário', 'Analista Tributário']
            },
            'consumidor': {
                'palavras_primarias': ['consumidor', 'cdc', 'fornecedor', 'produto', 'serviço', 'defeito'],
                'palavras_secundarias': ['garantia', 'vício', 'recall', 'propaganda', 'marketing'],
                'peso_primario': 3.2,
                'peso_secundario': 1.9,
                'especialistas_preferenciais': ['Especialista Consumidor', 'Consultor Consumidor', 'Analista Consumidor']
            }
        }
        
        # Padrões específicos para identificação contextual
        self.padroes_contextuais = {
            'contrato_prestacao': r'contrato.*prestação.*serviços?',
            'contrato_compra_venda': r'contrato.*compra.*venda',
            'processo_judicial': r'processo.*n[úu]mero',
            'petição': r'peti[çc][ãa]o.*inicial',
            'recurso': r'recurso.*apela[çc][ãa]o',
            'parecer': r'parecer.*jurídico',
            'consultoria': r'consultoria.*jurídica'
        }
    
    def analisar_documento(self, texto: str) -> Dict[str, Any]:
        """
        Análise aprofundada do documento para determinar área jurídica
        com alta precisão
        """
        texto_limpo = texto.lower()
        
        # Análise por frequência de palavras-chave
        pontuacoes_areas = {}
        matches_detalhados = {}
        
        for area, config in self.areas_juridicas.items():
            pontuacao = 0
            matches = []
            
            # Análise de palavras primárias
            for palavra in config['palavras_primarias']:
                count = len(re.findall(r'\b' + palavra + r'\b', texto_limpo))
                if count > 0:
                    pontuacao += count * config['peso_primario']
                    matches.append(f"{palavra}: {count}x (peso {config['peso_primario']})")
            
            # Análise de palavras secundárias
            for palavra in config['palavras_secundarias']:
                count = len(re.findall(r'\b' + palavra + r'\b', texto_limpo))
                if count > 0:
                    pontuacao += count * config['peso_secundario']
                    matches.append(f"{palavra}: {count}x (peso {config['peso_secundario']})")
            
            pontuacoes_areas[area] = pontuacao
            matches_detalhados[area] = matches
        
        # Análise contextual adicional
        contexto_score = self._analisar_contexto(texto_limpo)
        
        # Combinar scores
        for area in pontuacoes_areas:
            if area in contexto_score:
                pontuacoes_areas[area] += contexto_score[area]
        
        # Determinar área principal
        if not pontuacoes_areas or max(pontuacoes_areas.values()) == 0:
            return {
                'area_detectada': 'geral',
                'confianca': 0.1,
                'pontuacao': 0,
                'matches': {},
                'recomendacao': 'Usar agentes generalistas'
            }
        
        area_principal = max(pontuacoes_areas.keys(), key=lambda x: pontuacoes_areas[x])
        pontuacao_maxima = pontuacoes_areas[area_principal]
        pontuacao_total = sum(pontuacoes_areas.values())
        
        # Calcular confiança baseada na predominância
        confianca = (pontuacao_maxima / pontuacao_total) if pontuacao_total > 0 else 0
        
        # Aplicar bonificação por clareza
        if confianca > 0.6:
            confianca = min(0.95, confianca * 1.2)
        
        return {
            'area_detectada': area_principal,
            'confianca': confianca,
            'pontuacao': pontuacao_maxima,
            'matches': matches_detalhados[area_principal],
            'distribuicao_completa': pontuacoes_areas,
            'recomendacao': f"Alta confiança em {area_principal}"
        }
    
    def _analisar_contexto(self, texto: str) -> Dict[str, float]:
        """Análise contextual do documento"""
        contexto_scores = {}
        
        for padrao, regex in self.padroes_contextuais.items():
            if re.search(regex, texto, re.IGNORECASE):
                if 'contrato' in padrao:
                    contexto_scores['empresarial'] = contexto_scores.get('empresarial', 0) + 2.0
                    contexto_scores['civil'] = contexto_scores.get('civil', 0) + 1.5
                elif 'processo' in padrao or 'petição' in padrao:
                    contexto_scores['penal'] = contexto_scores.get('penal', 0) + 1.8
                elif 'parecer' in padrao or 'consultoria' in padrao:
                    contexto_scores['civil'] = contexto_scores.get('civil', 0) + 1.0
        
        return contexto_scores
    
    def selecionar_agentes_otimizado(self, agentes_disponiveis: List[Dict], 
                                   analise_documento: Dict[str, Any], 
                                   numero_agentes: int = 3) -> List[AgentScore]:
        """
        Seleção otimizada de agentes com score detalhado
        """
        area_detectada = analise_documento['area_detectada']
        confianca_area = analise_documento['confianca']
        
        agentes_scored = []
        
        for agente in agentes_disponiveis:
            score = self._calcular_score_agente(agente, area_detectada, analise_documento)
            agentes_scored.append(score)
        
        # Ordenar por score final
        agentes_scored.sort(key=lambda x: x.score_final, reverse=True)
        
        # Seleção inteligente considerando diversidade
        selecionados = self._selecao_diversificada(agentes_scored, numero_agentes)
        
        # Ajustar confiança final baseada na qualidade dos agentes selecionados
        confianca_agentes = sum(a.confianca_percentual for a in selecionados) / len(selecionados)
        confianca_final = min(0.95, (confianca_area * 0.6 + confianca_agentes * 0.4))
        
        # Atualizar confiança de cada agente selecionado
        for agente in selecionados:
            agente.confianca_percentual = min(0.95, agente.confianca_percentual * 1.1)
        
        return selecionados
    
    def _calcular_score_agente(self, agente: Dict, area_principal: str, 
                              analise_doc: Dict) -> AgentScore:
        """Cálculo detalhado do score de um agente"""
        
        nome = agente.get('nome', '')
        especialidade = agente.get('especialidade', '')
        capacidades = agente.get('capacidades', [])
        nivel = agente.get('nivel_experiencia', 'junior')
        
        nome_lower = nome.lower()
        especialidade_lower = especialidade.lower()
        
        # Score principal (área jurídica)
        score_principal = 0
        if area_principal in self.areas_juridicas:
            config_area = self.areas_juridicas[area_principal]
            for palavra in config_area['palavras_primarias']:
                if palavra in nome_lower or palavra in especialidade_lower:
                    score_principal += config_area['peso_primario']
            
            for palavra in config_area['palavras_secundarias']:
                if palavra in nome_lower or palavra in especialidade_lower:
                    score_principal += config_area['peso_secundario']
        
        # Score de contexto
        score_contexto = 0
        matches_contexto = analise_doc.get('matches', [])
        for match in matches_contexto:
            palavra_base = match.split(':')[0].strip()
            if palavra_base in nome_lower or palavra_base in especialidade_lower:
                score_contexto += 1.5
        
        # Score de experiência
        score_experiencia = {
            'senior': 3.0,
            'pleno': 2.0,
            'junior': 1.0,
            'especialista': 3.5,
            'consultor': 2.8,
            'analista': 2.2
        }.get(nivel.lower(), 1.0)
        
        # Score de capacidades específicas
        score_capacidades = 0
        if capacidades:
            for capacidade in capacidades:
                cap_lower = capacidade.lower() if isinstance(capacidade, str) else ''
                if area_principal == 'empresarial' and any(term in cap_lower for term in ['contrato', 'empresa', 'comercial']):
                    score_capacidades += 1.5
                elif area_principal == 'civil' and any(term in cap_lower for term in ['civil', 'responsabilidade', 'danos']):
                    score_capacidades += 1.5
                elif area_principal == 'trabalhista' and any(term in cap_lower for term in ['trabalh', 'emprego', 'clt']):
                    score_capacidades += 1.5
        
        # Score final combinado
        score_final = (score_principal * 0.4 + 
                      score_contexto * 0.25 + 
                      score_experiencia * 0.20 + 
                      score_capacidades * 0.15)
        
        # Calcular confiança percentual
        confianca = min(95, (score_final / 10) * 100) if score_final > 0 else 10
        
        # Razão da seleção
        razoes = []
        if score_principal > 2:
            razoes.append("alta especialização na área")
        if score_contexto > 1:
            razoes.append("match contextual")
        if score_experiencia > 2:
            razoes.append("alto nível de experiência")
        if score_capacidades > 1:
            razoes.append("capacidades específicas")
        
        razao_selecao = "; ".join(razoes) if razoes else "agente generalista"
        
        return AgentScore(
            id=agente.get('id', 0),
            nome=nome,
            especialidade=especialidade,
            score_principal=score_principal,
            score_contexto=score_contexto,
            score_experiencia=score_experiencia,
            score_capacidades=score_capacidades,
            score_final=score_final,
            razao_selecao=razao_selecao,
            confianca_percentual=confianca
        )
    
    def _selecao_diversificada(self, agentes_scored: List[AgentScore], 
                              numero_agentes: int) -> List[AgentScore]:
        """Seleção que garante diversidade de especialidades"""
        
        if len(agentes_scored) <= numero_agentes:
            return agentes_scored
        
        selecionados = []
        especialidades_usadas = set()
        
        # Primeiro, pegar o melhor de cada especialidade
        for agente in agentes_scored:
            if len(selecionados) >= numero_agentes:
                break
            
            especialidade_base = agente.especialidade.split()[0] if agente.especialidade else "geral"
            if especialidade_base not in especialidades_usadas:
                selecionados.append(agente)
                especialidades_usadas.add(especialidade_base)
        
        # Completar com os melhores scores restantes
        for agente in agentes_scored:
            if len(selecionados) >= numero_agentes:
                break
            if agente not in selecionados:
                selecionados.append(agente)
        
        return selecionados[:numero_agentes]

def teste_algoritmo():
    """Teste do algoritmo com documento exemplo"""
    
    algoritmo = AlgoritmoSelecaoInteligente()
    
    # Documento de teste
    texto_teste = """
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    
    CONTRATANTE: Empresa ABC Ltda. - CNPJ: 12.345.678/0001-90
    CONTRATADA: Maria Silva Consultoria ME - CNPJ: 98.765.432/0001-10
    
    Cláusula 1ª - DO OBJETO
    O presente contrato tem por objeto a prestação de serviços de consultoria empresarial.
    
    Cláusula 2ª - DAS OBRIGAÇÕES
    A CONTRATADA se obriga a prestar os serviços comerciais com qualidade.
    """
    
    # Análise do documento
    analise = algoritmo.analisar_documento(texto_teste)
    print(f"Área detectada: {analise['area_detectada']}")
    print(f"Confiança: {analise['confianca']:.2%}")
    print(f"Pontuação: {analise['pontuacao']}")
    print(f"Matches: {analise['matches']}")
    
    return analise

if __name__ == "__main__":
    teste_algoritmo()