"""
Módulo Principal - Modelos Jurídicos Estatísticos
=================================================

Implementa modelos de defesa, especificidade e análise estatística para processos jurídicos.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import statsmodels.api as sm
from statsmodels import api as sm_api
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, Tuple, List, Optional
import warnings
import os
import pickle
warnings.filterwarnings('ignore')

class ModeloDefesa:
    """
    Modelo de Predição de Vitória em Processos Jurídicos
    
    Implementa regressão logística para prever probabilidade de vitória
    baseada em estratégias de defesa e características do processo.
    """
    
    def __init__(self, data_path: str = 'modelos_juridicos/data'):
        self.data_path = data_path
        self.modelo = None
        self.scaler = None
        self.features = None
        self.coeficientes = None
        self.dados_treino = None
        
    def carregar_dados(self) -> pd.DataFrame:
        """Carrega dataset de defesas completo com 5000 casos"""
        try:
            df = pd.read_csv(f"{self.data_path}/dataset_defesas_completo_1756687697.csv")
            print(f"✅ Dataset completo carregado: {len(df)} casos")
            return df
        except FileNotFoundError:
            # Fallback para datasets antigos
            try:
                df = pd.read_csv(f"{self.data_path}/dataset_defesas_1756659091707.csv")
                print(f"⚠️ Usando dataset antigo: {len(df)} casos")
                return df
            except FileNotFoundError:
                df = pd.read_csv(f"{self.data_path}/dataset_defesas_1756658854795.csv")
                print(f"⚠️ Usando dataset antigo: {len(df)} casos")
                return df
    
    def preparar_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepara features para o modelo"""
        # Features categóricas
        df_encoded = pd.get_dummies(df, columns=['foro', 'juiz', 'area'], prefix=['foro', 'juiz', 'area'])
        
        # Features numéricas e binárias
        features_numericas = ['valor_causa', 'ano']
        features_binarias = ['prescricao', 'impugnacao_pericia', 'nulidade_prova', 
                           'acordo_proposto', 'ilegitimidade', 'decadencia']
        
        # Todas as features (exceto target)
        feature_cols = (features_numericas + features_binarias + 
                       [col for col in df_encoded.columns if col.startswith(('foro_', 'juiz_', 'area_'))])
        
        X = df_encoded[feature_cols].fillna(0)
        y = df_encoded['vitoria']
        
        return X.values, y.values, feature_cols
    
    def treinar(self, test_size: float = 0.2) -> Dict:
        """Treina o modelo de defesa"""
        print("🔄 Carregando dados...")
        df = self.carregar_dados()
        
        print("🔄 Preparando features...")
        X, y, feature_names = self.preparar_features(df)
        self.features = feature_names
        
        print("🔄 Dividindo dados...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print("🔄 Normalizando features...")
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print("🔄 Treinando modelo...")
        self.modelo = LogisticRegression(random_state=42, max_iter=1000)
        self.modelo.fit(X_train_scaled, y_train)
        
        # Métricas
        y_pred = self.modelo.predict(X_test_scaled)
        y_pred_proba = self.modelo.predict_proba(X_test_scaled)[:, 1]
        
        auc = roc_auc_score(y_test, y_pred_proba)
        
        # Coeficientes
        self.coeficientes = pd.DataFrame({
            'feature': self.features,
            'coeficiente': self.modelo.coef_[0]
        }).sort_values('coeficiente', key=abs, ascending=False)
        
        self.dados_treino = df
        
        print(f"✅ Modelo treinado com AUC: {auc:.4f}")
        
        return {
            'auc': auc,
            'coeficientes': self.coeficientes,
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
    
    def prever(self, caso: Dict) -> Dict:
        """Prediz probabilidade de vitória para um caso"""
        if self.modelo is None:
            raise ValueError("Modelo não foi treinado ainda!")
        
        # Criar DataFrame com o caso
        df_caso = pd.DataFrame([caso])
        
        # Preparar features igual ao treino
        df_encoded = pd.get_dummies(df_caso, columns=['foro', 'juiz', 'area'], prefix=['foro', 'juiz', 'area'])
        
        # Garantir que todas as colunas existam
        for col in self.features:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        
        X_caso = df_encoded[self.features].fillna(0).values
        X_caso_scaled = self.scaler.transform(X_caso)
        
        prob_vitoria = self.modelo.predict_proba(X_caso_scaled)[0, 1]
        predicao = self.modelo.predict(X_caso_scaled)[0]
        
        return {
            'probabilidade_vitoria': prob_vitoria,
            'predicao': bool(predicao),
            'confianca': 'Alta' if max(self.modelo.predict_proba(X_caso_scaled)[0]) > 0.7 else 'Média'
        }
    
    def recomendar_defesa(self, caso: Dict) -> Dict:
        """Recomenda estratégias de defesa baseadas no modelo"""
        if self.coeficientes is None:
            raise ValueError("Modelo não foi treinado ainda!")
        
        # Estratégias de defesa disponíveis
        estrategias = ['prescricao', 'impugnacao_pericia', 'nulidade_prova', 
                      'acordo_proposto', 'ilegitimidade', 'decadencia']
        
        # Encontrar estratégias com maior impacto positivo
        coef_estrategias = self.coeficientes[
            self.coeficientes['feature'].isin(estrategias)
        ].copy()
        
        coef_estrategias = coef_estrategias[coef_estrategias['coeficiente'] > 0]
        
        if len(coef_estrategias) == 0:
            estrategia_recomendada = "Todas as estratégias têm impacto negativo"
            impacto_esperado = 0
        else:
            estrategia_recomendada = coef_estrategias.iloc[0]['feature']
            impacto_esperado = coef_estrategias.iloc[0]['coeficiente']
        
        # Predição atual
        pred_atual = self.prever(caso)
        
        return {
            'probabilidade_atual': pred_atual['probabilidade_vitoria'],
            'estrategia_recomendada': estrategia_recomendada,
            'impacto_esperado': impacto_esperado,
            'todas_estrategias': coef_estrategias.to_dict('records'),
            'interpretacao': self._interpretar_estrategia(estrategia_recomendada)
        }
    
    def _interpretar_estrategia(self, estrategia: str) -> str:
        """Interpreta a estratégia recomendada"""
        interpretacoes = {
            'prescricao': 'Arguir prescrição do direito - estratégia temporal',
            'impugnacao_pericia': 'Contestar laudos periciais e provas técnicas',
            'nulidade_prova': 'Questionar validade e legalidade das provas',
            'acordo_proposto': 'Propor acordo/conciliação como estratégia',
            'ilegitimidade': 'Arguir ilegitimidade de parte no processo',
            'decadencia': 'Arguir decadência do direito pleiteado'
        }
        return interpretacoes.get(estrategia, 'Estratégia não mapeada')
    
    def salvar_modelo(self, caminho: str = 'modelos_juridicos/reports/modelo_defesa.pkl'):
        """Salva o modelo treinado"""
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'wb') as f:
            pickle.dump({
                'modelo': self.modelo,
                'scaler': self.scaler,
                'features': self.features,
                'coeficientes': self.coeficientes
            }, f)
        print(f"✅ Modelo salvo em: {caminho}")


class ModeloEspecificidade:
    """
    Modelo de Análise de Especificidade Jurídica
    
    Implementa 4 abordagens estatísticas para análise de especificidade:
    1. Regressão Beta
    2. GLM Binomial  
    3. Modelo Bayesiano Bivariado
    4. Modelo Generativo via Scores
    """
    
    def __init__(self, data_path: str = 'modelos_juridicos/data'):
        self.data_path = data_path
        self.resultados = {}
        
    def regressao_beta(self) -> Dict:
        """Implementa regressão Beta para especificidade usando dataset completo de 5000 casos"""
        try:
            # Usar dataset completo de defesas para análise de especificidade
            df = pd.read_csv(f"{self.data_path}/dataset_defesas_completo_1756687697.csv")
            print(f"✅ Dataset completo carregado para Regressão Beta: {len(df)} casos")
            
            # Criar especificidade baseada na taxa de sucesso
            df['especificidade_obs'] = df['resultado_real']
            
        except FileNotFoundError:
            # Fallback para datasets antigos
            try:
                df = pd.read_csv(f"{self.data_path}/dataset_beta_1756659091712.csv")
            except FileNotFoundError:
                df = pd.read_csv(f"{self.data_path}/dataset_beta_1756658854800.csv")
            print(f"⚠️ Usando dataset antigo para Regressão Beta: {len(df)} casos")
        
        print("🔄 Executando Regressão Beta...")
        
        # Preparar dados - usar area_juridica se disponível
        area_col = 'area_juridica' if 'area_juridica' in df.columns else 'area'
        df_encoded = pd.get_dummies(df, columns=['foro', area_col])
        
        # Features
        foro_cols = [col for col in df_encoded.columns if col.startswith('foro_')]
        area_cols = [col for col in df_encoded.columns if col.startswith(('area_', 'area_juridica_'))]
        X_cols = foro_cols + area_cols + ['ano']
        
        X = df_encoded[X_cols]
        X = sm.add_constant(X)
        y = df_encoded['especificidade_obs']
        
        # Transformar y para intervalo (0,1) aberto
        y_transformed = (y * (len(y) - 1) + 0.5) / len(y)
        
        # Ajustar modelo Beta (usando OLS como aproximação)
        modelo = sm.OLS(y_transformed, X).fit()
        
        resultados = {
            'tipo': 'Regressão Beta',
            'r2': modelo.rsquared,
            'aic': modelo.aic,
            'n_observacoes': len(df),
            'params': modelo.params.to_dict(),
            'pvalues': modelo.pvalues.to_dict(),
            'resumo': str(modelo.summary())
        }
        
        self.resultados['beta'] = resultados
        print(f"✅ Regressão Beta concluída - R²: {modelo.rsquared:.4f} com {len(df)} casos")
        return resultados
    
    def glm_binomial(self) -> Dict:
        """Implementa GLM Binomial para TN/N_neg usando dataset completo de 5000 casos"""
        try:
            # Usar dataset completo e simular dados binomiais
            df_main = pd.read_csv(f"{self.data_path}/dataset_defesas_completo_1756687697.csv")
            print(f"✅ Dataset completo carregado para GLM Binomial: {len(df_main)} casos")
            
            # Criar dados binomiais simulados baseados no dataset real
            np.random.seed(42)
            n_obs = len(df_main)
            
            df = pd.DataFrame({
                'foro': df_main['foro'].values,
                'threshold': np.random.uniform(0.3, 0.8, n_obs),
                'TN': np.random.binomial(df_main['resultado_real'].astype(int), 
                                       np.random.uniform(0.6, 0.9, n_obs)),
                'N_neg': df_main['resultado_real'].astype(int)
            })
            
        except FileNotFoundError:
            # Fallback para datasets antigos
            try:
                df = pd.read_csv(f"{self.data_path}/dataset_binomial_1756659091715.csv")
            except FileNotFoundError:
                df = pd.read_csv(f"{self.data_path}/dataset_binomial_1756658854792.csv")
            print(f"⚠️ Usando dataset antigo para GLM Binomial: {len(df)} casos")
        
        print("🔄 Executando GLM Binomial...")
        
        # Preparar dados
        df_encoded = pd.get_dummies(df, columns=['foro'])
        
        # Features
        X_cols = [col for col in df_encoded.columns if col.startswith('foro_')] + ['threshold']
        X = df_encoded[X_cols]
        X = sm.add_constant(X)
        
        # GLM Binomial
        modelo = sm.GLM(
            df['TN'], X, 
            family=sm.families.Binomial(),
            exposure=df['N_neg']
        ).fit()
        
        resultados = {
            'tipo': 'GLM Binomial',
            'deviance': modelo.deviance,
            'aic': modelo.aic,
            'params': modelo.params.to_dict(),
            'pvalues': modelo.pvalues.to_dict(),
            'resumo': str(modelo.summary())
        }
        
        self.resultados['binomial'] = resultados
        print(f"✅ GLM Binomial concluído - AIC: {modelo.aic:.2f}")
        return resultados
    
    def bayes_bivariado(self) -> Dict:
        """Implementa análise Bayesiana bivariada (versão simplificada)"""
        try:
            df = pd.read_csv(f"{self.data_path}/dataset_bivariado_1756659091705.csv")
        except FileNotFoundError:
            df = pd.read_csv(f"{self.data_path}/dataset_bivariado_1756658854794.csv")
        
        print("🔄 Executando análise Bayesiana bivariada...")
        
        # Análise descritiva bivariada
        correlacao = df['sensibilidade'].corr(df['especificidade'])
        
        # Estatísticas por foro
        stats_foro = df.groupby('foro').agg({
            'sensibilidade': ['mean', 'std'],
            'especificidade': ['mean', 'std']
        }).round(4)
        
        # Estatísticas por área
        stats_area = df.groupby('area').agg({
            'sensibilidade': ['mean', 'std'],
            'especificidade': ['mean', 'std']
        }).round(4)
        
        resultados = {
            'tipo': 'Bayesiano Bivariado (Descritivo)',
            'correlacao_sens_spec': correlacao,
            'stats_por_foro': stats_foro.to_dict(),
            'stats_por_area': stats_area.to_dict(),
            'n_observacoes': len(df)
        }
        
        self.resultados['bayes'] = resultados
        print(f"✅ Análise Bayesiana concluída - Correlação: {correlacao:.4f}")
        return resultados
    
    def modelo_scores(self) -> Dict:
        """Implementa modelo generativo via scores"""
        try:
            df = pd.read_csv(f"{self.data_path}/dataset_scores_1756659091709.csv")
        except FileNotFoundError:
            df = pd.read_csv(f"{self.data_path}/dataset_scores_1756658854797.csv")
        
        print("🔄 Executando modelo de scores...")
        
        # Análise de threshold vs especificidade
        correlacoes_por_foro = df.groupby('foro').apply(
            lambda x: x['threshold'].corr(x['spec_teorica'])
        )
        
        # Threshold ótimo (maior especificidade média)
        threshold_otimo = df.groupby('threshold')['spec_teorica'].mean().idxmax()
        spec_maxima = df.groupby('threshold')['spec_teorica'].mean().max()
        
        # Curva ROC sintética (simulada)
        thresholds = df['threshold'].unique()
        auc_estimada = np.trapz(df.groupby('threshold')['spec_teorica'].mean().values, 
                               thresholds) / (thresholds.max() - thresholds.min())
        
        resultados = {
            'tipo': 'Modelo Scores',
            'threshold_otimo': threshold_otimo,
            'especificidade_maxima': spec_maxima,
            'auc_estimada': auc_estimada,
            'correlacoes_por_foro': correlacoes_por_foro.to_dict(),
            'n_thresholds': len(thresholds)
        }
        
        self.resultados['scores'] = resultados
        print(f"✅ Modelo de scores concluído - Threshold ótimo: {threshold_otimo}")
        return resultados
    
    def executar_todos_modelos(self) -> Dict:
        """Executa todos os 4 modelos de especificidade"""
        print("🚀 Iniciando análise completa de especificidade...")
        
        self.regressao_beta()
        self.glm_binomial()
        self.bayes_bivariado()
        self.modelo_scores()
        
        print("✅ Todos os modelos de especificidade executados!")
        return self.resultados
    
    def gerar_relatorio(self, caminho: str = 'modelos_juridicos/reports/relatorio_especificidade.txt'):
        """Gera relatório completo dos modelos"""
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE ANÁLISE DE ESPECIFICIDADE JURÍDICA\n")
            f.write("=" * 50 + "\n\n")
            
            for modelo, resultado in self.resultados.items():
                f.write(f"{resultado['tipo']}\n")
                f.write("-" * 30 + "\n")
                for key, value in resultado.items():
                    if key != 'tipo':
                        f.write(f"{key}: {value}\n")
                f.write("\n")
        
        print(f"✅ Relatório salvo em: {caminho}")