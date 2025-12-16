"""
Dataset Builder para ML Tributário
Constrói dataset de treinamento a partir dos processos cadastrados
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, date
from decimal import Decimal
import logging

from main import db
from models_processos import (
    Processo,
    ProcessoTributario,
    ProcessoTese,
    TeseTributaria
)

logger = logging.getLogger(__name__)


class TributarioDatasetBuilder:
    """
    Constrói dataset para treinamento de modelos ML tributários
    
    Features extraídas:
    - Numéricas: valores (CDA, principal, multa, juros), percentuais, tempo
    - Categóricas: tributo, índice juros, comarca, vara, fase, status
    - Derivadas: razões, logs, contagens, flags
    """
    
    # Features numéricas diretas
    NUMERIC_FEATURES = [
        'valor_cda',
        'valor_principal', 
        'valor_multa',
        'percentual_multa',
        'valor_juros',
        'valor_causa',
        'valor_envolvido'
    ]
    
    # Features categóricas (IDs)
    CATEGORICAL_FEATURES = [
        'tributo_id',
        'indice_juros_id',
        'comarca_id',
        'vara_primeira_instancia_id',
        'turma_segunda_instancia_id',
        'fase_id',
        'status_id',
        'risco_id'
    ]
    
    def __init__(self):
        self.df = None
        self.features = []
        self.target_regression = 'contingencia'
        self.target_classification = 'risco_id'
        
    def build_dataset(
        self,
        min_samples: int = 50,
        natureza_id: int = 1  # Tributário
    ) -> Optional[pd.DataFrame]:
        """
        Constrói dataset completo
        
        Args:
            min_samples: Mínimo de amostras necessárias
            natureza_id: ID natureza (1=Tributário)
            
        Returns:
            DataFrame ou None se dados insuficientes
        """
        logger.info("Iniciando construção de dataset ML Tributário...")
        
        # 1. Buscar processos tributários
        query = db.session.query(
            Processo,
            ProcessoTributario
        ).join(
            ProcessoTributario,
            Processo.id_processo == ProcessoTributario.processo_id
        ).filter(
            Processo.natureza_id == natureza_id,
            Processo.ativo == True
        )
        
        processos = query.all()
        
        if len(processos) < min_samples:
            logger.warning(
                f"Dados insuficientes: {len(processos)} processos "
                f"(mínimo: {min_samples})"
            )
            return None
        
        logger.info(f"Encontrados {len(processos)} processos tributários")
        
        # 2. Extrair features
        data = []
        for processo, tributario in processos:
            row = self._extract_features(processo, tributario)
            if row:
                data.append(row)
        
        # 3. Criar DataFrame
        self.df = pd.DataFrame(data)
        
        # 4. Feature engineering
        self._engineer_features()
        
        # 5. Limpar valores nulos
        self._handle_missing_values()
        
        logger.info(f"Dataset criado: {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
        logger.info(f"Features: {list(self.df.columns)}")
        
        return self.df
    
    def _extract_features(
        self,
        processo: Processo,
        tributario: ProcessoTributario
    ) -> Optional[Dict]:
        """Extrai features de um processo"""
        
        try:
            row = {
                # ID para referência
                'processo_id': processo.id_processo,
                
                # Features numéricas do tributário
                'valor_cda': float(tributario.valor_inscrito_cda or 0),
                'valor_principal': float(tributario.valor_principal or 0),
                'valor_multa': float(tributario.valor_multa or 0),
                'percentual_multa': float(tributario.percentual_multa or 0),
                'valor_juros': float(tributario.valor_juros or 0),
                
                # Features numéricas do processo
                'valor_causa': float(processo.valor_causa or 0),
                'valor_envolvido': float(processo.valor_envolvido or 0),
                
                # Features categóricas
                'tributo_id': tributario.tributo_id or 0,
                'indice_juros': tributario.indice_juros or 'nao_informado',
                'comarca_id': processo.comarca_id or 0,
                'vara_primeira_instancia_id': tributario.vara_primeira_instancia_id or 0,
                'turma_segunda_instancia_id': tributario.turma_segunda_instancia_id or 0,
                'fase_id': processo.fase_id or 0,
                'status_id': processo.status_id or 0,
                
                # Target variables
                'contingencia': float(processo.contingencia or 0),
                'risco_id': processo.risco_id or 2,  # Default: Médio
                
                # Datas para cálculos
                'data_distribuicao': processo.data_distribuicao,
                'data_lancamento': tributario.data_lancamento
            }
            
            # Contar teses aplicadas
            teses_count = db.session.query(ProcessoTese).filter_by(
                processo_id=processo.id_processo
            ).count()
            row['teses_count'] = teses_count
            
            return row
            
        except Exception as e:
            logger.error(f"Erro ao extrair features processo {processo.id_processo}: {e}")
            return None
    
    def _engineer_features(self):
        """Cria features derivadas"""
        
        logger.info("Aplicando feature engineering...")
        
        # 1. Razões de valores
        self.df['razao_multa_principal'] = np.where(
            self.df['valor_principal'] > 0,
            self.df['valor_multa'] / self.df['valor_principal'],
            0
        )
        
        self.df['razao_juros_principal'] = np.where(
            self.df['valor_principal'] > 0,
            self.df['valor_juros'] / self.df['valor_principal'],
            0
        )
        
        # 2. Valor total
        self.df['valor_total'] = (
            self.df['valor_principal'] + 
            self.df['valor_multa'] + 
            self.df['valor_juros']
        )
        
        # 3. Logs (para valores muito altos)
        self.df['log_valor_cda'] = np.log1p(self.df['valor_cda'])  # log(x+1)
        self.df['log_valor_total'] = np.log1p(self.df['valor_total'])
        
        # 4. Flags booleanas
        self.df['tem_cda'] = (self.df['valor_cda'] > 0).astype(int)
        self.df['tem_multa'] = (self.df['valor_multa'] > 0).astype(int)
        self.df['tem_teses'] = (self.df['teses_count'] > 0).astype(int)
        
        # 5. Tempo de processo (anos)
        hoje = datetime.now()
        self.df['anos_processo'] = self.df['data_distribuicao'].apply(
            lambda x: (hoje - x).days / 365.25 if pd.notna(x) else 0
        )
        
        # 6. Tempo desde lançamento (anos)
        self.df['anos_desde_lancamento'] = self.df['data_lancamento'].apply(
            lambda x: (hoje - x).days / 365.25 if pd.notna(x) else 0
        )
        
        # 7. One-hot encoding para índice juros
        indice_dummies = pd.get_dummies(
            self.df['indice_juros'], 
            prefix='indice',
            drop_first=True
        )
        self.df = pd.concat([self.df, indice_dummies], axis=1)
        
        logger.info(f"Features engineered. Total colunas: {len(self.df.columns)}")
    
    def _handle_missing_values(self):
        """Trata valores nulos"""
        
        # Preencher numéricos com 0
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        self.df[numeric_cols] = self.df[numeric_cols].fillna(0)
        
        # Preencher categóricos com 'unknown' ou 0
        self.df['indice_juros'] = self.df['indice_juros'].fillna('nao_informado')
        
        # Remover linhas com target nulo
        before = len(self.df)
        self.df = self.df[self.df[self.target_regression].notna()]
        self.df = self.df[self.df[self.target_classification].notna()]
        after = len(self.df)
        
        if before > after:
            logger.info(f"Removidas {before - after} linhas com target nulo")
    
    def get_features_for_training(self) -> List[str]:
        """
        Retorna lista de features para usar no treinamento
        (exclui ID, targets, datas)
        """
        exclude = [
            'processo_id',
            'contingencia',  # target regressão
            'risco_id',  # target classificação
            'data_distribuicao',
            'data_lancamento',
            'indice_juros'  # já codificado em dummies
        ]
        
        features = [
            col for col in self.df.columns 
            if col not in exclude
        ]
        
        return features
    
    def split_train_test(
        self,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Divide dataset em treino e teste
        
        Returns:
            (train_df, test_df)
        """
        from sklearn.model_selection import train_test_split
        
        train_df, test_df = train_test_split(
            self.df,
            test_size=test_size,
            random_state=random_state,
            stratify=self.df[self.target_classification]  # Balancear por risco
        )
        
        logger.info(f"Split: {len(train_df)} treino, {len(test_df)} teste")
        
        return train_df, test_df
    
    def get_X_y_regression(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Retorna X e y para regressão"""
        features = self.get_features_for_training()
        X = df[features]
        y = df[self.target_regression]
        return X, y
    
    def get_X_y_classification(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Retorna X e y para classificação"""
        features = self.get_features_for_training()
        X = df[features]
        y = df[self.target_classification]
        return X, y


# Funções auxiliares
def check_data_availability() -> Dict[str, int]:
    """
    Verifica disponibilidade de dados
    
    Returns:
        Dict com contagens
    """
    total_processos = Processo.query.filter_by(
        natureza_id=1,  # Tributário
        ativo=True
    ).count()
    
    com_tributario = db.session.query(Processo).join(
        ProcessoTributario
    ).filter(
        Processo.natureza_id == 1,
        Processo.ativo == True
    ).count()
    
    com_contingencia = db.session.query(Processo).filter(
        Processo.natureza_id == 1,
        Processo.ativo == True,
        Processo.contingencia.isnot(None),
        Processo.contingencia > 0
    ).count()
    
    return {
        'total_processos_tributarios': total_processos,
        'com_dados_tributarios': com_tributario,
        'com_contingencia_definida': com_contingencia
    }
