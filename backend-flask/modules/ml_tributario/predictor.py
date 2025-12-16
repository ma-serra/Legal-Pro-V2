"""
Predictor Service para ML Tributário
Serviço de predição em produção
"""
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import logging
import os

from flask import current_app
from flask_sqlalchemy import SQLAlchemy

# Não importar db diretamente - usar current_app
from models_processos import (
    Processo,
    ProcessoTributario,
    MLModeloTributario,
    MLPredicaoTributario
)
from .dataset_builder import TributarioDatasetBuilder

logger = logging.getLogger(__name__)

# Cache de modelo carregado
_MODEL_CACHE = {}


class TributarioPredictor:
    """
    Serviço de predição para processos tributários
    """
    
    def __init__(self, versao_modelo: Optional[str] = None):
        """
        Inicializa predictor
        
        Args:
            versao_modelo: Versão específica ou None para usar modelo ativo
        """
        self.modelo_db = self._load_modelo_db(versao_modelo)
        self.modelo = self._load_modelo_file()
        self.dataset_builder = TributarioDatasetBuilder()
        
    def _load_modelo_db(self, versao: Optional[str]) -> MLModeloTributario:
        """Carrega registro do modelo do DB"""
        if versao:
            modelo = MLModeloTributario.query.filter_by(
                versao=versao,
                ativo=True
            ).first()
        else:
            # Pegar modelo ativo mais recente
            modelo = MLModeloTributario.query.filter_by(
                tipo='regressao',
                ativo=True
            ).order_by(MLModeloTributario.id_modelo.desc()).first()
        
        if not modelo:
            raise ValueError(f"Modelo não encontrado: {versao or 'ativo'}")
        
        logger.info(f"Usando modelo: {modelo.versao} (R²: {modelo.r2_score})")
        
        return modelo
    
    def _load_modelo_file(self):
        """Carrega modelo do arquivo .pkl"""
        path = self.modelo_db.path_arquivo
        
        # Verificar cache
        if path in _MODEL_CACHE:
            logger.debug(f"Modelo carregado do cache: {path}")
            return _MODEL_CACHE[path]
        
        # Carregar do disco
        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo modelo não encontrado: {path}")
        
        modelo = joblib.load(path)
        _MODEL_CACHE[path] = modelo
        
        logger.info(f"Modelo carregado do disco: {path}")
        
        return modelo
    
    def predict_processo(
        self,
        processo_id: int,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Prediz valor contingência para um processo
        
        Args:
            processo_id: ID do processo
            save_to_db: Se True, salva predição no banco
            
        Returns:
            Dict com predição e confiança
        """
        # 1. Buscar processo
        processo = Processo.query.get(processo_id)
        if not processo:
            raise ValueError(f"Processo {processo_id} não encontrado")
        
        tributario = ProcessoTributario.query.filter_by(processo_id=processo_id).first()
        if not tributario:
            raise ValueError(f"Dados tributários não encontrados para processo {processo_id}")
        
        # 2. Extrair features
        features = self.dataset_builder._extract_features(processo, tributario)
        if not features:
            raise ValueError("Erro ao extrair features")
        
        # 3. Criar DataFrame temporário para feature engineering
        temp_df = pd.DataFrame([features])
        self.dataset_builder.df = temp_df
        self.dataset_builder._engineer_features()
        
        # 4. Selecionar features usadas no treinamento
        feature_cols = self.modelo_db.features_utilizadas
        X = temp_df[feature_cols].fillna(0)
        
        # 5. Predizer
        valor_predito = self.modelo.predict(X)[0]
        
        # 6. Calcular confiança (baseado em R²)
        confianca = float(self.modelo_db.r2_score or 0.75)
        
        # 7. Criar resultado
        resultado = {
            'processo_id': processo_id,
            'valor_contingencia_predito': float(valor_predito),
            'confianca': confianca,
            'modelo_versao': self.modelo_db.versao,
            'modelo_algoritmo': self.modelo_db.algoritmo,
            'features_snapshot': features
        }
        
        # 8. Salvar no banco (opcional)
        if save_to_db:
            self._save_predicao(resultado)
        
        logger.info(f"Predição processo {processo_id}: R$ {valor_predito:,.2f} (confiança: {confianca:.2%})")
        
        return resultado
    
    def predict_batch(
        self,
        processo_ids: List[int],
        save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Prediz em lote para múltiplos processos
        
        Args:
            processo_ids: Lista de IDs
            save_to_db: Se True, salva predições no banco
            
        Returns:
            Lista de dicts com predições
        """
        resultados = []
        
        for processo_id in processo_ids:
            try:
                resultado = self.predict_processo(processo_id, save_to_db)
                resultados.append(resultado)
            except Exception as e:
                logger.error(f"Erro ao predizer processo {processo_id}: {e}")
                resultados.append({
                    'processo_id': processo_id,
                    'error': str(e)
                })
        
        return resultados
    
    def _save_predicao(self, resultado: Dict[str, Any]):
        """Salva predição no banco"""
        predicao = MLPredicaoTributario(
            processo_id=resultado['processo_id'],
            modelo_id=self.modelo_db.id_modelo,
            valor_contingencia_predito=resultado['valor_contingencia_predito'],
            valor_confianca=resultado['confianca'],
            features_snapshot=resultado['features_snapshot']
        )
        
        db.session.add(predicao)
        db.session.commit()
        
        logger.debug(f"Predição salva no DB: {predicao.id_predicao}")
    
    def get_ultimo_predicao(self, processo_id: int) -> Optional[Dict[str, Any]]:
        """Busca última predição de um processo"""
        predicao = MLPredicaoTributario.query.filter_by(
            processo_id=processo_id
        ).order_by(MLPredicaoTributario.data_predicao.desc()).first()
        
        if not predicao:
            return None
        
        return {
            'id_predicao': predicao.id_predicao,
            'processo_id': predicao.processo_id,
            'valor_predito': float(predicao.valor_contingencia_predito or 0),
            'confianca': float(predicao.valor_confianca or 0),
            'modelo_versao': predicao.modelo.versao,
            'data_predicao': predicao.data_predicao.isoformat()
        }


# Função auxiliar para uso rápido
def quick_predict(processo_id: int) -> Dict[str, Any]:
    """
    Predição rápida para um processo
    
    Args:
        processo_id: ID do processo
        
    Returns:
        Dict com predição
    """
    predictor = TributarioPredictor()
    return predictor.predict_processo(processo_id)
