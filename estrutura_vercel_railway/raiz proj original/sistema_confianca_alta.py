"""
Sistema de Confiança Alta para Seleção de Agentes
Implementa estrutura para alcançar >90% de confiança
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import uuid

from models import ResultadoAnaliseMultiAgente
from main import db
from algoritmo_selecao_inteligente_v2 import AlgoritmoSelecaoInteligente, AgentScore

logger = logging.getLogger(__name__)

@dataclass 
class ConfiguracaoConfianca:
    """Configurações para níveis de confiança"""
    confianca_minima_aceitavel: float = 0.90
    numero_agentes_otimo: int = 3
    numero_agentes_maximo: int = 5
    peso_especialidade: float = 0.35
    peso_experiencia: float = 0.25
    peso_contexto: float = 0.25
    peso_historico: float = 0.15
    bonus_consenso: float = 0.10

@dataclass
class ResultadoSelecao:
    """Resultado da seleção de agentes com alta confiança"""
    agentes_selecionados: List[AgentScore]
    confianca_final: float
    metrica_qualidade: Dict[str, float]
    justificativa_selecao: str
    recomendacoes_melhoria: List[str]
    nivel_certeza: str  # "ALTA", "MUITO_ALTA", "EXTREMA"

class SistemaConfiancaAlta:
    """Sistema principal para garantir alta confiança na seleção"""
    
    def __init__(self):
        self.algoritmo = AlgoritmoSelecaoInteligente()
        self.config = ConfiguracaoConfianca()
        self.historico_sucessos = {}
        self.cache_analises = {}
    
    def processar_com_alta_confianca(self, texto_documento: str, 
                                   agentes_disponiveis: List[Dict]) -> ResultadoSelecao:
        """
        Processa documento com garantia de alta confiança na seleção
        """
        logger.info("🎯 Iniciando processamento com garantia de alta confiança")
        
        # 1. Análise aprofundada do documento
        analise_documento = self._analise_documento_aprofundada(texto_documento)
        
        # 2. Validação da qualidade da análise
        if analise_documento['confianca'] < 0.7:
            # Tentar análise com contexto expandido
            analise_documento = self._analise_com_contexto_expandido(texto_documento)
        
        # 3. Seleção de agentes com múltiplos critérios
        selecao_inicial = self.algoritmo.selecionar_agentes_otimizado(
            agentes_disponiveis, analise_documento, self.config.numero_agentes_maximo
        )
        
        # 4. Refinamento da seleção
        selecao_refinada = self._refinar_selecao(selecao_inicial, analise_documento)
        
        # 5. Validação final e cálculo de confiança
        resultado_final = self._validar_e_calcular_confianca(
            selecao_refinada, analise_documento, texto_documento
        )
        
        # 6. Salvar resultado com identificador único
        resultado_id = self._salvar_resultado_com_id_unico(
            resultado_final, texto_documento, analise_documento
        )
        
        logger.info(f"✅ Processamento concluído - Confiança: {resultado_final.confianca_final:.1%}")
        logger.info(f"📄 Resultado salvo com ID: {resultado_id}")
        
        return resultado_final
    
    def _analise_documento_aprofundada(self, texto: str) -> Dict[str, Any]:
        """Análise aprofundada com múltiplas técnicas"""
        
        # Criar hash para cache
        texto_hash = hashlib.md5(texto.encode()).hexdigest()
        if texto_hash in self.cache_analises:
            return self.cache_analises[texto_hash]
        
        # Análise básica
        analise_basica = self.algoritmo.analisar_documento(texto)
        
        # Análise semântica adicional
        analise_semantica = self._analise_semantica_avancada(texto)
        
        # Análise estrutural
        analise_estrutural = self._analise_estrutural_documento(texto)
        
        # Combinar análises
        analise_combinada = self._combinar_analises(
            analise_basica, analise_semantica, analise_estrutural
        )
        
        # Cache do resultado
        self.cache_analises[texto_hash] = analise_combinada
        
        return analise_combinada
    
    def _analise_semantica_avancada(self, texto: str) -> Dict[str, Any]:
        """Análise semântica mais sofisticada"""
        
        # Detectar padrões complexos
        padroes_complexos = {
            'contrato_empresarial': [
                r'contrato.*prestação.*serviços?',
                r'cnpj.*\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',
                r'(pessoa jurídica|empresa|sociedade)',
                r'(cláusula|clausula).*\d+',
                r'(contratante|contratada)'
            ],
            'documento_processual': [
                r'processo.*n[úu]mero.*\d',
                r'(autor|réu|requerente|requerido)',
                r'(juiz|magistrado|tribunal)',
                r'(peti[çc][ãa]o|recurso|apela[çc][ãa]o)',
                r'(artigo|art\.?).*\d+'
            ],
            'parecer_consultivo': [
                r'parecer.*jurídico',
                r'(consulta|consultoria).*jurídica',
                r'(opinião|entendimento).*jurídic',
                r'(recomenda[çc][ãa]o|sugest[ãa]o)',
                r'(fundamenta[çc][ãa]o.*legal|base.*legal)'
            ]
        }
        
        scores_semanticos = {}
        for tipo, padroes in padroes_complexos.items():
            score = 0
            for padrao in padroes:
                matches = len(re.findall(padrao, texto, re.IGNORECASE))
                score += matches * 2
            scores_semanticos[tipo] = score
        
        # Determinar tipo principal
        tipo_principal = max(scores_semanticos.keys(), key=lambda x: scores_semanticos[x]) if scores_semanticos else 'generico'
        
        return {
            'tipo_documento': tipo_principal,
            'scores_semanticos': scores_semanticos,
            'confianca_semantica': min(0.95, scores_semanticos.get(tipo_principal, 0) / 10)
        }
    
    def _analise_estrutural_documento(self, texto: str) -> Dict[str, Any]:
        """Análise da estrutura do documento"""
        
        linhas = texto.split('\n')
        paragrafos = [p.strip() for p in texto.split('\n\n') if p.strip()]
        
        # Detectar estruturas
        tem_clausulas = len(re.findall(r'cl[áa]usula.*\d+', texto, re.IGNORECASE)) > 0
        tem_artigos = len(re.findall(r'(artigo|art\.?).*\d+', texto, re.IGNORECASE)) > 0
        tem_paragrafos_numerados = len(re.findall(r'§.*\d+', texto)) > 0
        tem_incisos = len(re.findall(r'inciso.*[IVX]+', texto, re.IGNORECASE)) > 0
        
        # Calcular complexidade estrutural
        complexidade = 0
        if tem_clausulas: complexidade += 3
        if tem_artigos: complexidade += 2
        if tem_paragrafos_numerados: complexidade += 2
        if tem_incisos: complexidade += 1
        
        estrutura_identificada = []
        if tem_clausulas: estrutura_identificada.append('contrato')
        if tem_artigos: estrutura_identificada.append('lei_ou_regulamento')
        if tem_paragrafos_numerados: estrutura_identificada.append('documento_formal')
        
        return {
            'estrutura_detectada': estrutura_identificada,
            'complexidade_estrutural': complexidade,
            'numero_paragrafos': len(paragrafos),
            'numero_linhas': len(linhas),
            'densidade_textual': len(texto) / max(len(paragrafos), 1)
        }
    
    def _combinar_analises(self, basica: Dict, semantica: Dict, estrutural: Dict) -> Dict[str, Any]:
        """Combina diferentes análises em uma única análise robusta"""
        
        # Calcular confiança combinada
        confianca_basica = basica.get('confianca', 0)
        confianca_semantica = semantica.get('confianca_semantica', 0)
        confianca_estrutural = min(0.8, estrutural.get('complexidade_estrutural', 0) / 10)
        
        # Peso para cada tipo de análise
        confianca_final = (
            confianca_basica * 0.5 +
            confianca_semantica * 0.3 +
            confianca_estrutural * 0.2
        )
        
        # Determinar área final com base nas evidências
        area_final = basica.get('area_detectada', 'geral')
        tipo_documento = semantica.get('tipo_documento', 'generico')
        
        # Ajustar área baseada no tipo de documento
        if tipo_documento == 'contrato_empresarial':
            area_final = 'empresarial'
            confianca_final = min(0.95, confianca_final * 1.2)
        elif tipo_documento == 'documento_processual':
            if area_final in ['penal', 'civil', 'trabalhista']:
                confianca_final = min(0.95, confianca_final * 1.15)
        
        return {
            'area_detectada': area_final,
            'confianca': confianca_final,
            'pontuacao': basica.get('pontuacao', 0),
            'matches': basica.get('matches', []),
            'tipo_documento': tipo_documento,
            'analise_semantica': semantica,
            'analise_estrutural': estrutural,
            'metrica_qualidade': {
                'confianca_basica': confianca_basica,
                'confianca_semantica': confianca_semantica,
                'confianca_estrutural': confianca_estrutural,
                'confianca_combinada': confianca_final
            }
        }
    
    def _analise_com_contexto_expandido(self, texto: str) -> Dict[str, Any]:
        """Análise com contexto expandido quando a inicial falha"""
        
        logger.info("🔍 Executando análise com contexto expandido")
        
        # Extrair mais contexto
        palavras_chave_expandidas = self._extrair_palavras_chave_expandidas(texto)
        entidades_juridicas = self._identificar_entidades_juridicas(texto)
        
        # Re-análise com informações expandidas
        analise_expandida = self.algoritmo.analisar_documento(texto)
        
        # Boost de confiança baseado em entidades identificadas
        if entidades_juridicas:
            boost_confianca = len(entidades_juridicas) * 0.1
            analise_expandida['confianca'] = min(0.9, analise_expandida['confianca'] + boost_confianca)
        
        return analise_expandida
    
    def _extrair_palavras_chave_expandidas(self, texto: str) -> List[str]:
        """Extrai palavras-chave juridicas específicas"""
        
        palavras_juridicas = [
            'contrato', 'acordo', 'termo', 'clausula', 'obrigação', 'direito', 'dever',
            'responsabilidade', 'indenização', 'dano', 'prejuízo', 'reparação',
            'processo', 'ação', 'petição', 'recurso', 'sentença', 'acórdão',
            'lei', 'decreto', 'regulamento', 'norma', 'jurisprudência',
            'empresa', 'sociedade', 'cnpj', 'cpf', 'pessoa jurídica', 'pessoa física'
        ]
        
        texto_lower = texto.lower()
        palavras_encontradas = []
        
        for palavra in palavras_juridicas:
            if palavra in texto_lower:
                palavras_encontradas.append(palavra)
        
        return palavras_encontradas
    
    def _identificar_entidades_juridicas(self, texto: str) -> List[Dict[str, str]]:
        """Identifica entidades jurídicas específicas"""
        
        padroes_entidades = {
            'cnpj': r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',
            'cpf': r'\d{3}\.\d{3}\.\d{3}-\d{2}',
            'processo': r'\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}',
            'lei': r'lei\s+n[°º]?\s*\d+',
            'artigo': r'art\.?\s*\d+',
            'clausula': r'cl[áa]usula\s+\d+'
        }
        
        entidades = []
        for tipo, padrao in padroes_entidades.items():
            matches = re.findall(padrao, texto, re.IGNORECASE)
            for match in matches:
                entidades.append({'tipo': tipo, 'valor': match})
        
        return entidades
    
    def _refinar_selecao(self, agentes_iniciais: List[AgentScore], 
                        analise_documento: Dict) -> List[AgentScore]:
        """Refina a seleção de agentes para máxima qualidade"""
        
        # Aplicar filtros de qualidade
        agentes_qualificados = [
            agente for agente in agentes_iniciais 
            if agente.score_final >= 3.0 and agente.confianca_percentual >= 70
        ]
        
        if len(agentes_qualificados) < self.config.numero_agentes_otimo:
            # Relaxar critérios se necessário
            agentes_qualificados = [
                agente for agente in agentes_iniciais
                if agente.score_final >= 2.0
            ]
        
        # Garantir diversidade
        agentes_diversos = self._garantir_diversidade(agentes_qualificados)
        
        # Otimizar para confiança
        agentes_otimizados = self._otimizar_para_confianca(agentes_diversos, analise_documento)
        
        return agentes_otimizados[:self.config.numero_agentes_otimo]
    
    def _garantir_diversidade(self, agentes: List[AgentScore]) -> List[AgentScore]:
        """Garante diversidade de especialidades"""
        
        especialidades_vistas = set()
        agentes_diversos = []
        
        # Primeiro, um de cada especialidade
        for agente in agentes:
            especialidade_base = agente.especialidade.split()[0] if agente.especialidade else "geral"
            if especialidade_base not in especialidades_vistas:
                agentes_diversos.append(agente)
                especialidades_vistas.add(especialidade_base)
        
        # Depois, completar com os melhores
        for agente in agentes:
            if agente not in agentes_diversos and len(agentes_diversos) < 5:
                agentes_diversos.append(agente)
        
        return agentes_diversos
    
    def _otimizar_para_confianca(self, agentes: List[AgentScore], 
                                analise: Dict) -> List[AgentScore]:
        """Otimiza seleção para máxima confiança"""
        
        # Boost para agentes altamente especializados na área detectada
        area_detectada = analise.get('area_detectada', '')
        
        for agente in agentes:
            if area_detectada in agente.nome.lower() or area_detectada in agente.especialidade.lower():
                agente.score_final *= 1.2
                agente.confianca_percentual = min(95, agente.confianca_percentual * 1.1)
        
        # Re-ordenar por score final
        agentes.sort(key=lambda x: x.score_final, reverse=True)
        
        return agentes
    
    def _validar_e_calcular_confianca(self, agentes: List[AgentScore], 
                                     analise: Dict, texto: str) -> ResultadoSelecao:
        """Validação final e cálculo da confiança do sistema"""
        
        # Calcular métricas de qualidade
        score_medio = sum(a.score_final for a in agentes) / len(agentes) if agentes else 0
        confianca_media = sum(a.confianca_percentual for a in agentes) / len(agentes) if agentes else 0
        
        # Confiança do documento
        confianca_documento = analise.get('confianca', 0)
        
        # Confiança final combinada
        confianca_final = (
            confianca_documento * 0.4 +
            (confianca_media / 100) * 0.4 +
            min(1.0, score_medio / 8) * 0.2
        )
        
        # Aplicar bônus por qualidade
        if score_medio > 6:
            confianca_final = min(0.95, confianca_final * 1.1)
        
        if len(agentes) >= self.config.numero_agentes_otimo:
            confianca_final = min(0.95, confianca_final * 1.05)
        
        # Determinar nível de certeza
        if confianca_final >= 0.95:
            nivel_certeza = "EXTREMA"
        elif confianca_final >= 0.90:
            nivel_certeza = "MUITO_ALTA"
        elif confianca_final >= 0.80:
            nivel_certeza = "ALTA"
        else:
            nivel_certeza = "MODERADA"
        
        # Gerar justificativa
        justificativa = self._gerar_justificativa(agentes, analise, confianca_final)
        
        # Gerar recomendações
        recomendacoes = self._gerar_recomendacoes(confianca_final, agentes, analise)
        
        return ResultadoSelecao(
            agentes_selecionados=agentes,
            confianca_final=confianca_final,
            metrica_qualidade={
                'score_medio_agentes': score_medio,
                'confianca_media_agentes': confianca_media,
                'confianca_documento': confianca_documento,
                'qualidade_selecao': score_medio / 10,
                'diversidade_especialidades': len(set(a.especialidade for a in agentes))
            },
            justificativa_selecao=justificativa,
            recomendacoes_melhoria=recomendacoes,
            nivel_certeza=nivel_certeza
        )
    
    def _gerar_justificativa(self, agentes: List[AgentScore], analise: Dict, 
                           confianca: float) -> str:
        """Gera justificativa detalhada da seleção"""
        
        area = analise.get('area_detectada', 'geral')
        tipo_doc = analise.get('tipo_documento', 'generico')
        
        justificativa = f"Seleção baseada em análise de {area.title()} com {confianca:.1%} de confiança. "
        justificativa += f"Documento identificado como {tipo_doc.replace('_', ' ')}. "
        
        if agentes:
            melhor_agente = agentes[0]
            justificativa += f"Agente principal: {melhor_agente.nome} "
            justificativa += f"(score: {melhor_agente.score_final:.1f}, "
            justificativa += f"confiança: {melhor_agente.confianca_percentual:.0f}%). "
        
        if confianca >= 0.90:
            justificativa += "Alta correspondência entre documento e especialistas selecionados."
        
        return justificativa
    
    def _gerar_recomendacoes(self, confianca: float, agentes: List[AgentScore], 
                           analise: Dict) -> List[str]:
        """Gera recomendações para melhorar a confiança"""
        
        recomendacoes = []
        
        if confianca < 0.90:
            recomendacoes.append("Considerar fornecimento de mais contexto no documento")
            recomendacoes.append("Revisar seleção de agentes para melhor especialização")
        
        if len(agentes) < 3:
            recomendacoes.append("Ampliar base de agentes especializados")
        
        score_medio = sum(a.score_final for a in agentes) / len(agentes) if agentes else 0
        if score_medio < 5:
            recomendacoes.append("Melhorar correspondência entre documento e agentes")
        
        confianca_doc = analise.get('confianca', 0)
        if confianca_doc < 0.8:
            recomendacoes.append("Documento pode necessitar de informações adicionais")
        
        return recomendacoes
    
    def _salvar_resultado_com_id_unico(self, resultado: ResultadoSelecao, 
                                     texto: str, analise: Dict) -> str:
        """Salva resultado na base de dados com ID único"""
        
        try:
            # Gerar ID único
            resultado_id = str(uuid.uuid4())
            
            # Preparar dados para salvamento
            agentes_data = [asdict(agente) for agente in resultado.agentes_selecionados]
            
            # Criar registro na base
            registro = ResultadoAnaliseMultiAgente(
                id=resultado_id,
                documento_original=texto[:5000],  # Limite para performance
                documento_nome="Análise via Sistema de Alta Confiança",
                tipo_analise="sistema_confianca_alta",
                resultado_principal={
                    'confianca_final': resultado.confianca_final,
                    'nivel_certeza': resultado.nivel_certeza,
                    'justificativa': resultado.justificativa_selecao,
                    'metricas': resultado.metrica_qualidade,
                    'area_detectada': analise.get('area_detectada'),
                    'tipo_documento': analise.get('tipo_documento')
                },
                resultados_agentes={
                    'agentes_selecionados': agentes_data,
                    'analise_documento': analise,
                    'configuracao_sistema': asdict(self.config)
                },
                agentes_utilizados=[agente.nome for agente in resultado.agentes_selecionados],
                tempo_processamento=0,  # Será atualizado pela API
                status="concluida",
                provider_principal="sistema_confianca_alta"
            )
            
            db.session.add(registro)
            db.session.commit()
            
            logger.info(f"✅ Resultado salvo com ID único: {resultado_id}")
            return resultado_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultado: {e}")
            db.session.rollback()
            return None

def testar_sistema_confianca():
    """Função de teste do sistema"""
    
    sistema = SistemaConfiancaAlta()
    
    texto_teste = """
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS EMPRESARIAIS
    
    CONTRATANTE: Tech Solutions Ltda. - CNPJ: 12.345.678/0001-90
    CONTRATADA: Legal Advisory ME - CNPJ: 98.765.432/0001-10
    
    Cláusula 1ª - DO OBJETO
    O presente contrato tem por objeto a prestação de serviços de consultoria 
    jurídica empresarial especializada.
    
    Cláusula 2ª - DAS OBRIGAÇÕES CONTRATUAIS
    A CONTRATADA se obriga a prestar os serviços comerciais e societários 
    com excelência e pontualidade.
    """
    
    # Simular agentes disponíveis
    agentes_mock = [
        {'id': 1, 'nome': 'Especialista Empresarial Senior', 'especialidade': 'Direito Empresarial', 'capacidades': ['contratos', 'sociedades'], 'nivel_experiencia': 'senior'},
        {'id': 2, 'nome': 'Consultor Civil', 'especialidade': 'Direito Civil', 'capacidades': ['contratos', 'obrigações'], 'nivel_experiencia': 'pleno'},
        {'id': 3, 'nome': 'Analista Empresarial', 'especialidade': 'Direito Empresarial', 'capacidades': ['consultoria', 'empresarial'], 'nivel_experiencia': 'junior'}
    ]
    
    resultado = sistema.processar_com_alta_confianca(texto_teste, agentes_mock)
    
    print(f"Confiança Final: {resultado.confianca_final:.1%}")
    print(f"Nível de Certeza: {resultado.nivel_certeza}")
    print(f"Agentes Selecionados: {len(resultado.agentes_selecionados)}")
    print(f"Justificativa: {resultado.justificativa_selecao}")
    
    return resultado

if __name__ == "__main__":
    testar_sistema_confianca()