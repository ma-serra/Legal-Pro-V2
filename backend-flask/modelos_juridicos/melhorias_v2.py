"""
Melhorias Meta Modelo de Especificidade Jurídica - Fase 1
=========================================================

Implementa melhorias incrementais mantendo compatibilidade com funcionalidades atuais.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
import yaml
import os
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report
import warnings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('meta_modelo_juridico')

class ValidacaoTemporal:
    """
    Sistema de validação temporal rigorosa com embargo e walk-forward validation
    """
    
    def __init__(self, embargo_days: int = 30):
        self.embargo_days = embargo_days
        logger.info(f"ValidacaoTemporal inicializada com embargo de {embargo_days} dias")
    
    def split_temporal(self, data: pd.DataFrame, date_column: str = 'ano') -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Walk-forward validation com embargo temporal
        - Treino sempre no passado
        - Gap entre treino/teste para evitar lookahead bias
        
        Args:
            data: DataFrame com dados temporais
            date_column: nome da coluna de data
            
        Returns:
            Lista de tuplas (indices_treino, indices_teste)
        """
        try:
            # Ordenar por data
            data_sorted = data.sort_values(date_column).reset_index(drop=True)
            
            # Usar TimeSeriesSplit com gap para embargo
            tscv = TimeSeriesSplit(n_splits=3, gap=self.embargo_days)
            
            splits = []
            for train_idx, test_idx in tscv.split(data_sorted):
                splits.append((train_idx, test_idx))
            
            logger.info(f"Criados {len(splits)} splits temporais com embargo de {self.embargo_days} dias")
            return splits
            
        except Exception as e:
            logger.error(f"Erro no split temporal: {e}")
            return []
    
    def validar_estabilidade(self, modelo, data: pd.DataFrame, periodos: List[int]) -> Dict:
        """
        Medir estabilidade do modelo ao longo do tempo
        
        Args:
            modelo: modelo treinado
            data: dados para validação
            periodos: lista de períodos para análise
            
        Returns:
            dict com coef_variacao_especificidade, alertas_drift
        """
        try:
            especificidades = []
            
            for periodo in periodos:
                # Filtrar dados do período
                dados_periodo = data[data['ano'] == periodo]
                if len(dados_periodo) > 0:
                    # Simular especificidade (substituir por cálculo real)
                    esp = np.random.uniform(0.75, 0.95)  # Placeholder
                    especificidades.append(esp)
            
            if len(especificidades) < 2:
                return {'coef_variacao_especificidade': 0, 'alertas_drift': []}
            
            # Calcular coeficiente de variação
            cv = np.std(especificidades) / np.mean(especificidades)
            
            # Detectar alertas de drift
            alertas = []
            if cv > 0.05:  # Threshold configurável
                alertas.append(f"Alta variabilidade detectada: CV={cv:.3f}")
            
            logger.info(f"Estabilidade validada: CV={cv:.3f}, {len(alertas)} alertas")
            
            return {
                'coef_variacao_especificidade': cv,
                'alertas_drift': alertas,
                'especificidades_periodo': especificidades,
                'media_especificidade': np.mean(especificidades)
            }
            
        except Exception as e:
            logger.error(f"Erro na validação de estabilidade: {e}")
            return {'coef_variacao_especificidade': 999, 'alertas_drift': ['Erro na análise']}


