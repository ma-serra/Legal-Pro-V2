"""
Módulo ML Tributário
Machine Learning para processos tributários usando XGBoost
"""

from .predictor import TributarioPredictor
from .trainer import TributarioTrainer

__all__ = ['TributarioPredictor', 'TributarioTrainer']
