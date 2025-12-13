"""
Meta Modelo de Especificidade Jurídica v2.0 - Metodologias Estatísticas
======================================================================

Implementa as 4 metodologias estatísticas avançadas para análise de especificidade jurídica:
1. Regressão Beta para modelagem de especificidade (0-1)
2. GLM Binomial para análise TN/N_neg por foro × threshold
3. Modelo Bayesiano Bivariado para Sensibilidade × Especificidade
4. Modelo Generativo via Scores para curvas ROC/PR simuladas

Inspirado em arcabouços médicos de avaliação diagnóstica aplicado ao direito.
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.optimize import minimize
import statsmodels.api as sm
from statsmodels.genmod import families
import warnings
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from sklearn.metrics import roc_curve, precision_recall_curve, auc
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('meta_modelo_metodologias')

class RegressaoBetaEspecificidade:
    """
    Metodologia 1: Regressão Beta para análise de especificidade
    
    Modela especificidade (valores entre 0-1) como função de covariáveis:
    - Foro, área jurídica, ano, valor da causa
    - Distribuição Beta é ideal para proporções
    - Permite inferência sobre fatores que afetam especificidade
    """
    
    def __init__(self):
        self.modelo_fitted = None
        self.resultados = None
        self.covariates = None
        self.logger = logging.getLogger('RegressaoBeta')
        self.logger.info("Regressão Beta inicializada para análise de especificidade")
    
    def preparar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara dados para regressão Beta
        
        Args:
            df: DataFrame com colunas [especificidade, foro, area, ano, valor_causa]
            
        Returns:
            DataFrame preparado com dummies e transformações
        """
        try:
            dados = df.copy()
            
            # Ajustar especificidade para (0,1) - Beta não aceita 0 ou 1 exatos
            epsilon = 1e-6
            dados['especificidade_adj'] = dados['especificidade'].clip(epsilon, 1-epsilon)
            
            # Criar variáveis dummy para categóricas
            dados_encoded = pd.get_dummies(dados, columns=['foro', 'area'], prefix=['foro', 'area'])
            
            # Log-transformar valor da causa se presente
            if 'valor_causa' in dados.columns:
                dados_encoded['log_valor_causa'] = np.log1p(dados_encoded['valor_causa'])
            
            # Centralizar ano
            dados_encoded['ano_centrado'] = dados_encoded['ano'] - dados_encoded['ano'].mean()
            
            self.logger.info(f"Dados preparados: {len(dados_encoded)} observações, {dados_encoded.shape[1]} variáveis")
            return dados_encoded
            
        except Exception as e:
            self.logger.error(f"Erro na preparação de dados: {e}")
            raise
    
    def ajustar_modelo(self, df: pd.DataFrame, formula: str = None) -> Dict[str, Any]:
        """
        Ajusta modelo de Regressão Beta
        
        Args:
            df: dados preparados
            formula: fórmula R-style (opcional)
            
        Returns:
            Dicionário com resultados do modelo
        """
        try:
            if formula is None:
                # Fórmula padrão
                colunas_X = [col for col in df.columns if 
                           col.startswith('foro_') or col.startswith('area_') or 
                           col in ['ano_centrado', 'log_valor_causa']]
                X = df[colunas_X]
                y = df['especificidade_adj']
            else:
                # Usar fórmula personalizada (implementação simplificada)
                X = df[[col for col in df.columns if col != 'especificidade_adj']]
                y = df['especificidade_adj']
            
            # Adicionar intercepto
            X = sm.add_constant(X)
            
            # Ajustar modelo Beta usando GLM com família Beta
            try:
                # Usar família Gamma como aproximação
                modelo_beta = sm.GLM(y, X, family=families.Gamma())
                resultado = modelo_beta.fit()
                self.modelo_fitted = resultado
                
            except Exception as e:
                # Fallback para OLS se Beta falhar
                self.logger.warning(f"Modelo Beta falhou, usando OLS: {e}")
                modelo_ols = sm.OLS(y, X)
                resultado = modelo_ols.fit()
                self.modelo_fitted = resultado
            
            # Extrair resultados
            resultados_dict = {
                'coeficientes': resultado.params.to_dict(),
                'p_valores': resultado.pvalues.to_dict(),
                'intervalo_confianca': resultado.conf_int().to_dict(),
                'r_quadrado': getattr(resultado, 'rsquared', 0),
                'aic': resultado.aic,
                'bic': resultado.bic,
                'n_observacoes': len(y),
                'residuos': resultado.resid,
                'valores_preditos': resultado.fittedvalues
            }
            
            self.resultados = resultados_dict
            self.logger.info(f"Modelo Beta ajustado com AIC={resultado.aic:.2f}")
            
            return resultados_dict
            
        except Exception as e:
            self.logger.error(f"Erro no ajuste do modelo Beta: {e}")
            raise
    
    def prever_especificidade(self, novos_dados: pd.DataFrame) -> np.ndarray:
        """
        Prediz especificidade para novos casos
        
        Args:
            novos_dados: DataFrame com mesma estrutura dos dados de treino
            
        Returns:
            Array com especificidades preditas
        """
        if self.modelo_fitted is None:
            raise ValueError("Modelo não foi ajustado ainda")
        
        try:
            # Preparar novos dados com mesma estrutura
            dados_prep = self.preparar_dados(novos_dados)
            
            # Garantir mesmas colunas que no treino
            colunas_modelo = self.modelo_fitted.params.index
            X_novo = dados_prep.reindex(columns=colunas_modelo, fill_value=0)
            
            # Predizer
            predicoes = self.modelo_fitted.predict(X_novo)
            
            # Garantir que predições estão em [0,1]
            predicoes = np.clip(predicoes, 0, 1)
            
            self.logger.info(f"Predições geradas para {len(predicoes)} casos")
            return predicoes
            
        except Exception as e:
            self.logger.error(f"Erro na predição: {e}")
            raise
    
    def analisar_impacto_covariaveis(self) -> pd.DataFrame:
        """
        Analisa impacto de cada covariável na especificidade
        
        Returns:
            DataFrame com análise de impacto ordenada
        """
        if self.resultados is None:
            raise ValueError("Modelo não foi ajustado ainda")
        
        try:
            impactos = pd.DataFrame({
                'covariavel': list(self.resultados['coeficientes'].keys()),
                'coeficiente': list(self.resultados['coeficientes'].values()),
                'p_valor': list(self.resultados['p_valores'].values())
            })
            
            # Calcular significância
            impactos['significativo'] = impactos['p_valor'] < 0.05
            impactos['impacto_abs'] = np.abs(impactos['coeficiente'])
            
            # Ordenar por impacto absoluto
            impactos = impactos.sort_values('impacto_abs', ascending=False)
            
            self.logger.info(f"Análise de impacto gerada para {len(impactos)} covariáveis")
            return impactos
            
        except Exception as e:
            self.logger.error(f"Erro na análise de impacto: {e}")
            raise

