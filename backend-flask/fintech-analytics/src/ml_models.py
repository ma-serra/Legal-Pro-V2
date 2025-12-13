"""
MODELOS PREDITIVOS FINTECH - 3 MODELOS OBRIGATÓRIOS
======================================================

Baseado na estrutura existente de jurimetria/services/machine_learning.py
Implementa os 3 modelos conforme prompt_replit_preditivo.md:
1. Predição de Resultado de Casos
2. Forecasting Temporal  
3. Sistema de Alertas Preditivos
"""

import pandas as pd
import numpy as np
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import joblib
import os

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    xgb = None
    XGB_AVAILABLE = False

# Time Series
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    Prophet = None
    PROPHET_AVAILABLE = False

# Visualização
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class FintechMLService:
    """
    Serviço completo de Machine Learning para análise preditiva Fintech
    Baseado na estrutura existente do sistema jurimetria
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_metrics = {}
        self.feature_importance = {}
        
        # Configurações
        self.random_state = 42
        self.test_size = 0.2
        
        # Diretórios
        self.models_dir = "fintech-analytics/models/trained_models"
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Dados carregados
        self.df = None
        self.training_data = {}
        
        logger.info("🤖 FintechMLService inicializado")
    
    def load_data(self, csv_path: str) -> bool:
        """Carrega dataset processado com tratamento robusto de encoding"""
        try:
            # Tentar carregar diretamente com pandas primeiro
            try:
                self.df = pd.read_csv(csv_path, encoding='utf-8')
                print(f"✅ Dataset carregado (UTF-8): {len(self.df)} registros")
                return True
            except UnicodeDecodeError:
                # Tentar com encoding latin-1
                self.df = pd.read_csv(csv_path, encoding='latin-1')
                print(f"✅ Dataset carregado (Latin-1): {len(self.df)} registros")
                return True
            except Exception:
                # Fallback para função original
                from .data_processor import carregar_dataset_fintech
                self.df = carregar_dataset_fintech(csv_path)
                print(f"✅ Dataset carregado (Função original): {len(self.df)} registros")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    # =====================================
    # MODELO 1: PREDIÇÃO DE RESULTADO DE CASOS
    # =====================================
    
    def prepare_case_prediction_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara features para predição de resultado de casos
        Target: grau_favorabilidade (1-5) ou resultado (Favorável/Desfavorável/Neutro)
        """
        print("🔧 Preparando features para predição de casos...")
        
        # Features selecionadas conforme especificação
        feature_columns = ['estado', 'regiao', 'orgao', 'instancia', 'banco_emissor', 
                          'codigo_causa', 'periodo_covid', 'ano', 'mes', 'trimestre']
        
        # Filtrar colunas disponíveis
        available_features = [col for col in feature_columns if col in df.columns]
        
        X = df[available_features].copy()
        y = df['grau_favorabilidade'].copy()
        
        # Encoding de variáveis categóricas
        categorical_columns = X.select_dtypes(include=['category', 'object']).columns
        
        for col in categorical_columns:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                X[col] = self.encoders[col].fit_transform(X[col].astype(str))
            else:
                X[col] = self.encoders[col].transform(X[col].astype(str))
        
        # Tratar valores nulos
        X = X.fillna(X.median())
        y = y.fillna(3)  # Score neutro por padrão
        
        print(f"✅ Features preparadas: {X.shape[1]} features, {len(X)} amostras")
        return X, y
    
    def train_case_outcome_predictor(self) -> Dict[str, Any]:
        """
        Treina modelo de predição de resultado de casos
        Algoritmos: RandomForest, XGBoost, Logistic Regression
        """
        print("🎯 Treinando modelo de predição de casos...")
        
        if self.df is None:
            raise ValueError("Dataset não carregado. Use load_data() primeiro.")
        
        # Preparar dados
        X, y = self.prepare_case_prediction_features(self.df)
        
        # Split treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        
        # Normalizar features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Modelos para testar
        models_to_test = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=self.random_state),
            'XGBoost': xgb.XGBClassifier(random_state=self.random_state),
            'LogisticRegression': LogisticRegression(random_state=self.random_state, max_iter=1000)
        }
        
        best_model = None
        best_score = 0
        results = {}
        
        # Testar cada modelo
        for name, model in models_to_test.items():
            print(f"  Testando {name}...")
            
            # Treinar
            if name == 'LogisticRegression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Métricas
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'predictions': y_pred
            }
            
            print(f"    Accuracy: {accuracy:.3f}")
            
            # Selecionar melhor modelo
            if accuracy > best_score:
                best_score = accuracy
                best_model = name
        
        # Salvar melhor modelo
        self.models['case_predictor'] = results[best_model]['model']
        self.scalers['case_predictor'] = scaler
        self.model_metrics['case_predictor'] = results[best_model]
        
        # Feature importance (para RandomForest e XGBoost)
        if best_model in ['RandomForest', 'XGBoost']:
            feature_names = X.columns.tolist()
            importance = results[best_model]['model'].feature_importances_
            self.feature_importance['case_predictor'] = dict(zip(feature_names, importance))
        
        # Salvar modelo
        model_path = os.path.join(self.models_dir, 'case_predictor.joblib')
        joblib.dump({
            'model': self.models['case_predictor'],
            'scaler': scaler,
            'encoders': self.encoders,
            'feature_names': X.columns.tolist()
        }, model_path)
        
        print(f"✅ Melhor modelo: {best_model} (Accuracy: {best_score:.3f})")
        print(f"💾 Modelo salvo em: {model_path}")
        
        return {
            'best_model': best_model,
            'accuracy': best_score,
            'all_results': results,
            'feature_importance': self.feature_importance.get('case_predictor', {})
        }
    
    def predict_case_outcome(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prediz resultado de um novo caso
        """
        if 'case_predictor' not in self.models:
            raise ValueError("Modelo de predição não treinado")
        
        # Preparar input
        input_df = pd.DataFrame([case_data])
        
        # Aplicar encodings
        for col in input_df.columns:
            if col in self.encoders:
                try:
                    input_df[col] = self.encoders[col].transform(input_df[col].astype(str))
                except:
                    input_df[col] = 0  # Default para valores não vistos
        
        # Predição
        model = self.models['case_predictor']
        prediction = model.predict(input_df)[0]
        
        # Probabilidades (se disponível)
        probabilities = {}
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(input_df)[0]
            classes = model.classes_
            probabilities = dict(zip(classes, proba))
        
        # Interpretação
        score_interpretation = {
            1: "Muito Desfavorável",
            2: "Desfavorável", 
            3: "Neutro",
            4: "Favorável",
            5: "Muito Favorável"
        }
        
        return {
            'score_favorabilidade': int(prediction),
            'interpretacao': score_interpretation.get(int(prediction), "Neutro"),
            'probabilidades': probabilities,
            'confianca': max(probabilities.values()) if probabilities else 0.5
        }
    
    # =====================================
    # MODELO 2: FORECASTING TEMPORAL
    # =====================================
    
    def prepare_time_series_data(self) -> pd.DataFrame:
        """
        Prepara dados de série temporal para forecasting
        """
        print("📈 Preparando dados de série temporal...")
        
        if self.df is None:
            raise ValueError("Dataset não carregado")
        
        # Agrupar por período e calcular taxa de sucesso
        ts_data = self.df.groupby(['ano', 'mes']).agg({
            'resultado': ['count', lambda x: (x == 'Favorável').mean() * 100]
        }).reset_index()
        
        # Flatten column names
        ts_data.columns = ['ano', 'mes', 'total_casos', 'taxa_sucesso']
        
        # Criar data
        ts_data['data'] = pd.to_datetime(ts_data[['ano', 'mes']])
        ts_data = ts_data.sort_values('data').reset_index(drop=True)
        
        print(f"✅ Série temporal preparada: {len(ts_data)} períodos")
        return ts_data
    
    def train_temporal_forecaster(self, periods_ahead: int = 12) -> Dict[str, Any]:
        """
        Treina modelo de forecasting temporal
        Algoritmos: ARIMA, Prophet (se disponível)
        """
        print("📊 Treinando modelo de forecasting temporal...")
        
        ts_data = self.prepare_time_series_data()
        
        results = {}
        
        # 1. ARIMA Model
        try:
            print("  Treinando modelo ARIMA...")
            
            ts_series = ts_data.set_index('data')['taxa_sucesso']
            
            # Auto ARIMA (simplified)
            model_arima = ARIMA(ts_series, order=(1, 1, 1))
            fitted_arima = model_arima.fit()
            
            # Forecast
            forecast_arima = fitted_arima.forecast(steps=periods_ahead)
            conf_int = fitted_arima.get_forecast(steps=periods_ahead).conf_int()
            
            # Criar datas futuras
            last_date = ts_series.index[-1]
            future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                       periods=periods_ahead, freq='MS')
            
            results['arima'] = {
                'model': fitted_arima,
                'forecast': forecast_arima.values,
                'dates': future_dates,
                'confidence_lower': conf_int.iloc[:, 0].values,
                'confidence_upper': conf_int.iloc[:, 1].values,
                'aic': fitted_arima.aic
            }
            
            print(f"    ARIMA AIC: {fitted_arima.aic:.2f}")
            
        except Exception as e:
            print(f"    Erro ARIMA: {e}")
            results['arima'] = None
        
        # 2. Prophet Model (se disponível)
        if Prophet is not None:
            try:
                print("  Treinando modelo Prophet...")
                
                # Preparar dados para Prophet
                prophet_data = ts_data[['data', 'taxa_sucesso']].copy()
                prophet_data.columns = ['ds', 'y']
                
                # Treinar modelo
                model_prophet = Prophet(yearly_seasonality=True, weekly_seasonality=False)
                model_prophet.fit(prophet_data)
                
                # Forecast
                future = model_prophet.make_future_dataframe(periods=periods_ahead, freq='MS')
                forecast_prophet = model_prophet.predict(future)
                
                # Extrair previsões futuras
                future_forecast = forecast_prophet.tail(periods_ahead)
                
                results['prophet'] = {
                    'model': model_prophet,
                    'forecast': future_forecast['yhat'].values,
                    'dates': future_forecast['ds'].values,
                    'confidence_lower': future_forecast['yhat_lower'].values,
                    'confidence_upper': future_forecast['yhat_upper'].values,
                    'full_forecast': forecast_prophet
                }
                
                print("    Prophet treinado com sucesso")
                
            except Exception as e:
                print(f"    Erro Prophet: {e}")
                results['prophet'] = None
        
        # Selecionar melhor modelo
        best_model = 'arima' if results.get('arima') else 'prophet'
        if results.get('prophet') and results.get('arima'):
            # Usar Prophet como padrão se ambos funcionaram
            best_model = 'prophet'
        
        # Salvar modelo
        self.models['forecaster'] = results[best_model]
        self.training_data['time_series'] = ts_data
        
        # Salvar no disco
        forecast_path = os.path.join(self.models_dir, 'temporal_forecaster.joblib')
        joblib.dump({
            'model': results[best_model],
            'training_data': ts_data,
            'best_model_type': best_model
        }, forecast_path)
        
        print(f"✅ Melhor modelo: {best_model.upper()}")
        print(f"💾 Modelo salvo em: {forecast_path}")
        
        return {
            'best_model': best_model,
            'results': results,
            'forecast_periods': periods_ahead
        }
    
    def generate_forecast(self, periods: int = 12) -> Dict[str, Any]:
        """
        Gera previsão para próximos períodos
        """
        if 'forecaster' not in self.models:
            raise ValueError("Modelo de forecasting não treinado")
        
        forecast_data = self.models['forecaster']
        
        return {
            'dates': forecast_data['dates'][:periods],
            'forecast': forecast_data['forecast'][:periods],
            'confidence_lower': forecast_data['confidence_lower'][:periods],
            'confidence_upper': forecast_data['confidence_upper'][:periods],
            'current_trend': forecast_data['forecast'][0] - self.training_data['time_series']['taxa_sucesso'].iloc[-1]
        }
    
    # =====================================
    # MODELO 3: SISTEMA DE ALERTAS
    # =====================================
    
    def train_alert_system(self) -> Dict[str, Any]:
        """
        Treina sistema de alertas preditivos
        Algoritmos: Isolation Forest, Statistical Control Charts
        """
        print("🚨 Treinando sistema de alertas...")
        
        if self.df is None:
            raise ValueError("Dataset não carregado")
        
        # 1. Preparar métricas para monitoramento
        alert_metrics = self._calculate_alert_metrics()
        
        # 2. Treinar modelos de detecção de anomalias
        anomaly_models = {}
        
        # Isolation Forest por estado
        print("  Treinando Isolation Forest por estado...")
        for estado in self.df['estado'].unique():
            if pd.isna(estado):
                continue
                
            estado_data = alert_metrics[alert_metrics['estado'] == estado]
            if len(estado_data) < 5:  # Mínimo de dados
                continue
            
            # Features para anomalia
            features = ['taxa_sucesso', 'volume_casos', 'casos_complexos']
            X = estado_data[features].fillna(estado_data[features].median())
            
            # Treinar Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=self.random_state)
            anomaly_scores = iso_forest.fit_predict(X)
            
            anomaly_models[estado] = {
                'model': iso_forest,
                'features': features,
                'baseline_metrics': X.mean().to_dict()
            }
        
        # 3. Estabelecer thresholds estatísticos
        statistical_thresholds = self._calculate_statistical_thresholds(alert_metrics)
        
        # Salvar sistema de alertas
        self.models['alert_system'] = {
            'anomaly_models': anomaly_models,
            'statistical_thresholds': statistical_thresholds,
            'baseline_metrics': alert_metrics
        }
        
        # Salvar no disco
        alert_path = os.path.join(self.models_dir, 'alert_system.joblib')
        joblib.dump(self.models['alert_system'], alert_path)
        
        print(f"✅ Sistema de alertas treinado para {len(anomaly_models)} estados")
        print(f"💾 Sistema salvo em: {alert_path}")
        
        return {
            'states_covered': len(anomaly_models),
            'thresholds': statistical_thresholds,
            'baseline_date': datetime.now().isoformat()
        }
    
    def _calculate_alert_metrics(self) -> pd.DataFrame:
        """Calcula métricas para sistema de alertas"""
        
        # Agrupar por estado e período
        alert_data = self.df.groupby(['estado', 'ano', 'mes']).agg({
            'resultado': [
                'count',
                lambda x: (x == 'Favorável').mean() * 100,
                lambda x: (x == 'Desfavorável').mean() * 100
            ],
            'grau_favorabilidade': 'mean',
            'codigo_causa': 'nunique'
        }).reset_index()
        
        # Flatten columns
        alert_data.columns = [
            'estado', 'ano', 'mes', 'volume_casos', 'taxa_sucesso', 
            'taxa_insucesso', 'favorabilidade_media', 'casos_complexos'
        ]
        
        # Criar data
        alert_data['data'] = pd.to_datetime(alert_data[['ano', 'mes']])
        
        return alert_data
    
    def _calculate_statistical_thresholds(self, metrics_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calcula thresholds estatísticos para alertas"""
        
        thresholds = {}
        
        for estado in metrics_df['estado'].unique():
            if pd.isna(estado):
                continue
                
            estado_data = metrics_df[metrics_df['estado'] == estado]
            
            if len(estado_data) < 3:
                continue
            
            # Calcular thresholds (média ± 2 desvios padrão)
            thresholds[estado] = {}
            
            for metric in ['taxa_sucesso', 'volume_casos', 'favorabilidade_media']:
                values = estado_data[metric].dropna()
                if len(values) > 0:
                    mean_val = values.mean()
                    std_val = values.std()
                    
                    thresholds[estado][metric] = {
                        'lower_bound': mean_val - 2 * std_val,
                        'upper_bound': mean_val + 2 * std_val,
                        'mean': mean_val,
                        'std': std_val
                    }
        
        return thresholds
    
    def check_alerts(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Verifica alertas baseado em métricas atual
        """
        if 'alert_system' not in self.models:
            raise ValueError("Sistema de alertas não treinado")
        
        alerts = []
        alert_system = self.models['alert_system']
        
        estado = current_metrics.get('estado')
        if not estado or estado not in alert_system['statistical_thresholds']:
            return alerts
        
        thresholds = alert_system['statistical_thresholds'][estado]
        
        # Verificar cada métrica
        for metric, threshold_data in thresholds.items():
            current_value = current_metrics.get(metric)
            if current_value is None:
                continue
            
            # Verificar se está fora dos bounds
            if current_value < threshold_data['lower_bound']:
                severity = 'Alta' if current_value < threshold_data['lower_bound'] * 0.8 else 'Média'
                alerts.append({
                    'tipo': 'Queda de Performance',
                    'metrica': metric,
                    'valor_atual': current_value,
                    'valor_esperado': threshold_data['mean'],
                    'desvio': abs(current_value - threshold_data['mean']) / threshold_data['std'],
                    'severidade': severity,
                    'estado': estado,
                    'timestamp': datetime.now().isoformat()
                })
            
            elif current_value > threshold_data['upper_bound']:
                severity = 'Baixa'  # Valores altos geralmente são bons
                alerts.append({
                    'tipo': 'Performance Excepcional',
                    'metrica': metric,
                    'valor_atual': current_value,
                    'valor_esperado': threshold_data['mean'],
                    'desvio': abs(current_value - threshold_data['mean']) / threshold_data['std'],
                    'severidade': severity,
                    'estado': estado,
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts
    
    # =====================================
    # UTILITÁRIOS E VALIDAÇÃO
    # =====================================
    
    def validate_all_models(self) -> Dict[str, Any]:
        """
        Valida todos os modelos treinados
        """
        validation_results = {}
        
        # Validar modelo de predição de casos
        if 'case_predictor' in self.models:
            metrics = self.model_metrics.get('case_predictor', {})
            validation_results['case_predictor'] = {
                'status': 'OK' if metrics.get('accuracy', 0) > 0.85 else 'BAIXA_PERFORMANCE',
                'accuracy': metrics.get('accuracy', 0),
                'required_accuracy': 0.85
            }
        
        # Validar forecaster
        if 'forecaster' in self.models:
            validation_results['forecaster'] = {
                'status': 'OK',
                'periods_available': 12
            }
        
        # Validar sistema de alertas
        if 'alert_system' in self.models:
            alert_system = self.models['alert_system']
            validation_results['alert_system'] = {
                'status': 'OK',
                'states_covered': len(alert_system['anomaly_models']),
                'thresholds_defined': len(alert_system['statistical_thresholds'])
            }
        
        return validation_results
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo de todos os modelos
        """
        summary = {
            'models_trained': list(self.models.keys()),
            'total_models': len(self.models),
            'data_loaded': self.df is not None,
            'data_size': len(self.df) if self.df is not None else 0
        }
        
        if self.model_metrics:
            summary['performance_metrics'] = self.model_metrics
        
        if self.feature_importance:
            summary['feature_importance'] = self.feature_importance
        
        return summary

# Função de conveniência para carregar modelos salvos
def load_trained_models(models_dir: str = "fintech-analytics/models/trained_models") -> FintechMLService:
    """
    Carrega modelos já treinados
    """
    service = FintechMLService()
    
    # Carregar cada modelo
    model_files = {
        'case_predictor': 'case_predictor.joblib',
        'forecaster': 'temporal_forecaster.joblib', 
        'alert_system': 'alert_system.joblib'
    }
    
    for model_name, filename in model_files.items():
        filepath = os.path.join(models_dir, filename)
        if os.path.exists(filepath):
            try:
                model_data = joblib.load(filepath)
                service.models[model_name] = model_data
                print(f"✅ {model_name} carregado")
            except Exception as e:
                print(f"❌ Erro ao carregar {model_name}: {e}")
    
    return service