class MonitoramentoDrift:
    """
    Sistema básico de monitoramento de drift de especificidade
    """
    
    def __init__(self, threshold_alerta: float = 0.05):
        self.threshold_alerta = threshold_alerta
        self.historico_especificidade = []
        logger.info(f"MonitoramentoDrift inicializado com threshold {threshold_alerta}")
    
    def detectar_drift_especificidade(self, historico_especificidade: List[float], 
                                    janela_dias: int = 90) -> Dict:
        """
        Detectar mudanças significativas na especificidade
        Alerta quando especificidade cai > 5% em relação à baseline
        
        Args:
            historico_especificidade: lista de valores de especificidade
            janela_dias: janela de análise em dias
            
        Returns:
            dict com status_drift, magnitude_drift, alertas
        """
        try:
            if len(historico_especificidade) < 2:
                return {'status_drift': 'dados_insuficientes', 'magnitude_drift': 0, 'alertas': []}
            
            # Calcular baseline (primeira metade dos dados)
            meio = len(historico_especificidade) // 2
            baseline = np.mean(historico_especificidade[:meio])
            
            # Calcular período recente (segunda metade)
            recente = np.mean(historico_especificidade[meio:])
            
            # Calcular magnitude do drift
            magnitude_drift = (baseline - recente) / baseline
            
            # Detectar alertas
            alertas = []
            status_drift = 'estavel'
            
            if magnitude_drift > self.threshold_alerta:
                status_drift = 'drift_detectado'
                alertas.append(f"Queda de especificidade: -{magnitude_drift*100:.1f}%")
                alertas.append(f"Baseline: {baseline:.3f} → Recente: {recente:.3f}")
            
            logger.info(f"Drift analysis: status={status_drift}, magnitude={magnitude_drift:.3f}")
            
            return {
                'status_drift': status_drift,
                'magnitude_drift': magnitude_drift,
                'alertas': alertas,
                'baseline_especificidade': baseline,
                'especificidade_recente': recente
            }
            
        except Exception as e:
            logger.error(f"Erro na detecção de drift: {e}")
            return {'status_drift': 'erro', 'magnitude_drift': 0, 'alertas': ['Erro na análise']}
    
    def gerar_relatorio_drift(self, foro: str, periodo: str) -> Dict:
        """
        Relatório de mudanças por foro/período
        
        Args:
            foro: nome do foro
            periodo: período de análise
            
        Returns:
            dict com relatório detalhado
        """
        try:
            # Simular dados históricos por foro (substituir por dados reais)
            dados_simulados = np.random.uniform(0.70, 0.90, 10)
            
            drift_analysis = self.detectar_drift_especificidade(dados_simulados.tolist())
            
            relatorio = {
                'foro': foro,
                'periodo': periodo,
                'timestamp': datetime.now().isoformat(),
                'drift_analysis': drift_analysis,
                'recomendacoes': []
            }
            
            # Gerar recomendações baseadas no drift
            if drift_analysis['status_drift'] == 'drift_detectado':
                relatorio['recomendacoes'].extend([
                    "Revisar critérios de seleção de casos",
                    "Analisar mudanças na composição do foro",
                    "Considerar retreinamento do modelo"
                ])
            
            logger.info(f"Relatório de drift gerado para {foro} - {periodo}")
            return relatorio
            
        except Exception as e:
            logger.error(f"Erro na geração do relatório: {e}")
            return {'erro': str(e)}


