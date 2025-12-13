#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Inteligente de Seleção de Agentes Baseado em Capacidades
================================================================

Este módulo implementa um algoritmo avançado que:
1. Analisa todo o conteúdo do documento
2. Identifica a área jurídica mais relevante
3. Avalia TODAS as capacidades dos agentes da área
4. Seleciona agentes com maior pontuação de capacidades para análise especializada
"""

import re
import logging
from typing import List, Dict, Tuple, Any
from collections import defaultdict
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeletorAgentesCapacidades:
    """Sistema inteligente de seleção de agentes baseado em análise de capacidades"""
    
    def __init__(self):
        # Mapeamento expandido de palavras-chave por área jurídica
        self.palavras_chave_areas = {
            'civil': {
                'termos': ['contrato', 'compra', 'venda', 'locação', 'aluguel', 'propriedade', 'posse', 
                          'usucapião', 'danos morais', 'responsabilidade civil', 'obrigações', 'direitos reais',
                          'sucessões', 'família', 'casamento', 'divórcio', 'inventário', 'herança'],
                'peso': 1.0,
                'nome': 'Direito Civil'
            },
            'trabalhista': {
                'termos': ['empregado', 'empregador', 'salário', 'férias', 'rescisão', 'FGTS', 'CLT',
                          'jornada trabalho', 'horas extras', 'adicional', 'demissão', 'aviso prévio'],
                'peso': 1.2,
                'nome': 'Direito Trabalhista'
            },
            'empresarial': {
                'termos': ['sociedade', 'empresa', 'CNPJ', 'contrato social', 'quotas', 'ações',
                          'assembleia', 'diretoria', 'conselho', 'falência', 'recuperação judicial'],
                'peso': 1.1,
                'nome': 'Direito Empresarial'
            },
            'agrario': {
                'termos': ['rural', 'agrário', 'arrendamento', 'parceria', 'ITR', 'terra', 'agricultura',
                          'pecuária', 'reforma agrária', 'MST', 'INCRA', 'comodato rural', 'agronegócio'],
                'peso': 1.3,
                'nome': 'Direito Agrário'
            },
            'penal': {
                'termos': ['crime', 'delito', 'prisão', 'pena', 'sentença penal', 'réu', 'acusado',
                          'Código Penal', 'homicídio', 'furto', 'roubo', 'estelionato', 'denúncia'],
                'peso': 1.0,
                'nome': 'Direito Penal'
            },
            'tributario': {
                'termos': ['imposto', 'tributo', 'ICMS', 'IPI', 'IR', 'COFINS', 'PIS', 'ISS',
                          'Receita Federal', 'sonegação', 'elisão', 'evasão', 'planejamento tributário'],
                'peso': 1.1,
                'nome': 'Direito Tributário'
            },
            'administrativo': {
                'termos': ['administração pública', 'servidor público', 'licitação', 'contrato administrativo',
                          'concurso público', 'processo administrativo', 'mandado de segurança'],
                'peso': 1.0,
                'nome': 'Direito Administrativo'
            },
            'constitucional': {
                'termos': ['Constituição', 'constitucional', 'direitos fundamentais', 'habeas corpus',
                          'mandado injunção', 'ADI', 'ADPF', 'STF', 'inconstitucionalidade'],
                'peso': 1.0,
                'nome': 'Direito Constitucional'
            }
        }
        
        # Pesos para diferentes tipos de capacidades
        self.pesos_capacidades = {
            'analise': 2.0,
            'elaboracao': 1.8,
            'consultoria': 1.5,
            'assessoria': 1.3,
            'revisao': 1.2,
            'orientacao': 1.0,
            'suporte': 0.8
        }

    def analisar_documento_completo(self, texto_documento: str) -> Dict[str, Any]:
        """
        Analisa todo o documento para identificar área jurídica e extrair características
        
        Args:
            texto_documento: Texto completo do documento
            
        Returns:
            Dicionário com análise completa do documento
        """
        logger.info(f"📄 Iniciando análise completa: {len(texto_documento)} caracteres")
        
        # Normalizar texto
        texto_normalizado = texto_documento.lower()
        
        # Análise de densidade de palavras-chave por área
        analise_areas = {}
        for area, config in self.palavras_chave_areas.items():
            matches = []
            pontuacao_total = 0
            
            for termo in config['termos']:
                count = len(re.findall(r'\b' + re.escape(termo.lower()) + r'\b', texto_normalizado))
                if count > 0:
                    matches.append({
                        'termo': termo,
                        'occurrencias': count,
                        'pontuacao': count * config['peso']
                    })
                    pontuacao_total += count * config['peso']
            
            analise_areas[area] = {
                'nome': config['nome'],
                'pontuacao': pontuacao_total,
                'matches': matches,
                'densidade': pontuacao_total / len(texto_documento) * 1000,  # Densidade por 1000 chars
                'confianca': min(pontuacao_total / 20, 1.0)  # Normalizar confiança 0-1
            }
        
        # Identificar área principal
        area_principal = max(analise_areas.keys(), key=lambda x: analise_areas[x]['pontuacao'])
        
        # Análise de complexidade do documento
        complexidade = self._analisar_complexidade(texto_documento)
        
        # Análise de tipo de documento
        tipo_documento = self._identificar_tipo_documento(texto_documento)
        
        resultado = {
            'area_principal': area_principal,
            'area_nome': analise_areas[area_principal]['nome'],
            'confianca_area': analise_areas[area_principal]['confianca'],
            'analise_areas': analise_areas,
            'complexidade': complexidade,
            'tipo_documento': tipo_documento,
            'tamanho_documento': len(texto_documento),
            'necessidades_identificadas': self._identificar_necessidades(texto_documento, area_principal)
        }
        
        logger.info(f"🎯 Área identificada: {resultado['area_nome']} ({resultado['confianca_area']:.1%} confiança)")
        return resultado

    def _analisar_complexidade(self, texto: str) -> Dict[str, Any]:
        """Analisa a complexidade do documento"""
        
        # Indicadores de complexidade
        indicadores_alta = ['clausula', 'whereas', 'considerando', 'subcláusula', 'anexo', 'aditivo']
        indicadores_media = ['contrato', 'acordo', 'termo', 'compromisso', 'instrumento']
        indicadores_baixa = ['recibo', 'declaração', 'atestado', 'certidão']
        
        texto_lower = texto.lower()
        
        pontuacao_alta = sum(1 for ind in indicadores_alta if ind in texto_lower)
        pontuacao_media = sum(1 for ind in indicadores_media if ind in texto_lower)
        pontuacao_baixa = sum(1 for ind in indicadores_baixa if ind in texto_lower)
        
        # Análise de estrutura
        num_paragrafos = len([p for p in texto.split('\n') if p.strip()])
        num_palavras = len(texto.split())
        
        # Determinar nível de complexidade
        if pontuacao_alta >= 3 or num_palavras > 2000:
            nivel = 'alta'
        elif pontuacao_media >= 2 or num_palavras > 500:
            nivel = 'media'
        else:
            nivel = 'baixa'
        
        return {
            'nivel': nivel,
            'num_palavras': num_palavras,
            'num_paragrafos': num_paragrafos,
            'indicadores_complexidade': {
                'alta': pontuacao_alta,
                'media': pontuacao_media,
                'baixa': pontuacao_baixa
            }
        }

    def _identificar_tipo_documento(self, texto: str) -> str:
        """Identifica o tipo específico do documento"""
        
        tipos = {
            'contrato_compra_venda': ['compra', 'venda', 'comprador', 'vendedor'],
            'contrato_locacao': ['locação', 'aluguel', 'locador', 'locatário'],
            'contrato_trabalho': ['empregado', 'empregador', 'salário', 'função'],
            'procuracao': ['procuração', 'outorga', 'poderes', 'representação'],
            'petição': ['petição', 'excelentíssimo', 'requer', 'deferimento'],
            'parecer': ['parecer', 'opinião', 'análise', 'conclusão'],
            'contrato_sociedade': ['sociedade', 'sócios', 'capital social', 'quotas'],
            'testamento': ['testamento', 'legado', 'herdeiro', 'sucessão']
        }
        
        texto_lower = texto.lower()
        
        for tipo, palavras in tipos.items():
            if sum(1 for palavra in palavras if palavra in texto_lower) >= 2:
                return tipo
        
        return 'documento_generico'

    def _identificar_necessidades(self, texto: str, area: str) -> List[str]:
        """Identifica necessidades específicas do documento"""
        
        necessidades_por_area = {
            'civil': ['análise_contratos', 'validação_cláusulas', 'identificação_riscos'],
            'trabalhista': ['conformidade_clt', 'cálculos_trabalhistas', 'análise_rescisão'],
            'empresarial': ['estrutura_societária', 'governança', 'compliance'],
            'agrario': ['questões_fundiárias', 'contratos_rurais', 'legislação_ambiental'],
            'penal': ['tipificação_crimes', 'análise_provas', 'estratégia_defesa'],
            'tributario': ['planejamento_tributário', 'conformidade_fiscal', 'elisão_fiscal']
        }
        
        return necessidades_por_area.get(area, ['análise_geral', 'consultoria_jurídica'])

    def avaliar_capacidades_agentes(self, agentes: List[Dict], analise_documento: Dict) -> List[Dict]:
        """
        Avalia e pontua todos os agentes da área baseado em suas capacidades
        
        Args:
            agentes: Lista de agentes da área identificada
            analise_documento: Análise completa do documento
            
        Returns:
            Lista de agentes ordenados por pontuação de capacidades
        """
        logger.info(f"🧠 Avaliando capacidades de {len(agentes)} agentes")
        
        agentes_pontuados = []
        
        for agente in agentes:
            pontuacao = self._calcular_pontuacao_agente(agente, analise_documento)
            
            agente_avaliado = {
                **agente,
                'pontuacao_capacidades': pontuacao['total'],
                'detalhes_pontuacao': pontuacao,
                'adequacao_documento': self._calcular_adequacao(agente, analise_documento)
            }
            
            agentes_pontuados.append(agente_avaliado)
        
        # Ordenar por pontuação decrescente
        agentes_pontuados.sort(key=lambda x: x['pontuacao_capacidades'], reverse=True)
        
        # Log dos top 5 agentes
        logger.info("🏆 Top 5 agentes por capacidades:")
        for i, agente in enumerate(agentes_pontuados[:5], 1):
            logger.info(f"   {i}. {agente['nome']} - {agente['pontuacao_capacidades']:.2f} pontos")
        
        return agentes_pontuados

    def _calcular_pontuacao_agente(self, agente: Dict, analise_documento: Dict) -> Dict[str, Any]:
        """Calcula pontuação detalhada do agente baseado em capacidades"""
        
        pontuacao = {
            'capacidades_base': 0,
            'adequacao_area': 0,
            'complexidade_match': 0,
            'especialização': 0,
            'experiencia': 0,
            'total': 0
        }
        
        # 1. Pontuação base das capacidades
        capacidades = agente.get('capacidades', [])
        if isinstance(capacidades, str):
            try:
                capacidades = json.loads(capacidades)
            except:
                capacidades = []
        
        for capacidade in capacidades:
            # Analisar tipo de capacidade
            cap_lower = capacidade.lower()
            for tipo, peso in self.pesos_capacidades.items():
                if tipo in cap_lower:
                    pontuacao['capacidades_base'] += peso
                    break
            else:
                pontuacao['capacidades_base'] += 1.0  # Peso padrão
        
        # 2. Adequação à área identificada
        area_principal = analise_documento['area_principal']
        descricao = agente.get('descricao', '').lower()
        classe = agente.get('classe', '').lower()
        
        if area_principal in descricao or self.palavras_chave_areas[area_principal]['nome'].lower() in descricao:
            pontuacao['adequacao_area'] = 3.0
        elif any(termo in descricao for termo in self.palavras_chave_areas[area_principal]['termos'][:3]):
            pontuacao['adequacao_area'] = 2.0
        
        # 3. Match com complexidade do documento
        complexidade_doc = analise_documento['complexidade']['nivel']
        
        if 'especialista' in classe or 'especializado' in descricao:
            if complexidade_doc == 'alta':
                pontuacao['complexidade_match'] = 3.0
            elif complexidade_doc == 'media':
                pontuacao['complexidade_match'] = 2.5
        elif 'assistente' in classe:
            if complexidade_doc in ['media', 'baixa']:
                pontuacao['complexidade_match'] = 2.0
        
        # 4. Nível de especialização
        if 'principal' in agente.get('nome', '').lower():
            pontuacao['especialização'] = 2.0
        elif 'especialista' in agente.get('nome', '').lower():
            pontuacao['especialização'] = 1.5
        elif 'assistente' in agente.get('nome', '').lower():
            pontuacao['especialização'] = 1.0
        
        # 5. Pontuação por experiência (baseada em detalhes técnicos)
        detalhes = agente.get('detalhes_tecnicos', '')
        if detalhes and len(detalhes) > 200:
            pontuacao['experiencia'] = 1.0
        
        # Calcular total
        pontuacao['total'] = sum(pontuacao.values()) - pontuacao['total']  # Evitar duplicação
        
        return pontuacao

    def _calcular_adequacao(self, agente: Dict, analise_documento: Dict) -> float:
        """Calcula adequação geral do agente ao documento"""
        
        # Fatores de adequação
        fatores = []
        
        # 1. Match de área
        area_principal = analise_documento['area_principal']
        descricao = agente.get('descricao', '').lower()
        
        if self.palavras_chave_areas[area_principal]['nome'].lower() in descricao:
            fatores.append(0.9)
        elif any(termo in descricao for termo in self.palavras_chave_areas[area_principal]['termos'][:5]):
            fatores.append(0.7)
        else:
            fatores.append(0.3)
        
        # 2. Match de tipo de documento
        tipo_doc = analise_documento['tipo_documento']
        if tipo_doc != 'documento_generico':
            tipo_palavras = tipo_doc.replace('_', ' ').split()
            if any(palavra in descricao for palavra in tipo_palavras):
                fatores.append(0.8)
            else:
                fatores.append(0.5)
        else:
            fatores.append(0.6)
        
        # 3. Match de complexidade
        complexidade = analise_documento['complexidade']['nivel']
        classe = agente.get('classe', '').lower()
        
        if complexidade == 'alta' and 'especialista' in classe:
            fatores.append(0.9)
        elif complexidade == 'media' and ('assistente' in classe or 'especialista' in classe):
            fatores.append(0.8)
        elif complexidade == 'baixa':
            fatores.append(0.7)
        else:
            fatores.append(0.5)
        
        return sum(fatores) / len(fatores)

    def selecionar_melhores_agentes(self, agentes_avaliados: List[Dict], num_agentes: int = 3) -> List[Dict]:
        """
        Seleciona os melhores agentes baseado na avaliação de capacidades
        
        Args:
            agentes_avaliados: Lista de agentes já avaliados
            num_agentes: Número de agentes a selecionar
            
        Returns:
            Lista dos melhores agentes selecionados
        """
        
        # Garantir diversidade na seleção
        selecionados = []
        classes_selecionadas = set()
        
        for agente in agentes_avaliados:
            if len(selecionados) >= num_agentes:
                break
            
            classe = agente.get('classe', 'geral')
            
            # Priorizar diversidade de classes
            if classe not in classes_selecionadas or len(selecionados) < 2:
                selecionados.append(agente)
                classes_selecionadas.add(classe)
        
        logger.info(f"✅ Selecionados {len(selecionados)} agentes com maior pontuação de capacidades")
        
        return selecionados

    def gerar_relatorio_selecao(self, analise_documento: Dict, agentes_selecionados: List[Dict]) -> Dict[str, Any]:
        """Gera relatório detalhado da seleção de agentes"""
        
        relatorio = {
            'documento': {
                'area_identificada': analise_documento['area_nome'],
                'confianca': analise_documento['confianca_area'],
                'tipo': analise_documento['tipo_documento'],
                'complexidade': analise_documento['complexidade']['nivel'],
                'tamanho': analise_documento['tamanho_documento']
            },
            'agentes_selecionados': [],
            'criterios_selecao': {
                'base': 'Análise completa de capacidades',
                'fatores': ['Capacidades técnicas', 'Adequação à área', 'Match de complexidade', 
                           'Especialização', 'Experiência'],
                'algoritmo': 'Pontuação ponderada com garantia de diversidade'
            },
            'resumo': {
                'total_agentes_avaliados': len(agentes_selecionados),
                'area_confianca': f"{analise_documento['confianca_area']:.1%}",
                'pontuacao_media': 0
            }
        }
        
        pontuacoes = []
        for agente in agentes_selecionados:
            relatorio['agentes_selecionados'].append({
                'nome': agente['nome'],
                'classe': agente.get('classe', 'N/A'),
                'pontuacao_capacidades': agente['pontuacao_capacidades'],
                'adequacao_documento': agente['adequacao_documento'],
                'capacidades': agente.get('capacidades', [])
            })
            pontuacoes.append(agente['pontuacao_capacidades'])
        
        relatorio['resumo']['pontuacao_media'] = sum(pontuacoes) / len(pontuacoes) if pontuacoes else 0
        
        return relatorio


def processar_selecao_inteligente(texto_documento: str, agentes_disponiveis: List[Dict], 
                                num_agentes: int = 3) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Função principal para seleção inteligente de agentes baseada em capacidades
    
    Args:
        texto_documento: Texto completo do documento
        agentes_disponiveis: Lista de todos os agentes disponíveis
        num_agentes: Número de agentes a selecionar
        
    Returns:
        Tupla com (agentes_selecionados, relatorio_completo)
    """
    
    logger.info("🚀 Iniciando seleção inteligente de agentes baseada em capacidades")
    
    seletor = SeletorAgentesCapacidades()
    
    # 1. Análise completa do documento
    analise_documento = seletor.analisar_documento_completo(texto_documento)
    
    # 2. Filtrar agentes da área identificada
    area_identificada = analise_documento['area_principal']
    agentes_area = [
        agente for agente in agentes_disponiveis 
        if area_identificada in agente.get('descricao', '').lower() or
           analise_documento['area_nome'].lower() in agente.get('descricao', '').lower()
    ]
    
    logger.info(f"🎯 {len(agentes_area)} agentes encontrados para área {analise_documento['area_nome']}")
    
    # 3. Avaliar capacidades de todos os agentes da área
    agentes_avaliados = seletor.avaliar_capacidades_agentes(agentes_area, analise_documento)
    
    # 4. Selecionar os melhores baseado em capacidades
    agentes_selecionados = seletor.selecionar_melhores_agentes(agentes_avaliados, num_agentes)
    
    # 5. Gerar relatório completo
    relatorio = seletor.gerar_relatorio_selecao(analise_documento, agentes_selecionados)
    
    logger.info(f"✅ Seleção inteligente concluída: {len(agentes_selecionados)} agentes selecionados")
    
    return agentes_selecionados, relatorio


