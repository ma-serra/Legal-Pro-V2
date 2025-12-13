"""
VISUALIZAÇÕES AVANÇADAS FINTECH
==================================

Implementa todas as visualizações especificadas no prompt_replit_preditivo.md:
- Gauge Charts, Probability Bars, Feature Importance
- Time Series Forecasts, Confidence Bands
- Alert Cards, Anomaly Timelines, Heat Maps
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import seaborn as sns
import matplotlib.pyplot as plt

class FintechVisualizations:
    """
    Classe para todas as visualizações do sistema Fintech
    """
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'success': '#2ca02c', 
            'warning': '#ff7f0e',
            'danger': '#d62728',
            'info': '#17a2b8',
            'fintech': '#eb001b',
            'favorable': '#2ca02c',
            'unfavorable': '#d62728',
            'neutral': '#6c757d'
        }
    
    # =====================================
    # VISUALIZAÇÕES - PREDIÇÃO DE CASOS
    # =====================================
    
    def create_favorability_gauge(self, score: int, confidence: float = 0.8) -> go.Figure:
        """
        Gauge Chart para score de favorabilidade (1-5)
        """
        # Converter score 1-5 para porcentagem
        percentage = (score - 1) / 4 * 100
        
        # Cores baseadas no score
        if score <= 2:
            color = self.color_palette['danger']
        elif score <= 3:
            color = self.color_palette['warning'] 
        else:
            color = self.color_palette['success']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = percentage,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Score de Favorabilidade<br>Confiança: {confidence:.1%}"},
            delta = {'reference': 60, 'position': "top"},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 25], 'color': '#ffe6e6'},
                    {'range': [25, 50], 'color': '#fff3cd'},
                    {'range': [50, 75], 'color': '#d1ecf1'},
                    {'range': [75, 100], 'color': '#d4edda'}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75, 'value': 90}
            }
        ))
        
        fig.update_layout(
            height=400,
            font={'color': "darkblue", 'family': "Arial"},
            paper_bgcolor="white"
        )
        
        return fig
    
    def create_probability_bar(self, probabilities: Dict[str, float]) -> go.Figure:
        """
        Bar chart horizontal para probabilidades de resultado
        """
        if not probabilities:
            probabilities = {'Neutro': 1.0}
        
        classes = list(probabilities.keys())
        probs = list(probabilities.values())
        
        # Cores por classe
        colors = []
        for cls in classes:
            if cls in [1, 2] or 'Desfavorável' in str(cls):
                colors.append(self.color_palette['danger'])
            elif cls in [4, 5] or 'Favorável' in str(cls):
                colors.append(self.color_palette['success'])
            else:
                colors.append(self.color_palette['neutral'])
        
        fig = go.Figure([go.Bar(
            x=probs,
            y=classes,
            orientation='h',
            marker_color=colors,
            text=[f'{p:.1%}' for p in probs],
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Probabilidade por Classe",
            xaxis_title="Probabilidade",
            yaxis_title="Resultado",
            height=300,
            xaxis=dict(tickformat='.0%')
        )
        
        return fig
    
    def create_feature_importance_chart(self, importance_dict: Dict[str, float]) -> go.Figure:
        """
        Chart de importância das features
        """
        if not importance_dict:
            return go.Figure()
        
        # Ordenar por importância
        sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        features, importance = zip(*sorted_features[:10])  # Top 10
        
        fig = go.Figure([go.Bar(
            x=list(importance),
            y=list(features),
            orientation='h',
            marker_color=self.color_palette['info']
        )])
        
        fig.update_layout(
            title="Importância das Features",
            xaxis_title="Importância",
            yaxis_title="Feature",
            height=400
        )
        
        return fig
    
    # =====================================
    # VISUALIZAÇÕES - FORECASTING TEMPORAL
    # =====================================
    
    def create_forecast_time_series(self, 
                                   historical_data: pd.DataFrame,
                                   forecast_data: Dict[str, Any]) -> go.Figure:
        """
        Série temporal com forecast e confidence intervals
        """
        fig = go.Figure()
        
        # Dados históricos
        fig.add_trace(go.Scatter(
            x=historical_data['data'],
            y=historical_data['taxa_sucesso'],
            mode='lines+markers',
            name='Dados Históricos',
            line=dict(color=self.color_palette['primary'], width=2)
        ))
        
        # Forecast
        if 'dates' in forecast_data and 'forecast' in forecast_data:
            fig.add_trace(go.Scatter(
                x=forecast_data['dates'],
                y=forecast_data['forecast'],
                mode='lines+markers',
                name='Previsão',
                line=dict(color=self.color_palette['fintech'], width=2, dash='dash')
            ))
            
            # Confidence intervals
            if 'confidence_upper' in forecast_data and 'confidence_lower' in forecast_data:
                # Upper bound
                fig.add_trace(go.Scatter(
                    x=forecast_data['dates'],
                    y=forecast_data['confidence_upper'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Lower bound com fill
                fig.add_trace(go.Scatter(
                    x=forecast_data['dates'],
                    y=forecast_data['confidence_lower'],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor=f'rgba(235, 0, 27, 0.2)',  # Fintech color com transparência
                    name='Intervalo de Confiança',
                    hoverinfo='skip'
                ))
        
        fig.update_layout(
            title="Previsão de Taxa de Sucesso - Próximos 12 Meses",
            xaxis_title="Data",
            yaxis_title="Taxa de Sucesso (%)",
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def create_seasonal_decomposition(self, ts_data: pd.DataFrame) -> go.Figure:
        """
        Decomposição sazonal da série temporal
        """
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        # Preparar dados
        ts_series = ts_data.set_index('data')['taxa_sucesso']
        ts_series.index.freq = 'MS'  # Monthly start frequency
        
        # Decomposição
        decomposition = seasonal_decompose(ts_series, model='additive', period=12)
        
        # Criar subplots
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=['Série Original', 'Tendência', 'Sazonalidade', 'Resíduos'],
            vertical_spacing=0.08
        )
        
        # Série original
        fig.add_trace(go.Scatter(
            x=ts_series.index, y=ts_series.values,
            mode='lines', name='Original',
            line=dict(color=self.color_palette['primary'])
        ), row=1, col=1)
        
        # Tendência
        fig.add_trace(go.Scatter(
            x=decomposition.trend.index, y=decomposition.trend.values,
            mode='lines', name='Tendência',
            line=dict(color=self.color_palette['success'])
        ), row=2, col=1)
        
        # Sazonalidade
        fig.add_trace(go.Scatter(
            x=decomposition.seasonal.index, y=decomposition.seasonal.values,
            mode='lines', name='Sazonalidade',
            line=dict(color=self.color_palette['warning'])
        ), row=3, col=1)
        
        # Resíduos
        fig.add_trace(go.Scatter(
            x=decomposition.resid.index, y=decomposition.resid.values,
            mode='lines', name='Resíduos',
            line=dict(color=self.color_palette['info'])
        ), row=4, col=1)
        
        fig.update_layout(
            height=800,
            title_text="Decomposição Sazonal - Taxa de Sucesso",
            showlegend=False
        )
        
        return fig
    
    # =====================================
    # VISUALIZAÇÕES - SISTEMA DE ALERTAS
    # =====================================
    
    def create_alert_cards(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cria dados para cards de alertas
        """
        alert_cards = []
        
        for alert in alerts:
            # Determinar cor por severidade
            severity_colors = {
                'Alta': self.color_palette['danger'],
                'Média': self.color_palette['warning'],
                'Baixa': self.color_palette['info']
            }
            
            card_data = {
                'title': alert['tipo'],
                'message': f"{alert['metrica']}: {alert['valor_atual']:.1f}",
                'expected': f"Esperado: {alert['valor_esperado']:.1f}",
                'deviation': f"Desvio: {alert['desvio']:.1f}σ",
                'severity': alert['severidade'],
                'color': severity_colors.get(alert['severidade'], self.color_palette['neutral']),
                'state': alert['estado'],
                'timestamp': alert['timestamp']
            }
            
            alert_cards.append(card_data)
        
        return alert_cards
    
    def create_anomaly_timeline(self, anomaly_data: pd.DataFrame) -> go.Figure:
        """
        Timeline de anomalias detectadas
        """
        if anomaly_data.empty:
            fig = go.Figure()
            fig.add_annotation(text="Nenhuma anomalia detectada", 
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
            fig.update_layout(title="Timeline de Anomalias", height=300)
            return fig
        
        fig = go.Figure()
        
        # Adicionar pontos para cada anomalia
        for severity in anomaly_data['severidade'].unique():
            severity_data = anomaly_data[anomaly_data['severidade'] == severity]
            
            color_map = {
                'Alta': self.color_palette['danger'],
                'Média': self.color_palette['warning'],
                'Baixa': self.color_palette['info']
            }
            
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(severity_data['timestamp']),
                y=severity_data['desvio'],
                mode='markers',
                name=f'Severidade {severity}',
                marker=dict(
                    color=color_map.get(severity, self.color_palette['neutral']),
                    size=10,
                    symbol='circle'
                ),
                text=severity_data['metrica'],
                hovertemplate='<b>%{text}</b><br>Desvio: %{y:.2f}σ<br>Data: %{x}<extra></extra>'
            ))
        
        fig.update_layout(
            title="Timeline de Anomalias Detectadas",
            xaxis_title="Data",
            yaxis_title="Severidade (Desvios Padrão)",
            height=400,
            hovermode='closest'
        )
        
        return fig
    
    def create_geographic_heatmap(self, state_data: Dict[str, Any]) -> go.Figure:
        """
        Mapa de calor geográfico por estado
        """
        # Dados fictícios se não fornecidos (para demonstração)
        if not state_data:
            state_data = {
                'SP': {'taxa_sucesso': 70, 'alertas': 0},
                'RJ': {'taxa_sucesso': 65, 'alertas': 1},
                'MG': {'taxa_sucesso': 68, 'alertas': 0},
                'RS': {'taxa_sucesso': 72, 'alertas': 0},
                'PR': {'taxa_sucesso': 69, 'alertas': 0}
            }
        
        states = list(state_data.keys())
        success_rates = [data['taxa_sucesso'] for data in state_data.values()]
        alert_counts = [data['alertas'] for data in state_data.values()]
        
        # Criar heatmap
        fig = go.Figure(data=go.Scatter(
            x=states,
            y=['Taxa de Sucesso'] * len(states),
            mode='markers',
            marker=dict(
                size=[50] * len(states),
                color=success_rates,
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Taxa de Sucesso (%)"),
                cmin=50,
                cmax=80
            ),
            text=[f"{state}<br>Taxa: {rate}%<br>Alertas: {alerts}" 
                  for state, rate, alerts in zip(states, success_rates, alert_counts)],
            hovertemplate='%{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Mapa de Performance por Estado",
            xaxis_title="Estado",
            height=400,
            showlegend=False
        )
        
        return fig
    
    # =====================================
    # DASHBOARD EXECUTIVO
    # =====================================
    
    def create_executive_dashboard(self, 
                                 kpis: Dict[str, Any],
                                 forecast_data: Dict[str, Any],
                                 alerts: List[Dict[str, Any]]) -> go.Figure:
        """
        Dashboard executivo completo 2x2
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Taxa de Sucesso Geral',
                'Performance por Estado', 
                'Previsão Próximos Meses',
                'Distribuição de Resultados'
            ],
            specs=[
                [{"type": "indicator"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "pie"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.12
        )
        
        # 1. KPI Principal (Gauge)
        taxa_sucesso = kpis.get('taxa_sucesso_geral', 65.4)
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=taxa_sucesso,
            title={'text': "Taxa de Sucesso %"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': self.color_palette['fintech']},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 70], 'color': "yellow"},
                    {'range': [70, 85], 'color': "lightgreen"},
                    {'range': [85, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75, 'value': 90
                }
            }
        ), row=1, col=1)
        
        # 2. Performance por Estado (Top 5)
        if 'performance_estados' in kpis:
            perf_estados = kpis['performance_estados'].head()
            estados = perf_estados.index.tolist()
            taxas = perf_estados[('resultado', '<lambda>')].tolist()
            
            fig.add_trace(go.Bar(
                x=estados,
                y=taxas,
                marker_color=self.color_palette['info'],
                name="Taxa Sucesso"
            ), row=1, col=2)
        
        # 3. Previsão (Simplified)
        if forecast_data and 'forecast' in forecast_data:
            months = list(range(1, min(7, len(forecast_data['forecast'])+1)))  # Próximos 6 meses
            forecast_values = forecast_data['forecast'][:6]
            
            fig.add_trace(go.Scatter(
                x=months,
                y=forecast_values,
                mode='lines+markers',
                name="Previsão",
                line=dict(color=self.color_palette['success'])
            ), row=2, col=1)
        
        # 4. Distribuição de Resultados (Pie)
        if 'distribuicao_resultados' in kpis:
            dist = kpis['distribuicao_resultados']
            labels = ['Favorável', 'Desfavorável', 'Neutro']
            values = [dist.get('favoravel', 0), dist.get('desfavoravel', 0), dist.get('neutro', 0)]
            colors = [self.color_palette['success'], self.color_palette['danger'], self.color_palette['neutral']]
            
            fig.add_trace(go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                name="Distribuição"
            ), row=2, col=2)
        
        fig.update_layout(
            height=800,
            title_text="Dashboard Executivo Fintech",
            showlegend=False
        )
        
        return fig
    
    # =====================================
    # UTILITÁRIOS
    # =====================================
    
    def create_confusion_matrix_plot(self, y_true, y_pred, classes=None) -> go.Figure:
        """
        Matriz de confusão interativa
        """
        from sklearn.metrics import confusion_matrix
        
        if classes is None:
            classes = sorted(list(set(y_true) | set(y_pred)))
        
        cm = confusion_matrix(y_true, y_pred, labels=classes)
        
        # Normalizar
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        fig = go.Figure(data=go.Heatmap(
            z=cm_normalized,
            x=classes,
            y=classes,
            colorscale='Blues',
            text=cm,
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate='Previsto: %{x}<br>Real: %{y}<br>Count: %{text}<br>Rate: %{z:.2%}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Matriz de Confusão",
            xaxis_title="Predito",
            yaxis_title="Real",
            height=400
        )
        
        return fig
    
    def create_roc_curve(self, y_true, y_proba, classes=None) -> go.Figure:
        """
        Curva ROC para classificação
        """
        from sklearn.metrics import roc_curve, auc
        from sklearn.preprocessing import label_binarize
        
        if classes is None:
            classes = sorted(list(set(y_true)))
        
        # Binarizar labels para multiclass
        y_test_bin = label_binarize(y_true, classes=classes)
        n_classes = len(classes)
        
        fig = go.Figure()
        
        # Calcular ROC para cada classe
        for i, class_name in enumerate(classes):
            if n_classes == 2 and i == 1:
                break  # Para binário, só precisamos de uma curva
                
            y_score = y_proba[:, i] if y_proba.ndim > 1 else y_proba
            
            if n_classes > 2:
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score)
            else:
                fpr, tpr, _ = roc_curve(y_true, y_score)
            
            roc_auc = auc(fpr, tpr)
            
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr,
                mode='lines',
                name=f'Classe {class_name} (AUC = {roc_auc:.2f})',
                line=dict(width=2)
            ))
        
        # Linha diagonal
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='lines',
            name='Random',
            line=dict(dash='dash', color='gray')
        ))
        
        fig.update_layout(
            title="Curva ROC",
            xaxis_title="Taxa de Falsos Positivos",
            yaxis_title="Taxa de Verdadeiros Positivos",
            height=500
        )
        
        return fig