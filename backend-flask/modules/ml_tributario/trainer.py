"""
Trainer para modelos ML Tributário
Script para treinar e salvar modelos
"""
import os
import joblib
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json

from .dataset_builder import TributarioDatasetBuilder, check_data_availability
from .models import get_model, XGBOOST_AVAILABLE
from main import db
from models_processos import MLModeloTributario

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Diretório para salvar modelos
MODELS_DIR = os.path.join(os.path.dirname(__file__), '../../ml_models/tributario')
os.makedirs(MODELS_DIR, exist_ok=True)


class TributarioTrainer:
    """
    Trainer para modelos ML tributários
    """
    
    def __init__(self):
        self.dataset_builder = TributarioDatasetBuilder()
        self.model = None
        self.model_type = None
        self.metrics = {}
        self.features_used = []
        
    def check_data_readiness(self) -> Dict[str, Any]:
        """Verifica se há dados suficientes para treinar"""
        availability = check_data_availability()
        
        ready = availability['com_contingencia_definida'] >= 50
        
        logger.info(f"Dados disponíveis: {availability}")
        logger.info(f"Pronto para treinar: {ready}")
        
        return {
            'ready': ready,
            **availability
        }
    
    def train_baseline(self, alpha: float = 1.0) -> Dict[str, Any]:
        """
        Treina modelo baseline Ridge
        
        Args:
            alpha: Parâmetro de regularização
            
        Returns:
            Dict com métricas
        """
        logger.info("=" * 60)
        logger.info("TREINANDO MODELO BASELINE - RIDGE REGRESSOR")
        logger.info("=" * 60)
        
        # 1. Construir dataset
        df = self.dataset_builder.build_dataset(min_samples=30)
        if df is None:
            raise ValueError("Dados insuficientes para treinar baseline")
        
        # 2. Split train/test
        train_df, test_df = self.dataset_builder.split_train_test(test_size=0.2)
        
        X_train, y_train = self.dataset_builder.get_X_y_regression(train_df)
        X_test, y_test = self.dataset_builder.get_X_y_regression(test_df)
        
        logger.info(f"Train: {X_train.shape}, Test: {X_test.shape}")
        
        # 3. Treinar modelo
        self.model = get_model('ridge', alpha=alpha)
        self.model_type = 'ridge'
        
        train_metrics = self.model.train(X_train, y_train)
        test_metrics = self.model.evaluate(X_test, y_test)
        
        # 4. Salvar métricas
        self.metrics = {
            **train_metrics,
            **test_metrics,
            'total_amostras_treino': len(train_df),
            'total_amostras_teste': len(test_df)
        }
        
        self.features_used = list(X_train.columns)
        
        logger.info("=" * 60)
        logger.info(f"BASELINE CONCLUÍDO - R²: {test_metrics['r2_score']:.4f}")
        logger.info("=" * 60)
        
        return self.metrics
    
    def train_xgboost(
        self,
        hyperparameter_tuning: bool = False,
        n_estimators: int = 200
    ) -> Dict[str, Any]:
        """
        Treina modelo XGBoost Regressor
        
        Args:
            hyperparameter_tuning: Se True, executa Grid Search
            n_estimators: Número de árvores
            
        Returns:
            Dict com métricas
        """
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost não instalado")
        
        logger.info("=" * 60)
        logger.info("TREINANDO MODELO XGBOOST REGRESSOR")
        logger.info("=" * 60)
        
        # 1. Construir dataset
        df = self.dataset_builder.build_dataset(min_samples=100)
        if df is None:
            raise ValueError("Dados insuficientes para XGBoost (mín 100)")
        
        # 2. Split train/validation/test
        train_df, test_df = self.dataset_builder.split_train_test(test_size=0.2)
        
        # Separar validation do train
        from sklearn.model_selection import train_test_split
        train_df, val_df = train_test_split(train_df, test_size=0.2, random_state=42)
        
        X_train, y_train = self.dataset_builder.get_X_y_regression(train_df)
        X_val, y_val = self.dataset_builder.get_X_y_regression(val_df)
        X_test, y_test = self.dataset_builder.get_X_y_regression(test_df)
        
        logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        # 3. Criar modelo
        self.model = get_model('xgboost_regressor', n_estimators=n_estimators)
        self.model_type = 'xgboost_regressor'
        
        # 4. Hyperparameter tuning (opcional)
        if hyperparameter_tuning:
            logger.info("Executando Grid Search...")
            param_grid = {
                'max_depth': [4, 6, 8],
                'learning_rate': [0.01, 0.05, 0.1],
                'subsample': [0.7, 0.8, 0.9],
                'colsample_bytree': [0.7, 0.8, 0.9]
            }
            tuning_results = self.model.hyperparameter_tuning(X_train, y_train, param_grid, cv=3)
            logger.info(f"Melhores parâmetros: {tuning_results['best_params']}")
        
        # 5. Treinar
        train_metrics = self.model.train(X_train, y_train, X_val, y_val, early_stopping_rounds=20)
        test_metrics = self.model.evaluate(X_test, y_test)
        
        # 6. Salvar métricas
        self.metrics = {
            **train_metrics,
            **test_metrics,
            'total_amostras_treino': len(train_df),
            'total_amostras_teste': len(test_df)
        }
        
        self.features_used = list(X_train.columns)
        
        logger.info("=" * 60)
        logger.info(f"XGBOOST CONCLUÍDO - R²: {test_metrics['r2_score']:.4f}")
        logger.info("=" * 60)
        
        return self.metrics
    
    def save_model(self, version: Optional[str] = None) -> str:
        """
        Salva modelo treinado em arquivo e registra no DB
        
        Args:
            version: Versão semântica (ex: v1.0.0). Se None, auto-incrementa
            
        Returns:
            Path do arquivo salvo
        """
        if self.model is None:
            raise ValueError("Nenhum modelo treinado")
        
        # 1. Gerar versão se não fornecida
        if version is None:
            # Buscar última versão
            ultimo = MLModeloTributario.query.filter_by(
                tipo='regressao',
                ativo=True
            ).order_by(MLModeloTributario.id_modelo.desc()).first()
            
            if ultimo:
                # Incrementar versão
                last_ver = ultimo.versao  # ex: v1.2.3
                major, minor, patch = map(int, last_ver[1:].split('.'))
                version = f"v{major}.{minor}.{patch + 1}"
            else:
                version = "v1.0.0"
        
        # 2. Salvar arquivo .pkl
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.model_type}_{version}_{timestamp}.pkl"
        filepath = os.path.join(MODELS_DIR, filename)
        
        joblib.dump(self.model, filepath)
        logger.info(f"Modelo salvo em: {filepath}")
        
        # 3. Registrar no banco
        modelo_db = MLModeloTributario(
            versao=version,
            algoritmo=self.model_type,
            tipo='regressao',
            data_treinamento=datetime.now(),
            total_amostras_treino=self.metrics.get('total_amostras_treino'),
            total_amostras_teste=self.metrics.get('total_amostras_teste'),
            r2_score=self.metrics.get('r2_score'),
            mae=self.metrics.get('mae'),
            rmse=self.metrics.get('rmse'),
            hiperparametros=self.model.model.get_params() if hasattr(self.model.model, 'get_params') else {},
            features_utilizadas=self.features_used,
            path_arquivo=filepath,
            ativo=True
        )
        
        db.session.add(modelo_db)
        db.session.commit()
        
        logger.info(f"Modelo registrado no DB - ID: {modelo_db.id_modelo}, Versão: {version}")
        
        return filepath
    
    def train_and_save(
        self,
        model_type: str = 'ridge',
        version: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Pipeline completo: treinar + salvar
        
        Args:
            model_type: 'ridge' ou 'xgboost'
            version: Versão do modelo
            **kwargs: Parâmetros para treinamento
            
        Returns:
            Dict com métricas e path
        """
        # Treinar
        if model_type == 'ridge':
            metrics = self.train_baseline(**kwargs)
        elif model_type == 'xgboost':
            metrics = self.train_xgboost(**kwargs)
        else:
            raise ValueError(f"Tipo inválido: {model_type}")
        
        # Salvar
        model_path = self.save_model(version)
        
        return {
            **metrics,
            'model_path': model_path,
            'model_type': model_type
        }


# Script CLI
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Treinar modelos ML Tributário')
    parser.add_argument('--model', choices=['ridge', 'xgboost'], default='ridge',
                        help='Tipo de modelo')
    parser.add_argument('--version', type=str, help='Versão do modelo (ex: v1.0.0)')
    parser.add_argument('--tune', action='store_true', help='Hyperparameter tuning')
    
    args = parser.parse_args()
    
    trainer = TributarioTrainer()
    
    # Verificar dados
    readiness = trainer.check_data_readiness()
    if not readiness['ready']:
        logger.error(f"Dados insuficientes: {readiness}")
        exit(1)
    
    # Treinar e salvar
    result = trainer.train_and_save(
        model_type=args.model,
        version=args.version,
        hyperparameter_tuning=args.tune if args.model == 'xgboost' else False
    )
    
    print("\n" + "=" * 60)
    print("TREINAMENTO CONCLUÍDO")
    print("=" * 60)
    print(f"Modelo: {result['model_type']}")
    print(f"R² Score: {result['r2_score']:.4f}")
    print(f"MAE: R$ {result['mae']:.2f}")
    print(f"RMSE: R$ {result['rmse']:.2f}")
    print(f"Path: {result['model_path']}")
    print("=" * 60)