if __name__ == "__main__":
    # Teste do sistema
    texto_teste = """
    CONTRATO DE ARRENDAMENTO RURAL
    
    Arrendador: João Silva, proprietário rural
    Arrendatário: Maria Santos, produtora agrícola
    
    Objeto: Arrendamento de 100 hectares para cultivo de soja
    Prazo: 5 anos
    Valor: R$ 50.000,00 por ano
    
    Cláusulas específicas sobre conservação do solo, 
    responsabilidade ambiental e ITR.
    """
    
    # Simular agentes disponíveis
    agentes_teste = [
        {
            'id': 1,
            'nome': 'Especialista em Contratos Rurais',
            'classe': 'especialista',
            'descricao': 'Especializado em contratos de arrendamento e parceria rural',
            'capacidades': ['análise de contratos rurais', 'consultoria agrária', 'revisão de cláusulas']
        },
        {
            'id': 2,
            'nome': 'Assistente Principal de Direito Agrário',
            'classe': 'assistente_principal',
            'descricao': 'Coordenação geral em questões do direito agrário',
            'capacidades': ['coordenação jurídica', 'análise complexa', 'assessoria estratégica']
        }
    ]
    
    selecionados, relatorio = processar_selecao_inteligente(texto_teste, agentes_teste, 2)
    
    print("📊 RELATÓRIO DE SELEÇÃO INTELIGENTE")
    print("=" * 50)
    print(f"Área: {relatorio['documento']['area_identificada']}")
    print(f"Confiança: {relatorio['resumo']['area_confianca']}")
    print(f"Agentes selecionados: {len(selecionados)}")
    
    for i, agente in enumerate(selecionados, 1):
        print(f"\n{i}. {agente['nome']}")
        print(f"   Pontuação: {agente['pontuacao_capacidades']:.2f}")
        print(f"   Adequação: {agente['adequacao_documento']:.2f}")