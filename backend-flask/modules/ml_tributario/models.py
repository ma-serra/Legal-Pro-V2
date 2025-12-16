"""
Models ML Tributário
Define modelos de Machine Learning para processos tributários
"""
import numpy as np
from typing import Dict, Any, Tuple
import logging

# Sklearn models
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

# XGBoost
try:
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost não instalado. Usando baseline apenas.")

logger = logging.getLogger(__name__)


class BaselineRidgeModel:
    """
    Modelo baseline para regressão usando Ridge
    Simples, rápido, bom para início
    """
    
    def __init__(self, alpha: float = 1.0):
        self.model = Ridge(alpha=alpha)
        self.is_trained = False
        
    def train(self, X_train, y_train, **kwargs) -> Dict[str, float]:
        """
        Treina modelo Ridge
        
        Returns:
            Dict com métricas
        """
        logger.info("Treinando modelo Ridge...")
        
        # Treinar
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Métricas treinamento
        y_pred_train = self.model.predict(X_train)
        r2_train = r2_score(y_train, y_pred_train)
        mae_train = mean_absolute_error(y_train, y_pred_train)
        rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
        
        logger.info(f"Ridge treinado - R²: {r2_train:.4f}, MAE: {mae_train:.2f}")
        
        return {
            'r2_train': r2_train,
            'mae_train': mae_train,
            'rmse_train': rmse_train
        }
    
    def evaluate(self, X_test, y_test) -> Dict[str, float]:
        """Avalia modelo no conjunto de teste"""
        if not self.is_trained:
            raise ValueError("Modelo não treinado")
        
        y_pred = self.model.predict(X_test)
        
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        logger.info(f"Ridge test - R²: {r2:.4f}, MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        
        return {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse
        }
    
    def predict(self, X) -> np.ndarray:
        """Prediz valores"""
        if not self.is_trained:
            raise ValueError("Modelo não treinado")
        return self.model.predict(X)
    
    def get_feature_importance(self) -> np.ndarray:
        """Retorna coeficientes (importância de features)"""
        return self.model.coef_


class XGBoostRegressorModel:
    """
    Modelo XGBoost para regressão (predição de valor contingência)
    Alta precisão, moderadamente rápido
    """
    
    def __init__(self, **params):
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost não disponível")
        
        # Hiperparâmetros padrão otimizados
        default_params = {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.05,
            'reg_lambda': 1.0,
            'random_state': 42,
            'n_jobs': -1
        }
        default_params.update(params)
        
        self.model = XGBRegressor(**default_params)
        self.is_trained = False
        self.best_params = None
        
    def train(
        self,
        X_train,
        y_train,
        X_val=None,
        y_val=None,
        early_stopping_rounds: int = 20
    ) -> Dict[str, float]:
        """
        Treina modelo XGBoost
        
        Args:
            X_train, y_train: Dados treino
            X_val, y_val: Dados validação (opcional)
            early_stopping_rounds: Paradas antecipadas
            
        Returns:
            Dict com métricas
        """
        logger.info("Treinando modelo XGBoost Regressor...")
        
        # Treinar com validação
        if X_val is not None and y_val is not None:
            eval_set = [(X_train, y_train), (X_val, y_val)]
            self.model.fit(
                X_train, y_train,
                eval_set=eval_set,
                early_stopping_rounds=early_stopping_rounds,
                verbose=False
            )
        else:
            self.model.fit(X_train, y_train)
        
        self.is_trained = True
        
        # Métricas treinamento
        y_pred_train = self.model.predict(X_train)
        r2_train = r2_score(y_train, y_pred_train)
        mae_train = mean_absolute_error(y_train, y_pred_train)
        rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
        
        logger.info(f"XGBoost treinado - R²: {r2_train:.4f}, MAE: {mae_train:.2f}")
        
        return {
            'r2_train': r2_train,
            'mae_train': mae_train,
            'rmse_train': rmse_train
        }
    
    def hyperparameter_tuning(
        self,
        X_train,
        y_train,
        param_grid: Dict[str, list],
        cv: int = 3
    ) -> Dict[str, Any]:
        """
        Otimização de hiperparâmetros via GridSearch
        
        Args:
            X_train, y_train: Dados treino
            param_grid: Grid de parâmetros
            cv: Folds para cross-validation
            
        Returns:
            Dict com melhores parâmetros e score
        """
        logger.info("Iniciando Grid Search para XGBoost...")
        
        grid_search = GridSearchCV(
            estimator=self.model,
            param_grid=param_grid,
            cv=cv,
            scoring='r2',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        self.best_params = grid_search.best_params_
        self.model = grid_search.best_estimator_
        self.is_trained = True
        
        logger.info(f"Melhores parâmetros: {self.best_params}")
        logger.info(f"Melhor R² (CV): {grid_search.best_score_:.4f}")
        
        return {
            'best_params': self.best_params,
            'best_score': grid_search.best_score_,
            'cv_results': grid_search.cv_results_
        }
    
    def evaluate(self, X_test, y_test) -> Dict[str, float]:
        """Avalia modelo no conjunto de teste"""
        if not self.is_trained:
            raise ValueError("Modelo não treinado")
        
        y_pred = self.model.predict(X_test)
        
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        logger.info(f"XGBoost test - R²: {r2:.4f}, MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        
        return {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse
        }
    
    def predict(self, X) -> np.ndarray:
        """Prediz valores"""
        if not self.is_trained:
            raise ValueError("Modelo não treinado")
        return self.model.predict(X)
    
    def get_feature_importance(self) -> np.ndarray:
        """Retorna importância de features"""
        return self.model.feature_importances_


class XGBoostClassifierModel:
    """
    Modelo XGBoost para classificação (risco: Alto/Médio/Baixo)
    """
    
    def __init__(self, **params):
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost não disponível")
        
        default_params = {
            'n_estimators': 150,
            'max_depth': 5,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.05,
            'reg_lambda': 1.0,
            'random_state': 42,
            'n_jobs': -1,
            'objective': 'multi:softprob',  # Multi-classe
            'num_class': 3  # Baixo, Médio, Alto
        }
        default_params.update(params)
        
        self.model = XGBClassifier(**default_params)
        self.is_trained = False
        
    def train(self, X_train, y_train, **kwargs) -> Dict[str, float]:
        """Treina modelo XGBoost Classifier"""
        logger.info("Treinando modelo XGBoost Classifier...")
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Métricas treinamento
        y_pred_train = self.model.predict(X_train)
        accuracy_train = accuracy_score(y_train, y_pred_train)
        
        logger.info(f"XGBoost Classifier treinado - Accuracy: {accuracy_train:.4f}")
        
        return {
            'accuracy_train': accuracy_train
        }
    
    def evaluate(self, X_test, y_test) -> Dict[str, float]:
        """Avalia modelo no conjunto de teste"""
        if not self.is_trained:
            raise ValueError("Modelo não treinado")
        
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='weighted'
        )
        
        # AUC ROC (multi-classe)
        try:
            auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
        except:
            auc = 0.0
        
        logger.info(f"XGBoost Classifier test - Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc_roc': auc
        }
    
    def predict(self, X) -> np.ndarray:
        """Prediz classes"""
        if not self.is_trained:
            raise ValueError("Modelo não treinado")
        return self.model.predict(X)
    
    def predict_proba(self, X) -> np.ndarray:
        """Prediz probabilidades"""
        if not self.is_trained:
            raise ValueError("Modelo não treinado")
        return self.model.predict_proba(X)
    
    def get_feature_importance(self) -> np.ndarray:
        """Retorna importância de features"""
        return self.model.feature_importances_


# Mapeamento de modelos disponíveis
AVAILABLE_MODELS = {
    'ridge': BaselineRidgeModel,
}

if XGBOOST_AVAILABLE:
    AVAILABLE_MODELS['xgboost_regressor'] = XGBoostRegressorModel
    AVAILABLE_MODELS['xgboost_classifier'] = XGBoostClassifierModel


def get_model(model_name: str, **params):
    """
    Factory para criar modelos
    
    Args:
        model_name: 'ridge', 'xgboost_regressor', 'xgboost_classifier'
        **params: Hiperparâmetros
        
    Returns:
        Instância do modelo
    """
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Modelo '{model_name}' não disponível. Opções: {list(AVAILABLE_MODELS.keys())}")
    
    return AVAILABLE_MODELS[model_name](**params)