class GLMBinomialTN:
    """
    Metodologia 2: GLM Binomial para análise TN/N_neg
    
    Modela a probabilidade de classificar corretamente um negativo (especificidade)
    como função de foro × threshold usando GLM Binomial.
    
    Entrada: contagens TN (verdadeiros negativos) e FP (falsos positivos)
    Saída: função logito para predizer especificidade por contexto
    """
    
    def __init__(self):
        self.modelo_glm = None
        self.resultados = None
        self.logger = logging.getLogger('GLMBinomial')
        self.logger.info("GLM Binomial inicializado para análise TN/N_neg")
    
    def preparar_dados_binomial(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara dados para GLM Binomial
        
        Args:
            df: DataFrame com [TN, FP, foro, threshold, area]
            
        Returns:
            DataFrame preparado com proporções e pesos
        """
        try:
            dados = df.copy()
            
            # Calcular totais e proporções
            dados['N_total'] = dados['TN'] + dados['FP']  # Total de negativos
            dados['proporção_TN'] = dados['TN'] / dados['N_total']  # Especificidade observada
            
            # Remover casos sem observações
            dados = dados[dados['N_total'] > 0].copy()
            
            # Criar interações foro × threshold
            dados['foro_threshold'] = dados['foro'].astype(str) + '_' + dados['threshold'].astype(str)
            
            # Variáveis dummy
            dados_encoded = pd.get_dummies(dados, columns=['foro', 'area'], prefix=['foro', 'area'])
            
            # Threshold como contínua e categórica
            dados_encoded['threshold_cont'] = dados_encoded['threshold']
            dados_encoded['threshold_quad'] = dados_encoded['threshold'] ** 2
            
            self.logger.info(f"Dados binomiais preparados: {len(dados_encoded)} observações")
            return dados_encoded
            
        except Exception as e:
            self.logger.error(f"Erro na preparação binomial: {e}")
            raise
    
    def ajustar_glm_binomial(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Ajusta GLM Binomial para TN/N_total
        
        Args:
            df: dados preparados
            
        Returns:
            Resultados do GLM
        """
        try:
            # Preparar variáveis
            y = df['TN']  # Sucessos (verdadeiros negativos)
            n_trials = df['N_total']  # Total de tentativas
            
            # Variáveis explicativas
            X_cols = [col for col in df.columns if 
                     col.startswith('foro_') or col.startswith('area_') or 
                     col in ['threshold_cont', 'threshold_quad']]
            X = df[X_cols]
            X = sm.add_constant(X)
            
            # Ajustar GLM Binomial
            modelo_glm = sm.GLM(y, X, family=families.Binomial(), var_weights=n_trials)
            resultado = modelo_glm.fit()
            
            self.modelo_glm = resultado
            
            # Extrair resultados
            resultados_dict = {
                'coeficientes': resultado.params.to_dict(),
                'p_valores': resultado.pvalues.to_dict(),
                'intervalo_confianca': resultado.conf_int().to_dict(),
                'deviance': resultado.deviance,
                'aic': resultado.aic,
                'bic': resultado.bic,
                'n_observacoes': len(y),
                'pseudor2': 1 - resultado.deviance / resultado.null_deviance
            }
            
            self.resultados = resultados_dict
            self.logger.info(f"GLM Binomial ajustado - AIC: {resultado.aic:.2f}, Pseudo-R²: {resultados_dict['pseudor2']:.3f}")
            
            return resultados_dict
            
        except Exception as e:
            self.logger.error(f"Erro no GLM Binomial: {e}")
            raise
    
    def prever_especificidade_binomial(self, foro: str, threshold: float, area: str = None) -> Dict[str, float]:
        """
        Prediz especificidade para combinação foro × threshold
        
        Args:
            foro: nome do foro
            threshold: valor do threshold (0-1)
            area: área jurídica (opcional)
            
        Returns:
            Dicionário com predição e intervalos
        """
        if self.modelo_glm is None:
            raise ValueError("Modelo GLM não foi ajustado")
        
        try:
            # Criar vetor de predição
            X_pred = pd.Series(0, index=self.modelo_glm.params.index)
            X_pred['const'] = 1
            X_pred['threshold_cont'] = threshold
            X_pred['threshold_quad'] = threshold ** 2
            
            # Ativar variáveis dummy
            foro_col = f'foro_{foro}'
            if foro_col in X_pred.index:
                X_pred[foro_col] = 1
            
            if area:
                area_col = f'area_{area}'
                if area_col in X_pred.index:
                    X_pred[area_col] = 1
            
            # Predição no espaço logito
            pred_logito = self.modelo_glm.predict(X_pred.values.reshape(1, -1))[0]
            
            # Converter para probabilidade
            especificidade_pred = 1 / (1 + np.exp(-pred_logito))
            
            # Intervalo de confiança (aproximado)
            se_pred = np.sqrt(X_pred.values @ self.modelo_glm.cov_params() @ X_pred.values)
            ic_lower_logito = pred_logito - 1.96 * se_pred
            ic_upper_logito = pred_logito + 1.96 * se_pred
            
            ic_lower = 1 / (1 + np.exp(-ic_lower_logito))
            ic_upper = 1 / (1 + np.exp(-ic_upper_logito))
            
            resultado = {
                'especificidade_predita': especificidade_pred,
                'ic_lower': ic_lower,
                'ic_upper': ic_upper,
                'pred_logito': pred_logito,
                'se_pred': se_pred
            }
            
            self.logger.info(f"Predição GLM: {foro} × {threshold:.2f} → Espec: {especificidade_pred:.3f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na predição GLM: {e}")
            raise

class ModeloBayesianoBivariado:
    """
    Metodologia 3: Modelo Bayesiano Bivariado (Sensibilidade × Especificidade)
    
    Modela sensibilidade e especificidade conjuntamente reconhecendo correlação.
    Usa distribuição Beta bivariada com efeitos aleatórios por foro/área/ano.
    
    Ideal para capturar trade-offs entre Sen/Spec e heterogeneidade entre contextos.
    """
    
    def __init__(self):
        self.modelo_bayes = None
        self.trace = None
        self.summary_stats = None
        self.logger = logging.getLogger('ModeloBayes')
        self.logger.info("Modelo Bayesiano Bivariado inicializado")
    
    def preparar_dados_bayes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Prepara dados para modelagem Bayesiana
        
        Args:
            df: DataFrame com [TP, TN, FP, FN, foro, area, ano]
            
        Returns:
            Dicionário com dados estruturados para PyMC
        """
        try:
            dados = df.copy()
            
            # Calcular sensibilidade e especificidade observadas
            dados['sensibilidade'] = dados['TP'] / (dados['TP'] + dados['FN'])
            dados['especificidade'] = dados['TN'] / (dados['TN'] + dados['FP'])
            
            # Remover NaN e infinitos
            dados = dados.dropna(subset=['sensibilidade', 'especificidade'])
            dados = dados[(dados['sensibilidade'].between(0, 1)) & 
                         (dados['especificidade'].between(0, 1))]
            
            # Codificar fatores categóricos
            foro_codes, foro_unique = pd.factorize(dados['foro'])
            area_codes, area_unique = pd.factorize(dados['area'])
            ano_codes, ano_unique = pd.factorize(dados['ano'])
            
            # Estrutura para PyMC
            dados_bayes = {
                'sensibilidade': dados['sensibilidade'].values,
                'especificidade': dados['especificidade'].values,
                'foro_idx': foro_codes,
                'area_idx': area_codes,
                'ano_idx': ano_codes,
                'n_foros': len(foro_unique),
                'n_areas': len(area_unique),
                'n_anos': len(ano_unique),
                'n_obs': len(dados),
                'foro_names': foro_unique,
                'area_names': area_unique,
                'ano_values': ano_unique,
                'TP': dados['TP'].values,
                'TN': dados['TN'].values,
                'FP': dados['FP'].values,
                'FN': dados['FN'].values
            }
            
            self.logger.info(f"Dados Bayesianos: {dados_bayes['n_obs']} obs, {dados_bayes['n_foros']} foros, {dados_bayes['n_areas']} áreas")
            return dados_bayes
            
        except Exception as e:
            self.logger.error(f"Erro na preparação Bayesiana: {e}")
            raise
    
    def ajustar_modelo_bayesiano_simplificado(self, dados_bayes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ajusta modelo Bayesiano simplificado (sem PyMC)
        Usa aproximação analítica com conjugação Beta-Binomial
        
        Args:
            dados_bayes: dados preparados
            
        Returns:
            Resultados do modelo Bayesiano aproximado
        """
        try:
            sens = dados_bayes['sensibilidade']
            spec = dados_bayes['especificidade']
            
            # Prior Beta(1,1) - uniforme
            alpha_prior = 1
            beta_prior = 1
            
            # Estatísticas por foro
            resultados_foro = {}
            
            for i, foro in enumerate(dados_bayes['foro_names']):
                mask = dados_bayes['foro_idx'] == i
                if np.sum(mask) == 0:
                    continue
                
                sens_foro = sens[mask]
                spec_foro = spec[mask]
                n_obs = len(sens_foro)
                
                # Momentos observados
                sens_media = np.mean(sens_foro)
                spec_media = np.mean(spec_foro)
                
                # Estimação de parâmetros Beta via método dos momentos
                def estimar_beta_params(media, var):
                    if var >= media * (1 - media) or var <= 0:
                        var = media * (1 - media) * 0.1  # Fallback
                    alpha = media * (media * (1 - media) / var - 1)
                    beta = (1 - media) * (media * (1 - media) / var - 1)
                    return max(alpha, 0.1), max(beta, 0.1)
                
                sens_var = np.var(sens_foro) if len(sens_foro) > 1 else sens_media * (1 - sens_media) * 0.1
                spec_var = np.var(spec_foro) if len(spec_foro) > 1 else spec_media * (1 - spec_media) * 0.1
                
                alpha_sens, beta_sens = estimar_beta_params(sens_media, sens_var)
                alpha_spec, beta_spec = estimar_beta_params(spec_media, spec_var)
                
                # Posterior Beta (conjugação)
                alpha_sens_post = alpha_prior + n_obs * sens_media
                beta_sens_post = beta_prior + n_obs * (1 - sens_media)
                alpha_spec_post = alpha_prior + n_obs * spec_media
                beta_spec_post = beta_prior + n_obs * (1 - spec_media)
                
                # Intervalos credíveis
                sens_ic = stats.beta.interval(0.95, alpha_sens_post, beta_sens_post)
                spec_ic = stats.beta.interval(0.95, alpha_spec_post, beta_spec_post)
                
                resultados_foro[foro] = {
                    'sensibilidade_posterior_media': alpha_sens_post / (alpha_sens_post + beta_sens_post),
                    'especificidade_posterior_media': alpha_spec_post / (alpha_spec_post + beta_spec_post),
                    'sensibilidade_ic': sens_ic,
                    'especificidade_ic': spec_ic,
                    'n_observacoes': n_obs,
                    'alpha_sens_post': alpha_sens_post,
                    'beta_sens_post': beta_sens_post,
                    'alpha_spec_post': alpha_spec_post,
                    'beta_spec_post': beta_spec_post
                }
            
            # Estatísticas globais
            sens_global = np.mean(sens)
            spec_global = np.mean(spec)
            corr_sens_spec = np.corrcoef(sens, spec)[0, 1] if len(sens) > 1 else 0
            
            resultado_global = {
                'resultados_por_foro': resultados_foro,
                'estatisticas_globais': {
                    'sensibilidade_media_global': sens_global,
                    'especificidade_media_global': spec_global,
                    'correlacao_sens_spec': corr_sens_spec,
                    'n_total_observacoes': len(sens)
                },
                'modelo_tipo': 'bayesiano_conjugado_beta'
            }
            
            self.summary_stats = resultado_global
            self.logger.info(f"Modelo Bayesiano ajustado: Sens={sens_global:.3f}, Spec={spec_global:.3f}, Corr={corr_sens_spec:.3f}")
            
            return resultado_global
            
        except Exception as e:
            self.logger.error(f"Erro no modelo Bayesiano: {e}")
            raise
    
    def prever_sens_spec_bayesiano(self, foro: str, n_sims: int = 1000) -> Dict[str, Any]:
        """
        Gera amostras posteriores de sensibilidade e especificidade
        
        Args:
            foro: nome do foro
            n_sims: número de simulações
            
        Returns:
            Amostras posteriores e estatísticas
        """
        if self.summary_stats is None:
            raise ValueError("Modelo Bayesiano não ajustado")
        
        try:
            foro_stats = self.summary_stats['resultados_por_foro'].get(foro)
            if foro_stats is None:
                # Usar estatísticas globais
                sens_media = self.summary_stats['estatisticas_globais']['sensibilidade_media_global']
                spec_media = self.summary_stats['estatisticas_globais']['especificidade_media_global']
                
                # Parâmetros padrão
                alpha_sens = beta_sens = 10  # Prior informativo
                alpha_spec = beta_spec = 10
            else:
                alpha_sens = foro_stats['alpha_sens_post']
                beta_sens = foro_stats['beta_sens_post']
                alpha_spec = foro_stats['alpha_spec_post']
                beta_spec = foro_stats['beta_spec_post']
            
            # Gerar amostras posteriores
            sens_samples = stats.beta.rvs(alpha_sens, beta_sens, size=n_sims)
            spec_samples = stats.beta.rvs(alpha_spec, beta_spec, size=n_sims)
            
            # Estatísticas das amostras
            resultado = {
                'sensibilidade_samples': sens_samples,
                'especificidade_samples': spec_samples,
                'sensibilidade_media': np.mean(sens_samples),
                'especificidade_media': np.mean(spec_samples),
                'sensibilidade_ic_95': np.percentile(sens_samples, [2.5, 97.5]),
                'especificidade_ic_95': np.percentile(spec_samples, [2.5, 97.5]),
                'correlacao_amostral': np.corrcoef(sens_samples, spec_samples)[0, 1]
            }
            
            self.logger.info(f"Simulação Bayesiana {foro}: Sens={resultado['sensibilidade_media']:.3f} ±{np.std(sens_samples):.3f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na predição Bayesiana: {e}")
            raise

class ModeloGenerativoScores:
    """
    Metodologia 4: Modelo Generativo via Scores
    
    Estima especificidade(t) e sensibilidade(t) diretamente das distribuições
    de scores contínuos dos classificadores.
    
    Gera curvas ROC/PR simuladas e encontra thresholds ótimos.
    """
    
    def __init__(self):
        self.scores_pos = None
        self.scores_neg = None
        self.distribuicoes = None
        self.thresholds_otimos = None
        self.logger = logging.getLogger('ModeloScores')
        self.logger.info("Modelo Generativo de Scores inicializado")
    
    def ajustar_distribuicoes_scores(self, scores_positivos: np.ndarray, scores_negativos: np.ndarray) -> Dict[str, Any]:
        """
        Ajusta distribuições estatísticas aos scores
        
        Args:
            scores_positivos: scores para classe positiva (alto risco)
            scores_negativos: scores para classe negativa (baixo risco)
            
        Returns:
            Parâmetros das distribuições ajustadas
        """
        try:
            self.scores_pos = scores_positivos
            self.scores_neg = scores_negativos
            
            # Testar múltiplas distribuições
            distribuicoes_teste = ['norm', 'beta', 'gamma', 'lognorm']
            
            resultado = {}
            
            for classe, scores in [('positivos', scores_positivos), ('negativos', scores_negativos)]:
                melhor_dist = None
                melhor_aic = np.inf
                melhor_params = None
                
                for dist_name in distribuicoes_teste:
                    try:
                        dist = getattr(stats, dist_name)
                        
                        # Ajustar distribuição
                        if dist_name == 'beta':
                            # Beta requer (0,1), normalizar se necessário
                            scores_norm = (scores - scores.min()) / (scores.max() - scores.min())
                            scores_norm = scores_norm * 0.998 + 0.001  # Evitar 0 e 1 exatos
                            params = dist.fit(scores_norm)
                            ll = np.sum(dist.logpdf(scores_norm, *params))
                        else:
                            params = dist.fit(scores)
                            ll = np.sum(dist.logpdf(scores, *params))
                        
                        # Calcular AIC
                        k = len(params)
                        aic = 2 * k - 2 * ll
                        
                        if aic < melhor_aic:
                            melhor_aic = aic
                            melhor_dist = dist_name
                            melhor_params = params
                            
                    except Exception:
                        continue
                
                resultado[classe] = {
                    'distribuicao': melhor_dist,
                    'parametros': melhor_params,
                    'aic': melhor_aic,
                    'n_scores': len(scores)
                }
            
            self.distribuicoes = resultado
            self.logger.info(f"Distribuições ajustadas: Pos={resultado['positivos']['distribuicao']}, Neg={resultado['negativos']['distribuicao']}")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro no ajuste de distribuições: {e}")
            raise
    
    def calcular_curvas_teoricas(self, thresholds: np.ndarray = None) -> Dict[str, np.ndarray]:
        """
        Calcula curvas ROC e PR teóricas baseadas nas distribuições
        
        Args:
            thresholds: array de thresholds para calcular (padrão: 100 pontos)
            
        Returns:
            Dicionário com FPR, TPR, Precision, Recall para cada threshold
        """
        if self.distribuicoes is None:
            raise ValueError("Distribuições não foram ajustadas")
        
        try:
            if thresholds is None:
                thresholds = np.linspace(0, 1, 100)
            
            # Obter distribuições
            dist_pos_name = self.distribuicoes['positivos']['distribuicao']
            dist_neg_name = self.distribuicoes['negativos']['distribuicao']
            params_pos = self.distribuicoes['positivos']['parametros']
            params_neg = self.distribuicoes['negativos']['parametros']
            
            dist_pos = getattr(stats, dist_pos_name)
            dist_neg = getattr(stats, dist_neg_name)
            
            tpr = []  # True Positive Rate (Sensibilidade)
            fpr = []  # False Positive Rate (1 - Especificidade)
            precision = []
            
            for t in thresholds:
                # TPR = P(Score > t | Positivo)
                tpr_t = 1 - dist_pos.cdf(t, *params_pos)
                
                # FPR = P(Score > t | Negativo)  
                fpr_t = 1 - dist_neg.cdf(t, *params_neg)
                
                # Precision = TPR * P(Pos) / (TPR * P(Pos) + FPR * P(Neg))
                # Assumindo P(Pos) = P(Neg) = 0.5
                if tpr_t + fpr_t > 0:
                    precision_t = tpr_t / (tpr_t + fpr_t)
                else:
                    precision_t = 1.0
                
                tpr.append(tpr_t)
                fpr.append(fpr_t)
                precision.append(precision_t)
            
            # Especificidade = 1 - FPR
            especificidade = 1 - np.array(fpr)
            
            resultado = {
                'thresholds': thresholds,
                'sensibilidade': np.array(tpr),
                'especificidade': especificidade,
                'fpr': np.array(fpr),
                'precision': np.array(precision),
                'auc_roc': auc(fpr, tpr),
                'auc_pr': auc(tpr, precision)
            }
            
            self.logger.info(f"Curvas teóricas calculadas: AUC-ROC={resultado['auc_roc']:.3f}, AUC-PR={resultado['auc_pr']:.3f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de curvas: {e}")
            raise
    
    def encontrar_threshold_otimo(self, criterio: str = 'youden') -> Dict[str, Any]:
        """
        Encontra threshold ótimo segundo diferentes critérios
        
        Args:
            criterio: 'youden', 'f1', 'especificidade_90', 'sensibilidade_90'
            
        Returns:
            Threshold ótimo e métricas associadas
        """
        try:
            curvas = self.calcular_curvas_teoricas()
            
            sens = curvas['sensibilidade']
            spec = curvas['especificidade']
            prec = curvas['precision']
            thresholds = curvas['thresholds']
            
            if criterio == 'youden':
                # Índice de Youden = Sensibilidade + Especificidade - 1
                youden_index = sens + spec - 1
                idx_otimo = np.argmax(youden_index)
                
            elif criterio == 'f1':
                # F1-Score = 2 * (Precision * Recall) / (Precision + Recall)
                f1_scores = 2 * (prec * sens) / (prec + sens + 1e-8)
                idx_otimo = np.argmax(f1_scores)
                
            elif criterio == 'especificidade_90':
                # Máxima sensibilidade com especificidade >= 0.90
                idx_validos = spec >= 0.90
                if np.sum(idx_validos) == 0:
                    idx_otimo = np.argmax(spec)
                else:
                    sens_validos = sens[idx_validos]
                    idx_otimo = np.where(idx_validos)[0][np.argmax(sens_validos)]
                    
            elif criterio == 'sensibilidade_90':
                # Máxima especificidade com sensibilidade >= 0.90
                idx_validos = sens >= 0.90
                if np.sum(idx_validos) == 0:
                    idx_otimo = np.argmax(sens)
                else:
                    spec_validos = spec[idx_validos]
                    idx_otimo = np.where(idx_validos)[0][np.argmax(spec_validos)]
            else:
                raise ValueError(f"Critério {criterio} não reconhecido")
            
            threshold_otimo = thresholds[idx_otimo]
            
            resultado = {
                'threshold_otimo': threshold_otimo,
                'sensibilidade': sens[idx_otimo],
                'especificidade': spec[idx_otimo],
                'precision': prec[idx_otimo],
                'criterio_usado': criterio,
                'indice_otimo': idx_otimo
            }
            
            # Adicionar métricas específicas do critério
            if criterio == 'youden':
                resultado['youden_index'] = sens[idx_otimo] + spec[idx_otimo] - 1
            elif criterio == 'f1':
                resultado['f1_score'] = 2 * (prec[idx_otimo] * sens[idx_otimo]) / (prec[idx_otimo] + sens[idx_otimo])
            
            self.thresholds_otimos = self.thresholds_otimos or {}
            self.thresholds_otimos[criterio] = resultado
            
            self.logger.info(f"Threshold ótimo ({criterio}): {threshold_otimo:.3f} → Sens={sens[idx_otimo]:.3f}, Spec={spec[idx_otimo]:.3f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro no threshold ótimo: {e}")
            raise
    
    def simular_scores_futuros(self, n_pos: int = 100, n_neg: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simula scores futuros baseado nas distribuições ajustadas
        
        Args:
            n_pos: número de amostras positivas
            n_neg: número de amostras negativas
            
        Returns:
            (scores_simulados, labels_verdadeiros, probs_preditas)
        """
        if self.distribuicoes is None:
            raise ValueError("Distribuições não ajustadas")
        
        try:
            # Obter parâmetros
            dist_pos_name = self.distribuicoes['positivos']['distribuicao']
            dist_neg_name = self.distribuicoes['negativos']['distribuicao']
            params_pos = self.distribuicoes['positivos']['parametros']
            params_neg = self.distribuicoes['negativos']['parametros']
            
            dist_pos = getattr(stats, dist_pos_name)
            dist_neg = getattr(stats, dist_neg_name)
            
            # Simular scores
            scores_pos_sim = dist_pos.rvs(*params_pos, size=n_pos)
            scores_neg_sim = dist_neg.rvs(*params_neg, size=n_neg)
            
            # Combinar
            scores_todos = np.concatenate([scores_pos_sim, scores_neg_sim])
            labels_todos = np.concatenate([np.ones(n_pos), np.zeros(n_neg)])
            
            # Probs como scores normalizados
            probs_todos = (scores_todos - scores_todos.min()) / (scores_todos.max() - scores_todos.min())
            
            self.logger.info(f"Simulação: {n_pos} pos, {n_neg} neg → Scores [{scores_todos.min():.3f}, {scores_todos.max():.3f}]")
            return scores_todos, labels_todos, probs_todos
            
        except Exception as e:
            self.logger.error(f"Erro na simulação: {e}")
            raise

# Função integradora das 4 metodologias
def executar_analise_completa_v2(dados_path: str = None) -> Dict[str, Any]:
    """
    Executa análise completa usando as 4 metodologias estatísticas
    
    Args:
        dados_path: caminho para dados (opcional, usa dados sintéticos se None)
        
    Returns:
        Resultados consolidados das 4 metodologias
    """
    logger.info("=== INICIANDO ANÁLISE META MODELO v2.0 ===")
    
    try:
        # 1. Preparar dados sintéticos se não fornecidos
        if dados_path is None:
            dados = gerar_dados_sinteticos_metodologias()
        else:
            dados = pd.read_csv(dados_path)
        
        resultados = {}
        
        # 2. METODOLOGIA 1: Regressão Beta
        logger.info("--- Executando Metodologia 1: Regressão Beta ---")
        beta_model = RegressaoBetaEspecificidade()
        dados_beta = beta_model.preparar_dados(dados['especificidade_data'])
        resultados['regressao_beta'] = beta_model.ajustar_modelo(dados_beta)
        resultados['impacto_covariaveis'] = beta_model.analisar_impacto_covariaveis()
        
        # 3. METODOLOGIA 2: GLM Binomial
        logger.info("--- Executando Metodologia 2: GLM Binomial ---")
        glm_model = GLMBinomialTN()
        dados_glm = glm_model.preparar_dados_binomial(dados['binomial_data'])
        resultados['glm_binomial'] = glm_model.ajustar_glm_binomial(dados_glm)
        
        # Exemplo de predição
        pred_exemplo = glm_model.prever_especificidade_binomial('São Paulo', 0.5, 'civil')
        resultados['predicao_exemplo_glm'] = pred_exemplo
        
        # 4. METODOLOGIA 3: Modelo Bayesiano
        logger.info("--- Executando Metodologia 3: Modelo Bayesiano Bivariado ---")
        bayes_model = ModeloBayesianoBivariado()
        dados_bayes = bayes_model.preparar_dados_bayes(dados['confusion_matrix_data'])
        resultados['modelo_bayesiano'] = bayes_model.ajustar_modelo_bayesiano_simplificado(dados_bayes)
        
        # Simulação Bayesiana
        sim_bayes = bayes_model.prever_sens_spec_bayesiano('São Paulo', n_sims=1000)
        resultados['simulacao_bayesiana'] = {
            'sensibilidade_media': sim_bayes['sensibilidade_media'],
            'especificidade_media': sim_bayes['especificidade_media'],
            'ic_sensibilidade': sim_bayes['sensibilidade_ic_95'].tolist(),
            'ic_especificidade': sim_bayes['especificidade_ic_95'].tolist()
        }
        
        # 5. METODOLOGIA 4: Modelo Generativo
        logger.info("--- Executando Metodologia 4: Modelo Generativo de Scores ---")
        scores_model = ModeloGenerativoScores()
        dist_result = scores_model.ajustar_distribuicoes_scores(
            dados['scores_data']['scores_positivos'],
            dados['scores_data']['scores_negativos']
        )
        resultados['distribuicoes_scores'] = dist_result
        
        # Curvas teóricas
        curvas = scores_model.calcular_curvas_teoricas()
        resultados['curvas_teoricas'] = {
            'auc_roc': curvas['auc_roc'],
            'auc_pr': curvas['auc_pr'],
            'n_thresholds': len(curvas['thresholds'])
        }
        
        # Thresholds ótimos
        for criterio in ['youden', 'f1', 'especificidade_90']:
            thresh_opt = scores_model.encontrar_threshold_otimo(criterio)
            resultados[f'threshold_otimo_{criterio}'] = thresh_opt
        
        # 6. Resumo geral
        resultados['resumo_analise'] = {
            'timestamp': datetime.now().isoformat(),
            'metodologias_executadas': 4,
            'n_observacoes_total': len(dados['especificidade_data']),
            'foros_analisados': dados['especificidade_data']['foro'].nunique(),
            'areas_analisadas': dados['especificidade_data']['area'].nunique(),
            'status': 'completo'
        }
        
        logger.info("=== ANÁLISE META MODELO v2.0 CONCLUÍDA ===")
        return resultados
        
    except Exception as e:
        logger.error(f"Erro na análise completa: {e}")
        raise

def gerar_dados_sinteticos_metodologias() -> Dict[str, pd.DataFrame]:
    """
    Gera dados sintéticos para demonstração das 4 metodologias
    """
    np.random.seed(42)
    
    foros = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Porto Alegre', 'Brasília']
    areas = ['civil', 'trabalhista', 'tributario', 'consumidor']
    anos = [2020, 2021, 2022, 2023, 2024, 2025]
    
    # Dados para Regressão Beta (especificidade observada)
    n_obs_beta = 200
    dados_beta = []
    
    for _ in range(n_obs_beta):
        foro = np.random.choice(foros)
        area = np.random.choice(areas)
        ano = np.random.choice(anos)
        valor_causa = np.random.lognormal(10, 1.5)
        
        # Especificidade simulada com efeitos
        base_spec = 0.75
        if foro in ['São Paulo', 'Rio de Janeiro']:
            base_spec += 0.05
        if area == 'tributario':
            base_spec += 0.08
        if ano >= 2023:
            base_spec -= 0.02
        
        especificidade = np.clip(np.random.beta(base_spec * 20, (1-base_spec) * 20), 0.1, 0.95)
        
        dados_beta.append({
            'especificidade': especificidade,
            'foro': foro,
            'area': area,
            'ano': ano,
            'valor_causa': valor_causa
        })
    
    # Dados para GLM Binomial (TN, FP por foro x threshold)
    dados_binomial = []
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
    
    for foro in foros:
        for area in areas:
            for thresh in thresholds:
                # Simular especificidade base
                spec_base = 0.8 - 0.15 * thresh + np.random.normal(0, 0.05)
                spec_base = np.clip(spec_base, 0.1, 0.95)
                
                n_neg = np.random.randint(50, 200)  # Total de negativos
                tn = np.random.binomial(n_neg, spec_base)  # Verdadeiros negativos
                fp = n_neg - tn  # Falsos positivos
                
                dados_binomial.append({
                    'TN': tn,
                    'FP': fp,
                    'foro': foro,
                    'area': area,
                    'threshold': thresh
                })
    
    # Dados para Modelo Bayesiano (matriz de confusão)
    dados_confusion = []
    
    for foro in foros:
        for area in areas:
            for ano in anos:
                # Simular performance com variação
                base_sens = 0.75 + np.random.normal(0, 0.1)
                base_spec = 0.80 + np.random.normal(0, 0.1)
                
                base_sens = np.clip(base_sens, 0.4, 0.95)
                base_spec = np.clip(base_spec, 0.4, 0.95)
                
                n_pos = np.random.randint(30, 100)
                n_neg = np.random.randint(40, 120)
                
                tp = np.random.binomial(n_pos, base_sens)
                fn = n_pos - tp
                tn = np.random.binomial(n_neg, base_spec)
                fp = n_neg - tn
                
                dados_confusion.append({
                    'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn,
                    'foro': foro, 'area': area, 'ano': ano
                })
    
    # Dados para Modelo Generativo (scores)
    n_pos = 500
    n_neg = 700
    
    # Scores positivos (distribuição mais alta)
    scores_pos = np.random.beta(3, 2, n_pos)  # Enviesada para valores altos
    
    # Scores negativos (distribuição mais baixa) 
    scores_neg = np.random.beta(2, 4, n_neg)  # Enviesada para valores baixos
    
    return {
        'especificidade_data': pd.DataFrame(dados_beta),
        'binomial_data': pd.DataFrame(dados_binomial), 
        'confusion_matrix_data': pd.DataFrame(dados_confusion),
        'scores_data': {
            'scores_positivos': scores_pos,
            'scores_negativos': scores_neg
        }
    }

# Sistema de Análise de Viés e Recomendações
class AnalisadorVies:
    """
    Sistema para análise de viés por grupos demográficos/contextuais
    Verifica se especificidade varia injustificadamente entre grupos
    """
    
    def __init__(self):
        self.resultados_vies = None
        self.logger = logging.getLogger('AnalisadorVies')
        
    def analisar_vies_por_grupo(self, df: pd.DataFrame, grupos: List[str] = ['foro', 'area', 'valor_causa_faixa']) -> Dict[str, Any]:
        """
        Análise de viés por grupos específicos
        
        Args:
            df: DataFrame com especificidade e covariáveis
            grupos: lista de colunas para agrupar
            
        Returns:
            Relatório de equidade e alertas de viés
        """
        try:
            resultados = {}
            alertas_vies = []
            
            for grupo in grupos:
                if grupo not in df.columns:
                    continue
                    
                # Calcular especificidade por grupo
                stats_grupo = df.groupby(grupo)['especificidade'].agg([
                    'mean', 'std', 'count', 'min', 'max'
                ]).round(4)
                
                # Teste de diferenças significativas (ANOVA)
                grupos_vals = [group['especificidade'].values for name, group in df.groupby(grupo)]
                try:
                    f_stat, p_valor = stats.f_oneway(*grupos_vals)
                except:
                    f_stat, p_valor = np.nan, np.nan
                
                # Calcular coeficiente de variação
                cv = stats_grupo['std'] / stats_grupo['mean']
                
                resultados[grupo] = {
                    'estatisticas': stats_grupo.to_dict(),
                    'teste_anova': {'f_statistic': f_stat, 'p_valor': p_valor},
                    'coeficiente_variacao': cv.to_dict(),
                    'diferenca_max_min': stats_grupo['max'].max() - stats_grupo['min'].min()
                }
                
                # Alertas de viés
                if p_valor < 0.05:
                    alertas_vies.append({
                        'grupo': grupo,
                        'tipo': 'diferenca_significativa',
                        'p_valor': p_valor,
                        'descricao': f'Diferenças significativas de especificidade entre {grupo}'
                    })
                
                if resultados[grupo]['diferenca_max_min'] > 0.15:
                    alertas_vies.append({
                        'grupo': grupo,
                        'tipo': 'diferenca_alta',
                        'diferenca': resultados[grupo]['diferenca_max_min'],
                        'descricao': f'Grande variação na especificidade entre {grupo}'
                    })
            
            self.resultados_vies = {
                'analise_por_grupo': resultados,
                'alertas_vies': alertas_vies,
                'n_grupos_analisados': len(resultados),
                'n_alertas': len(alertas_vies)
            }
            
            self.logger.info(f"Análise de viés concluída: {len(resultados)} grupos, {len(alertas_vies)} alertas")
            return self.resultados_vies
            
        except Exception as e:
            self.logger.error(f"Erro na análise de viés: {e}")
            raise

class RecomendadorEstrategias:
    """
    Sistema integrado de recomendação de estratégias de defesa
    Combina resultados das 4 metodologias para recomendações ótimas
    """
    
    def __init__(self):
        self.modelo_estrategias = None
        self.logger = logging.getLogger('RecomendadorEstrategias')
        
    def treinar_modelo_estrategias(self, df_estrategias: pd.DataFrame) -> Dict[str, Any]:
        """
        Treina modelo para recomendação de estratégias
        
        Args:
            df_estrategias: DataFrame com [estrategia, foro, area, impacto_especificidade, vitoria]
            
        Returns:
            Modelo treinado e métricas
        """
        try:
            # Preparar dados
            dados = df_estrategias.copy()
            
            # Codificar variáveis categóricas
            dados_encoded = pd.get_dummies(dados, columns=['foro', 'area', 'estrategia'])
            
            # Variável resposta: impacto na especificidade
            y = dados_encoded['impacto_especificidade']
            X = dados_encoded.drop(['impacto_especificidade', 'vitoria'], axis=1)
            
            # Modelo simples: Regressão Linear
            X_const = sm.add_constant(X)
            modelo = sm.OLS(y, X_const).fit()
            
            self.modelo_estrategias = {
                'modelo_fitted': modelo,
                'colunas_X': X.columns.tolist(),
                'estatisticas': {
                    'r_quadrado': modelo.rsquared,
                    'r_quadrado_adj': modelo.rsquared_adj,
                    'f_statistic': modelo.fvalue,
                    'p_valor_f': modelo.f_pvalue
                }
            }
            
            self.logger.info(f"Modelo de estratégias treinado: R²={modelo.rsquared:.3f}")
            return self.modelo_estrategias
            
        except Exception as e:
            self.logger.error(f"Erro no treino de estratégias: {e}")
            raise
    
    def recomendar_estrategia_otima(self, caso: Dict[str, Any], estrategias_disponiveis: List[str] = None) -> Dict[str, Any]:
        """
        Recomenda estratégia ótima para um caso específico
        
        Args:
            caso: dicionário com características do caso {'foro': ..., 'area': ...}
            estrategias_disponiveis: lista de estratégias possíveis
            
        Returns:
            Recomendação com estratégia, impacto esperado, e confiança
        """
        if self.modelo_estrategias is None:
            raise ValueError("Modelo de estratégias não foi treinado")
        
        try:
            if estrategias_disponiveis is None:
                estrategias_disponiveis = [
                    'contestacao_merito', 'questao_processual', 'acordo_judicial',
                    'prescricao', 'incompetencia', 'arguicao_nulidade'
                ]
            
            recomendacoes = []
            
            for estrategia in estrategias_disponiveis:
                # Criar vetor de predição
                caso_encoded = {col: 0 for col in self.modelo_estrategias['colunas_X']}
                
                # Ativar características do caso
                if f"foro_{caso.get('foro')}" in caso_encoded:
                    caso_encoded[f"foro_{caso.get('foro')}"] = 1
                if f"area_{caso.get('area')}" in caso_encoded:
                    caso_encoded[f"area_{caso.get('area')}"] = 1
                if f"estrategia_{estrategia}" in caso_encoded:
                    caso_encoded[f"estrategia_{estrategia}"] = 1
                
                # Predizer impacto
                X_pred = pd.Series(caso_encoded)[self.modelo_estrategias['colunas_X']]
                X_pred_const = sm.add_constant(X_pred)
                
                impacto_pred = self.modelo_estrategias['modelo_fitted'].predict(X_pred_const.values.reshape(1, -1))[0]
                
                # Intervalo de confiança
                pred_summary = self.modelo_estrategias['modelo_fitted'].get_prediction(X_pred_const.values.reshape(1, -1))
                ic_lower, ic_upper = pred_summary.conf_int()[0]
                
                recomendacoes.append({
                    'estrategia': estrategia,
                    'impacto_especificidade_esperado': impacto_pred,
                    'intervalo_confianca': [ic_lower, ic_upper],
                    'confianca': 1 - (ic_upper - ic_lower) / 2  # Métrica simples
                })
            
            # Ordenar por impacto esperado
            recomendacoes = sorted(recomendacoes, key=lambda x: x['impacto_especificidade_esperado'], reverse=True)
            
            resultado = {
                'estrategia_recomendada': recomendacoes[0]['estrategia'],
                'impacto_esperado': recomendacoes[0]['impacto_especificidade_esperado'],
                'confianca_recomendacao': recomendacoes[0]['confianca'],
                'todas_recomendacoes': recomendacoes,
                'caso_analisado': caso
            }
            
            self.logger.info(f"Recomendação: {resultado['estrategia_recomendada']} (impacto: {resultado['impacto_esperado']:.3f})")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na recomendação: {e}")
            raise

if __name__ == "__main__":
    # Exemplo de uso das metodologias
    print("=== DEMONSTRAÇÃO META MODELO v2.0 ===")
    
    try:
        # Executar análise completa
        resultados = executar_analise_completa_v2()
        
        print(f"✅ Análise concluída com sucesso!")
        print(f"📊 Metodologias executadas: {resultados['resumo_analise']['metodologias_executadas']}")
        print(f"🎯 AUC-ROC: {resultados['curvas_teoricas']['auc_roc']:.3f}")
        print(f"⚖️ Threshold ótimo (Youden): {resultados['threshold_otimo_youden']['threshold_otimo']:.3f}")
        
        # Análise de viés
        analisador = AnalisadorVies()
        dados_sinteticos = gerar_dados_sinteticos_metodologias()
        vies_resultado = analisador.analisar_vies_por_grupo(dados_sinteticos['especificidade_data'])
        print(f"🚨 Alertas de viés detectados: {vies_resultado['n_alertas']}")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")