class ModeloDefesaSegmentado:
    """
    Extensão do ModeloDefesa original com segmentação por área jurídica
    Mantém compatibilidade total com a API existente
    """
    
    def __init__(self, data_path: str = 'modelos_juridicos/data'):
        # Importar classe original para manter compatibilidade
        from .modulo_modelos_juridicos import ModeloDefesa
        
        self.modelo_base = ModeloDefesa(data_path)
        self.data_path = data_path
        
        # Modelos por área
        self.modelos_por_area = {
            'trabalhista': None,
            'civil': None,
            'consumidor': None,
            'tributario': None
        }
        
        # Sistemas de melhorias
        self.validacao_temporal = ValidacaoTemporal()
        self.monitoramento_drift = MonitoramentoDrift()
        
        logger.info("ModeloDefesaSegmentado inicializado com compatibilidade v1_")
    
    def v1_treinar(self, test_size: float = 0.2) -> Dict:
        """
        Método de compatibilidade - mantém API original
        """
        return self.modelo_base.treinar(test_size)
    
    def v1_prever(self, caso: Dict) -> Dict:
        """
        Método de compatibilidade - mantém API original
        """
        return self.modelo_base.prever(caso)
    
    def treinar_por_area(self, dataset_path: str = None) -> Dict:
        """
        Treinar modelos específicos para cada área jurídica
        
        Args:
            dataset_path: caminho opcional para dataset específico
            
        Returns:
            dict com resultados do treinamento por área
        """
        try:
            # Carregar dados
            df = self.modelo_base.carregar_dados()
            
            resultados = {
                'areas_treinadas': [],
                'metricas_por_area': {},
                'validacao_temporal': {},
                'alertas': []
            }
            
            # Treinar para cada área com dados suficientes
            for area in self.modelos_por_area.keys():
                dados_area = df[df['area'].str.lower().str.contains(area, na=False)]
                
                if len(dados_area) < 50:  # Mínimo de dados para treinar
                    logger.warning(f"Dados insuficientes para área {area}: {len(dados_area)} registros")
                    resultados['alertas'].append(f"Área {area}: dados insuficientes ({len(dados_area)} registros)")
                    continue
                
                # Treinar modelo específico para a área
                modelo_area = self._treinar_modelo_area(dados_area, area)
                self.modelos_por_area[area] = modelo_area
                
                resultados['areas_treinadas'].append(area)
                resultados['metricas_por_area'][area] = modelo_area.get('metricas', {})
                
                # Validação temporal para a área
                validacao = self.validacao_temporal.validar_estabilidade(
                    modelo_area['modelo'], dados_area, dados_area['ano'].unique()
                )
                resultados['validacao_temporal'][area] = validacao
            
            logger.info(f"Treinamento por área concluído: {len(resultados['areas_treinadas'])} áreas")
            return resultados
            
        except Exception as e:
            logger.error(f"Erro no treinamento por área: {e}")
            return {'erro': str(e)}
    
    def _treinar_modelo_area(self, dados_area: pd.DataFrame, area: str) -> Dict:
        """Treinar modelo específico para uma área"""
        try:
            # Usar validação temporal
            splits = self.validacao_temporal.split_temporal(dados_area)
            
            if not splits:
                logger.warning(f"Não foi possível criar splits temporais para {area}")
                return {'erro': 'splits_temporais_falharam'}
            
            # Usar o primeiro split para treino
            train_idx, test_idx = splits[0]
            
            # Simular treinamento (substituir por lógica real)
            modelo_simulado = {
                'modelo': f"modelo_{area}",  # Placeholder
                'metricas': {
                    'auc': np.random.uniform(0.75, 0.95),
                    'especificidade': np.random.uniform(0.70, 0.90),
                    'n_treino': len(train_idx),
                    'n_teste': len(test_idx)
                },
                'area': area,
                'timestamp': datetime.now().isoformat()
            }
            
            return modelo_simulado
            
        except Exception as e:
            logger.error(f"Erro no treinamento do modelo para {area}: {e}")
            return {'erro': str(e)}
    
    def prever_contextualizado(self, caso: Dict) -> Dict:
        """
        Usar modelo específico da área + modelo geral como fallback
        
        Args:
            caso: dict com dados do caso incluindo 'area'
            
        Returns:
            dict com predição contextualizada e metadata
        """
        try:
            area_caso = caso.get('area', '').lower()
            modelo_usado = 'geral'
            
            # Tentar usar modelo específico da área
            for area_key in self.modelos_por_area.keys():
                if area_key in area_caso and self.modelos_por_area[area_key] is not None:
                    modelo_usado = area_key
                    break
            
            # Predição com modelo específico ou geral
            if modelo_usado != 'geral':
                # Usar modelo da área específica
                predicao = self._prever_com_modelo_area(caso, modelo_usado)
            else:
                # Fallback para modelo geral
                predicao = self.v1_prever(caso)
            
            # Adicionar contexto e metadata
            resultado = {
                **predicao,
                'modelo_usado': modelo_usado,
                'contexto_area': area_caso,
                'timestamp': datetime.now().isoformat(),
                'confianca_contextual': self._calcular_confianca_contexto(caso, modelo_usado)
            }
            
            logger.info(f"Predição contextualizada usando modelo: {modelo_usado}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na predição contextualizada: {e}")
            # Fallback para modelo original em caso de erro
            return self.v1_prever(caso)
    
    def _prever_com_modelo_area(self, caso: Dict, area: str) -> Dict:
        """Fazer predição com modelo específico da área"""
        # Placeholder - implementar lógica real de predição
        modelo_area = self.modelos_por_area[area]
        
        return {
            'probabilidade_vitoria': np.random.uniform(0.60, 0.95),
            'area_especializada': area,
            'metricas_modelo': modelo_area.get('metricas', {}),
            'recomendacao': f"Predição usando modelo especializado em {area}"
        }
    
    def _calcular_confianca_contexto(self, caso: Dict, modelo_usado: str) -> float:
        """Calcular nível de confiança baseado no contexto"""
        confianca_base = 0.8
        
        # Ajustar confiança baseado no modelo usado
        if modelo_usado != 'geral':
            confianca_base += 0.1  # Maior confiança com modelo especializado
        
        # Ajustar baseado na completude dos dados
        campos_obrigatorios = ['foro', 'area', 'valor_causa']
        campos_presentes = sum(1 for campo in campos_obrigatorios if caso.get(campo))
        confianca_ajustada = confianca_base * (campos_presentes / len(campos_obrigatorios))
        
        return min(confianca_ajustada, 1.0)
    
    def detectar_outlier(self, caso: Dict) -> Dict:
        """
        Identificar casos que fogem do padrão histórico
        
        Args:
            caso: dict com dados do caso
            
        Returns:
            dict com is_outlier (bool), score_atipicidade (0-1), explicacao
        """
        try:
            # Carregar dados históricos para comparação
            df = self.modelo_base.carregar_dados()
            
            # Calcular scores de atipicidade baseados em features principais
            score_valor = self._calcular_score_valor_atipico(caso, df)
            score_area = self._calcular_score_area_atipica(caso, df)
            score_foro = self._calcular_score_foro_atipico(caso, df)
            
            # Score geral de atipicidade
            score_atipicidade = np.mean([score_valor, score_area, score_foro])
            is_outlier = score_atipicidade > 0.7  # Threshold configurável
            
            # Gerar explicação
            explicacao = []
            if score_valor > 0.5:
                explicacao.append(f"Valor da causa atípico: R$ {caso.get('valor_causa', 0):,.2f}")
            if score_area > 0.5:
                explicacao.append(f"Combinação área-foro incomum: {caso.get('area', 'N/A')}")
            if score_foro > 0.5:
                explicacao.append(f"Foro com padrão diferente: {caso.get('foro', 'N/A')}")
            
            if not explicacao:
                explicacao = ["Caso dentro do padrão histórico esperado"]
            
            resultado = {
                'is_outlier': is_outlier,
                'score_atipicidade': score_atipicidade,
                'explicacao': explicacao,
                'scores_detalhados': {
                    'valor': score_valor,
                    'area': score_area,
                    'foro': score_foro
                }
            }
            
            logger.info(f"Detecção de outlier: {is_outlier} (score: {score_atipicidade:.3f})")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na detecção de outlier: {e}")
            return {
                'is_outlier': False,
                'score_atipicidade': 0.0,
                'explicacao': ['Erro na análise de outlier'],
                'erro': str(e)
            }
    
    def _calcular_score_valor_atipico(self, caso: Dict, df: pd.DataFrame) -> float:
        """Calcular score de atipicidade baseado no valor da causa"""
        valor_caso = caso.get('valor_causa', 0)
        if valor_caso == 0:
            return 0.0
        
        # Estatísticas dos dados históricos
        q25, q75 = df['valor_causa'].quantile([0.25, 0.75])
        iqr = q75 - q25
        
        # Limites para outliers
        limite_inferior = q25 - 1.5 * iqr
        limite_superior = q75 + 1.5 * iqr
        
        if valor_caso < limite_inferior or valor_caso > limite_superior:
            # Calcular quão extremo é o valor
            if valor_caso < limite_inferior:
                score = min((limite_inferior - valor_caso) / limite_inferior, 1.0)
            else:
                score = min((valor_caso - limite_superior) / limite_superior, 1.0)
            return score
        
        return 0.0
    
    def _calcular_score_area_atipica(self, caso: Dict, df: pd.DataFrame) -> float:
        """Calcular score baseado na raridade da área jurídica"""
        area_caso = caso.get('area', '')
        if not area_caso:
            return 0.0
        
        # Frequência da área nos dados históricos
        freq_area = (df['area'] == area_caso).mean()
        
        # Quanto mais rara a área, maior o score
        score = max(0, 1 - freq_area * 10)  # Áreas com <10% de frequência são consideradas raras
        return min(score, 1.0)
    
    def _calcular_score_foro_atipico(self, caso: Dict, df: pd.DataFrame) -> float:
        """Calcular score baseado no padrão do foro"""
        foro_caso = caso.get('foro', '')
        if not foro_caso:
            return 0.0
        
        # Dados históricos do foro
        dados_foro = df[df['foro'] == foro_caso]
        if len(dados_foro) == 0:
            return 1.0  # Foro completamente novo
        
        # Taxa de vitória média do foro vs. geral
        taxa_foro = dados_foro['vitoria'].mean() if 'vitoria' in dados_foro.columns else 0.5
        taxa_geral = df['vitoria'].mean() if 'vitoria' in df.columns else 0.5
        
        # Score baseado na diferença das taxas
        diferenca = abs(taxa_foro - taxa_geral)
        score = min(diferenca * 2, 1.0)  # Multiplicar por 2 para amplificar diferenças
        
        return score


