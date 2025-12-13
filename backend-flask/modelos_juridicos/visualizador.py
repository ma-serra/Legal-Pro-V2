"""
Sistema de Visualizações para Modelos Jurídicos
===============================================

Gera gráficos, relatórios visuais e dashboards para análise
dos modelos estatísticos e recomendações.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os


class VisualizadorModelos:
    """
    Visualizador para Modelos Jurídicos
    
    Gera gráficos e relatórios visuais para análise de:
    - Coeficientes dos modelos
    - Especificidade por contexto
    - Comparações de estratégias
    - Performance histórica
    """
    
    def __init__(self, data_path: str = 'modelos_juridicos/data', output_path: str = 'modelos_juridicos/reports'):
        self.data_path = data_path
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
        
        # Configurar estilo dos gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def plot_coeficientes_modelo(self, salvar: bool = True) -> str:
        """Gráfico de barras dos coeficientes do modelo"""
        try:
            # Carregar coeficientes
            try:
                df_coef = pd.read_csv(f"{self.data_path}/coeficientes_modelo_1756659091710.csv")
            except FileNotFoundError:
                df_coef = pd.read_csv(f"{self.data_path}/coeficientes_modelo_1756658854798.csv")
            
            # Preparar dados
            df_coef = df_coef.sort_values('coef', key=abs, ascending=True)
            
            # Criar gráfico
            fig, ax = plt.subplots(figsize=(12, 8))
            
            colors = ['red' if x < 0 else 'green' for x in df_coef['coef']]
            bars = ax.barh(df_coef['feature'], df_coef['coef'], color=colors, alpha=0.7)
            
            # Personalizar
            ax.set_xlabel('Coeficiente (Impacto na Probabilidade de Vitória)')
            ax.set_ylabel('Features do Modelo')
            ax.set_title('Impacto das Estratégias e Contextos na Vitória Processual', 
                        fontsize=14, fontweight='bold')
            
            # Adicionar linha zero
            ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            
            # Adicionar valores nas barras
            for i, (bar, valor) in enumerate(zip(bars, df_coef['coef'])):
                ax.text(valor + (0.01 if valor > 0 else -0.01), bar.get_y() + bar.get_height()/2, 
                       f'{valor:.3f}', ha='left' if valor > 0 else 'right', va='center', fontsize=9)
            
            plt.tight_layout()
            
            if salvar:
                caminho = f"{self.output_path}/coeficientes_modelo.png"
                plt.savefig(caminho, dpi=300, bbox_inches='tight')
                plt.close()
                print(f"✅ Gráfico salvo: {caminho}")
                return caminho
            else:
                plt.show()
                return "Gráfico exibido"
                
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de coeficientes: {e}")
            return ""
    
    def plot_especificidade_foro(self, salvar: bool = True) -> str:
        """Gráfico de especificidade por foro e threshold"""
        try:
            # Carregar dados
            try:
                df_scores = pd.read_csv(f"{self.data_path}/dataset_scores_1756659091709.csv")
            except FileNotFoundError:
                df_scores = pd.read_csv(f"{self.data_path}/dataset_scores_1756658854797.csv")
            
            # Criar gráfico
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Plot por foro
            for foro in df_scores['foro'].unique():
                df_foro = df_scores[df_scores['foro'] == foro]
                ax.plot(df_foro['threshold'], df_foro['spec_teorica'], 
                       marker='o', linewidth=2, label=f'Foro {foro}')
            
            # Personalizar
            ax.set_xlabel('Threshold de Decisão')
            ax.set_ylabel('Especificidade Teórica')
            ax.set_title('Especificidade por Foro e Threshold de Decisão', 
                        fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Destacar threshold ótimo
            threshold_otimo = df_scores.groupby('threshold')['spec_teorica'].mean().idxmax()
            ax.axvline(x=threshold_otimo, color='red', linestyle='--', alpha=0.7, 
                      label=f'Threshold Ótimo: {threshold_otimo}')
            ax.legend()
            
            plt.tight_layout()
            
            if salvar:
                caminho = f"{self.output_path}/especificidade_por_foro.png"
                plt.savefig(caminho, dpi=300, bbox_inches='tight')
                plt.close()
                print(f"✅ Gráfico salvo: {caminho}")
                return caminho
            else:
                plt.show()
                return "Gráfico exibido"
                
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de especificidade: {e}")
            return ""
    
    def plot_sensibilidade_especificidade(self, salvar: bool = True) -> str:
        """Gráfico de dispersão sensibilidade vs especificidade"""
        try:
            # Carregar dados
            try:
                df_biv = pd.read_csv(f"{self.data_path}/dataset_bivariado_1756659091705.csv")
            except FileNotFoundError:
                df_biv = pd.read_csv(f"{self.data_path}/dataset_bivariado_1756658854794.csv")
            
            # Criar gráfico
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Scatter plot por foro
            for foro in df_biv['foro'].unique():
                df_foro = df_biv[df_biv['foro'] == foro]
                ax.scatter(df_foro['sensibilidade'], df_foro['especificidade'], 
                          s=100, alpha=0.7, label=f'Foro {foro}')
            
            # Personalizar
            ax.set_xlabel('Sensibilidade (Taxa de Verdadeiros Positivos)')
            ax.set_ylabel('Especificidade (Taxa de Verdadeiros Negativos)')
            ax.set_title('Trade-off Sensibilidade vs Especificidade por Foro', 
                        fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Adicionar linha diagonal (sensibilidade = especificidade)
            ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Sensibilidade = Especificidade')
            ax.legend()
            
            # Definir limites
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            
            plt.tight_layout()
            
            if salvar:
                caminho = f"{self.output_path}/sensibilidade_especificidade.png"
                plt.savefig(caminho, dpi=300, bbox_inches='tight')
                plt.close()
                print(f"✅ Gráfico salvo: {caminho}")
                return caminho
            else:
                plt.show()
                return "Gráfico exibido"
                
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico sens vs spec: {e}")
            return ""
    
    def plot_distribuicao_valores(self, salvar: bool = True) -> str:
        """Histograma da distribuição de valores de causa"""
        try:
            # Carregar dados de defesas
            try:
                df_defesas = pd.read_csv(f"{self.data_path}/dataset_defesas_1756659091707.csv")
            except FileNotFoundError:
                df_defesas = pd.read_csv(f"{self.data_path}/dataset_defesas_1756658854795.csv")
            
            # Criar subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Distribuições dos Dados Processuais', fontsize=16, fontweight='bold')
            
            # 1. Distribuição de valores de causa
            axes[0,0].hist(df_defesas['valor_causa'], bins=50, alpha=0.7, color='skyblue')
            axes[0,0].set_xlabel('Valor da Causa (R$)')
            axes[0,0].set_ylabel('Frequência')
            axes[0,0].set_title('Distribuição dos Valores de Causa')
            
            # 2. Distribuição por área
            area_counts = df_defesas['area'].value_counts()
            axes[0,1].pie(area_counts.values, labels=area_counts.index, autopct='%1.1f%%')
            axes[0,1].set_title('Distribuição por Área Jurídica')
            
            # 3. Distribuição por foro
            foro_counts = df_defesas['foro'].value_counts()
            axes[1,0].bar(foro_counts.index, foro_counts.values, color='lightcoral')
            axes[1,0].set_xlabel('Foro')
            axes[1,0].set_ylabel('Número de Casos')
            axes[1,0].set_title('Distribuição por Foro')
            
            # 4. Taxa de vitória por ano
            vitoria_ano = df_defesas.groupby('ano')['vitoria'].mean()
            axes[1,1].plot(vitoria_ano.index, vitoria_ano.values, marker='o', linewidth=2)
            axes[1,1].set_xlabel('Ano')
            axes[1,1].set_ylabel('Taxa de Vitória')
            axes[1,1].set_title('Evolução da Taxa de Vitória')
            axes[1,1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if salvar:
                caminho = f"{self.output_path}/distribuicoes_dados.png"
                plt.savefig(caminho, dpi=300, bbox_inches='tight')
                plt.close()
                print(f"✅ Gráfico salvo: {caminho}")
                return caminho
            else:
                plt.show()
                return "Gráfico exibido"
                
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de distribuições: {e}")
            return ""
    
    def plot_matriz_correlacao(self, salvar: bool = True) -> str:
        """Matriz de correlação das estratégias"""
        try:
            # Carregar dados
            try:
                df_defesas = pd.read_csv(f"{self.data_path}/dataset_defesas_1756659091707.csv")
            except FileNotFoundError:
                df_defesas = pd.read_csv(f"{self.data_path}/dataset_defesas_1756658854795.csv")
            
            # Selecionar apenas variáveis binárias (estratégias)
            estrategias = ['prescricao', 'impugnacao_pericia', 'nulidade_prova', 
                          'acordo_proposto', 'ilegitimidade', 'decadencia', 'vitoria']
            
            df_estrategias = df_defesas[estrategias]
            
            # Calcular correlação
            corr_matrix = df_estrategias.corr()
            
            # Criar heatmap
            fig, ax = plt.subplots(figsize=(10, 8))
            
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": 0.5}, ax=ax)
            
            ax.set_title('Matriz de Correlação - Estratégias de Defesa e Vitória', 
                        fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            if salvar:
                caminho = f"{self.output_path}/matriz_correlacao_estrategias.png"
                plt.savefig(caminho, dpi=300, bbox_inches='tight')
                plt.close()
                print(f"✅ Gráfico salvo: {caminho}")
                return caminho
            else:
                plt.show()
                return "Gráfico exibido"
                
        except Exception as e:
            print(f"❌ Erro ao gerar matriz de correlação: {e}")
            return ""
    
    def gerar_relatorio_visual_completo(self) -> List[str]:
        """Gera todos os gráficos e retorna lista dos caminhos"""
        print("🎨 Gerando relatório visual completo...")
        
        graficos_gerados = []
        
        # Gerar todos os gráficos
        graficos = [
            self.plot_coeficientes_modelo(),
            self.plot_especificidade_foro(),
            self.plot_sensibilidade_especificidade(),
            self.plot_distribuicao_valores(),
            self.plot_matriz_correlacao()
        ]
        
        # Filtrar apenas os que foram gerados com sucesso
        graficos_gerados = [g for g in graficos if g and g != "Gráfico exibido"]
        
        print(f"✅ Relatório visual completo gerado: {len(graficos_gerados)} gráficos")
        return graficos_gerados
    
    def criar_dashboard_interativo(self, salvar: bool = True) -> str:
        """Cria dashboard interativo com Plotly"""
        try:
            # Carregar dados
            try:
                df_defesas = pd.read_csv(f"{self.data_path}/dataset_defesas_1756659091707.csv")
                df_biv = pd.read_csv(f"{self.data_path}/dataset_bivariado_1756659091705.csv")
            except FileNotFoundError:
                df_defesas = pd.read_csv(f"{self.data_path}/dataset_defesas_1756658854795.csv")
                df_biv = pd.read_csv(f"{self.data_path}/dataset_bivariado_1756658854794.csv")
            
            # Criar subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Taxa de Vitória por Área', 'Valor da Causa por Foro',
                               'Sensibilidade vs Especificidade', 'Evolução Temporal'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # 1. Taxa de vitória por área
            vitoria_area = df_defesas.groupby('area')['vitoria'].mean().reset_index()
            fig.add_trace(
                go.Bar(x=vitoria_area['area'], y=vitoria_area['vitoria'], name='Taxa de Vitória'),
                row=1, col=1
            )
            
            # 2. Box plot valor da causa por foro
            for i, foro in enumerate(df_defesas['foro'].unique()):
                df_foro = df_defesas[df_defesas['foro'] == foro]
                fig.add_trace(
                    go.Box(y=df_foro['valor_causa'], name=f'Foro {foro}', showlegend=False),
                    row=1, col=2
                )
            
            # 3. Scatter sensibilidade vs especificidade
            fig.add_trace(
                go.Scatter(
                    x=df_biv['sensibilidade'], y=df_biv['especificidade'],
                    mode='markers', text=df_biv['foro'] + ' - ' + df_biv['area'],
                    name='Foro-Área', showlegend=False
                ),
                row=2, col=1
            )
            
            # 4. Evolução temporal
            evolucao = df_defesas.groupby('ano')['vitoria'].mean().reset_index()
            fig.add_trace(
                go.Scatter(x=evolucao['ano'], y=evolucao['vitoria'], mode='lines+markers',
                          name='Taxa de Vitória', showlegend=False),
                row=2, col=2
            )
            
            # Atualizar layout
            fig.update_layout(
                title_text="Dashboard Analítico - Modelos Jurídicos",
                height=800,
                showlegend=True
            )
            
            if salvar:
                caminho = f"{self.output_path}/dashboard_interativo.html"
                fig.write_html(caminho)
                print(f"✅ Dashboard salvo: {caminho}")
                return caminho
            else:
                fig.show()
                return "Dashboard exibido"
                
        except Exception as e:
            print(f"❌ Erro ao gerar dashboard: {e}")
            return ""