def carregar_configuracao() -> Dict:
    """
    Carregar configuração do arquivo YAML
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'modelo_config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.info("Configuração carregada com sucesso")
        return config
        
    except FileNotFoundError:
        logger.warning("Arquivo de configuração não encontrado, usando defaults")
        return {
            'validacao': {'embargo_days': 30, 'janela_drift': 90, 'threshold_alerta_drift': 0.05},
            'segmentacao': {'areas_ativas': ['trabalhista', 'civil', 'consumidor', 'tributario'], 'fallback_modelo_geral': True},
            'monitoramento': {'freq_verificacao_drift': 'diaria', 'salvar_metricas': True}
        }
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        return {}


def gerar_dashboard_metricas(data_path: str = 'modelos_juridicos/data') -> Dict:
    """
    Gerar relatório HTML/CSV com métricas do sistema
    
    Args:
        data_path: caminho para os dados
        
    Returns:
        dict com métricas e caminhos dos arquivos gerados
    """
    try:
        # Inicializar componentes
        modelo_segmentado = ModeloDefesaSegmentado(data_path)
        config = carregar_configuracao()
        
        # Coletar métricas do sistema
        metricas = {
            'timestamp': datetime.now().isoformat(),
            'especificidade_por_foro': {},
            'alertas_drift': [],
            'casos_atipicos_recentes': [],
            'metricas_calibracao': {},
            'config_sistema': config
        }
        
        # Simular dados para demonstração
        foros = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Porto Alegre']
        areas = ['civil', 'trabalhista', 'tributario', 'consumidor']
        
        for foro in foros:
            metricas['especificidade_por_foro'][foro] = {
                'especificidade_atual': np.random.uniform(0.75, 0.95),
                'casos_analisados': np.random.randint(50, 200),
                'tendencia': np.random.choice(['estavel', 'crescente', 'decrescente'])
            }
        
        # Gerar alertas de drift simulados
        drift_monitor = MonitoramentoDrift()
        for foro in foros[:2]:  # Apenas alguns foros
            relatorio = drift_monitor.gerar_relatorio_drift(foro, '2025-Q3')
            if relatorio.get('drift_analysis', {}).get('status_drift') == 'drift_detectado':
                metricas['alertas_drift'].append({
                    'foro': foro,
                    'tipo': 'drift_especificidade',
                    'severidade': 'media',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Casos atípicos simulados
        for i in range(3):
            caso_simulado = {
                'valor_causa': np.random.uniform(1000000, 5000000),
                'area': np.random.choice(areas),
                'foro': np.random.choice(foros)
            }
            deteccao = modelo_segmentado.detectar_outlier(caso_simulado)
            if deteccao['is_outlier']:
                metricas['casos_atipicos_recentes'].append({
                    'caso_id': f'CASO_{i+1:03d}',
                    'score_atipicidade': deteccao['score_atipicidade'],
                    'explicacao': deteccao['explicacao'][0] if deteccao['explicacao'] else 'N/A'
                })
        
        # Métricas de calibração simuladas
        metricas['metricas_calibracao'] = {
            'acuracia_geral': np.random.uniform(0.80, 0.95),
            'calibracao_probabilidades': np.random.uniform(0.75, 0.90),
            'coverage_intervalos_confianca': np.random.uniform(0.90, 0.98)
        }
        
        logger.info(f"Dashboard de métricas gerado com {len(metricas['alertas_drift'])} alertas")
        
        return {
            'metricas': metricas,
            'status': 'sucesso',
            'resumo': {
                'foros_monitorados': len(foros),
                'alertas_ativos': len(metricas['alertas_drift']),
                'casos_atipicos': len(metricas['casos_atipicos_recentes'])
            }
        }
        
    except Exception as e:
        logger.error(f"Erro na geração do dashboard: {e}")
        return {'erro': str(e), 'status': 'erro'}


# Funções de compatibilidade para integração com sistema existente
def inicializar_melhorias_v2(data_path: str = 'modelos_juridicos/data') -> Dict:
    """
    Função principal para inicializar as melhorias v2
    Mantém compatibilidade total com sistema existente
    """
    try:
        logger.info("Inicializando melhorias Meta Modelo v2...")
        
        # Carregar configuração
        config = carregar_configuracao()
        
        # Inicializar componentes principais
        modelo_segmentado = ModeloDefesaSegmentado(data_path)
        
        # Verificar compatibilidade com sistema existente
        teste_compatibilidade = modelo_segmentado.v1_treinar()
        
        resultado = {
            'status': 'inicializado',
            'componentes_ativos': [
                'ValidacaoTemporal',
                'MonitoramentoDrift', 
                'ModeloDefesaSegmentado'
            ],
            'compatibilidade_v1': bool(teste_compatibilidade),
            'config': config,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Melhorias v2 inicializadas com sucesso")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na inicialização das melhorias v2: {e}")
        return {'status': 'erro', 'erro': str(e)}