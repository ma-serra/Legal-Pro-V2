"""
Sistema de Recomendações de Defesa Jurídica
==========================================

Integra modelos estatísticos para fornecer recomendações práticas
de estratégias de defesa e thresholds ótimos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from .modulo_modelos_juridicos import ModeloDefesa, ModeloEspecificidade
import json


class RecomendadorDefesa:
    """
    Recomendador Inteligente de Estratégias de Defesa
    
    Combina modelos de defesa e especificidade para fornecer
    recomendações personalizadas por caso.
    """
    
    def __init__(self, data_path: str = 'modelos_juridicos/data'):
        self.data_path = data_path
        self.modelo_defesa = ModeloDefesa(data_path)
        self.modelo_especificidade = ModeloEspecificidade(data_path)
        self.coeficientes_conhecidos = None
        self.estrategias_disponiveis = [
            'prescricao', 'impugnacao_pericia', 'nulidade_prova',
            'acordo_proposto', 'ilegitimidade', 'decadencia'
        ]
        self.inicializar()
    
    def inicializar(self):
        """Inicializa recomendador carregando coeficientes conhecidos"""
        try:
            # Tentar carregar coeficientes pré-calculados
            df_coef = pd.read_csv(f"{self.data_path}/coeficientes_modelo_1756659091710.csv")
            self.coeficientes_conhecidos = df_coef.set_index('feature')['coef'].to_dict()
            print("✅ Coeficientes conhecidos carregados")
        except FileNotFoundError:
            try:
                df_coef = pd.read_csv(f"{self.data_path}/coeficientes_modelo_1756658854798.csv")
                self.coeficientes_conhecidos = df_coef.set_index('feature')['coef'].to_dict()
                print("✅ Coeficientes conhecidos carregados (arquivo alternativo)")
            except FileNotFoundError:
                print("⚠️  Coeficientes não encontrados, será necessário treinar modelo")
    
    def recomendar_estrategia_completa(self, caso: Dict) -> Dict:
        """
        Recomendação completa de estratégia baseada em análise estatística
        
        Args:
            caso: dict com foro, area, juiz, valor_causa, ano, estratégias atuais
            
        Returns:
            dict com recomendações detalhadas
        """
        resultado = {
            'caso_id': caso.get('id', 'N/A'),
            'foro': caso.get('foro', 'N/A'),
            'area': caso.get('area', 'N/A'),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # 1. Análise com coeficientes conhecidos (se disponível)
        if self.coeficientes_conhecidos:
            recom_coeficientes = self._recomendar_por_coeficientes(caso)
            resultado['recomendacao_coeficientes'] = recom_coeficientes
        
        # 2. Análise de especificidade por threshold
        recom_threshold = self._analisar_threshold_otimo(caso)
        resultado['recomendacao_threshold'] = recom_threshold
        
        # 3. Análise contextual (foro/área)
        recom_contextual = self._analisar_contexto(caso)
        resultado['recomendacao_contextual'] = recom_contextual
        
        # 4. Recomendação final consolidada
        recom_final = self._consolidar_recomendacoes(resultado)
        resultado['recomendacao_final'] = recom_final
        
        return resultado
    
    def _recomendar_por_coeficientes(self, caso: Dict) -> Dict:
        """Recomenda baseado nos coeficientes conhecidos do modelo"""
        if not self.coeficientes_conhecidos:
            return {'erro': 'Coeficientes não disponíveis'}
        
        # Analisar impacto das estratégias binárias
        estrategias_impacto = {}
        for estrategia in self.estrategias_disponiveis:
            coef_key = f'bin__{estrategia}'
            if coef_key in self.coeficientes_conhecidos:
                estrategias_impacto[estrategia] = {
                    'coeficiente': self.coeficientes_conhecidos[coef_key],
                    'impacto': 'Positivo' if self.coeficientes_conhecidos[coef_key] > 0 else 'Negativo',
                    'magnitude': abs(self.coeficientes_conhecidos[coef_key])
                }
        
        # Ordenar por impacto positivo
        estrategias_ordenadas = sorted(
            [(k, v) for k, v in estrategias_impacto.items() if v['coeficiente'] > 0],
            key=lambda x: x[1]['coeficiente'], reverse=True
        )
        
        if estrategias_ordenadas:
            melhor_estrategia = estrategias_ordenadas[0][0]
            melhor_coef = estrategias_ordenadas[0][1]['coeficiente']
        else:
            melhor_estrategia = 'Nenhuma estratégia com impacto positivo identificada'
            melhor_coef = 0
        
        # Análise de contexto (foro/área)
        contexto_foro = self._analisar_coeficientes_contextuais('foro', caso.get('foro'))
        contexto_area = self._analisar_coeficientes_contextuais('area', caso.get('area'))
        
        return {
            'estrategia_recomendada': melhor_estrategia,
            'impacto_esperado': melhor_coef,
            'todas_estrategias': estrategias_impacto,
            'contexto_foro': contexto_foro,
            'contexto_area': contexto_area,
            'interpretacao': self._interpretar_estrategia(melhor_estrategia)
        }
    
    def _analisar_coeficientes_contextuais(self, tipo: str, valor: str) -> Dict:
        """Analisa coeficientes contextuais (foro/área)"""
        if not valor or not self.coeficientes_conhecidos:
            return {'impacto': 'neutro', 'coeficiente': 0}
        
        key_pattern = f'onehot__{tipo}_{valor}'
        coef = self.coeficientes_conhecidos.get(key_pattern, 0)
        
        return {
            'coeficiente': coef,
            'impacto': 'Positivo' if coef > 0 else 'Negativo' if coef < 0 else 'Neutro',
            'magnitude': abs(coef)
        }
    
    def _analisar_threshold_otimo(self, caso: Dict) -> Dict:
        """Analisa threshold ótimo baseado nos dados de especificidade"""
        try:
            # Carregar dados de scores
            try:
                df_scores = pd.read_csv(f"{self.data_path}/dataset_scores_1756659091709.csv")
            except FileNotFoundError:
                df_scores = pd.read_csv(f"{self.data_path}/dataset_scores_1756658854797.csv")
            
            foro = caso.get('foro', 'SP')  # Default SP
            
            # Filtrar por foro se disponível
            if foro in df_scores['foro'].values:
                df_foro = df_scores[df_scores['foro'] == foro]
            else:
                df_foro = df_scores  # Usar todos se foro não encontrado
            
            # Encontrar threshold ótimo (maior especificidade)
            threshold_otimo = df_foro.loc[df_foro['spec_teorica'].idxmax(), 'threshold']
            spec_maxima = df_foro['spec_teorica'].max()
            
            return {
                'threshold_otimo': threshold_otimo,
                'especificidade_maxima': spec_maxima,
                'foro_analisado': foro,
                'interpretacao': f'Threshold {threshold_otimo} maximiza especificidade ({spec_maxima:.3f})'
            }
        except Exception as e:
            return {'erro': f'Erro na análise de threshold: {str(e)}'}
    
    def _analisar_contexto(self, caso: Dict) -> Dict:
        """Análise contextual baseada em dados históricos"""
        try:
            # Carregar dados bivariados
            try:
                df_biv = pd.read_csv(f"{self.data_path}/dataset_bivariado_1756659091705.csv")
            except FileNotFoundError:
                df_biv = pd.read_csv(f"{self.data_path}/dataset_bivariado_1756658854794.csv")
            
            foro = caso.get('foro', 'SP')
            area = caso.get('area', 'cível')
            
            # Filtrar dados por contexto
            contexto_filtro = df_biv[
                (df_biv['foro'] == foro) & (df_biv['area'] == area)
            ]
            
            if len(contexto_filtro) > 0:
                sens_media = contexto_filtro['sensibilidade'].mean()
                spec_media = contexto_filtro['especificidade'].mean()
                performance = 'Boa' if (sens_media + spec_media) / 2 > 0.75 else 'Moderada'
            else:
                sens_media = df_biv['sensibilidade'].mean()
                spec_media = df_biv['especificidade'].mean()
                performance = 'Dados insuficientes - usando média geral'
            
            return {
                'foro': foro,
                'area': area,
                'sensibilidade_historica': round(sens_media, 3),
                'especificidade_historica': round(spec_media, 3),
                'performance_geral': performance,
                'interpretacao': f'Foro {foro} em {area}: sens={sens_media:.3f}, spec={spec_media:.3f}'
            }
        except Exception as e:
            return {'erro': f'Erro na análise contextual: {str(e)}'}
    
    def _consolidar_recomendacoes(self, resultado: Dict) -> Dict:
        """Consolida todas as recomendações em uma recomendação final"""
        recom_final = {
            'status': 'sucesso',
            'confianca': 'alta'
        }
        
        # Extrair estratégia principal
        if 'recomendacao_coeficientes' in resultado:
            coef_rec = resultado['recomendacao_coeficientes']
            if 'estrategia_recomendada' in coef_rec:
                recom_final['estrategia_principal'] = coef_rec['estrategia_recomendada']
                recom_final['impacto_esperado'] = coef_rec.get('impacto_esperado', 0)
        
        # Extrair threshold ótimo
        if 'recomendacao_threshold' in resultado:
            thresh_rec = resultado['recomendacao_threshold']
            if 'threshold_otimo' in thresh_rec:
                recom_final['threshold_recomendado'] = thresh_rec['threshold_otimo']
        
        # Extrair contexto
        if 'recomendacao_contextual' in resultado:
            ctx_rec = resultado['recomendacao_contextual']
            recom_final['performance_historica'] = ctx_rec.get('performance_geral', 'N/A')
        
        # Gerar resumo executivo
        recom_final['resumo_executivo'] = self._gerar_resumo_executivo(recom_final)
        
        return recom_final
    
    def _gerar_resumo_executivo(self, recom: Dict) -> str:
        """Gera resumo executivo da recomendação"""
        estrategia = recom.get('estrategia_principal', 'N/A')
        impacto = recom.get('impacto_esperado', 0)
        threshold = recom.get('threshold_recomendado', 'N/A')
        
        resumo = f"Estratégia recomendada: {estrategia}"
        
        if impacto > 0:
            resumo += f" (impacto positivo: +{impacto:.3f})"
        
        if threshold != 'N/A':
            resumo += f". Threshold ótimo: {threshold}"
        
        return resumo
    
    def _interpretar_estrategia(self, estrategia: str) -> str:
        """Interpreta a estratégia recomendada em linguagem jurídica"""
        interpretacoes = {
            'prescricao': 'Arguir prescrição: questionar se o prazo legal para propositura da ação foi ultrapassado',
            'impugnacao_pericia': 'Impugnar perícia: contestar laudos técnicos, metodologia ou qualificação do perito',
            'nulidade_prova': 'Nulidade de prova: questionar legalidade, autenticidade ou cadeia de custódia das evidências',
            'acordo_proposto': 'Proposta de acordo: buscar solução consensual como estratégia de mitigação de riscos',
            'ilegitimidade': 'Ilegitimidade de parte: questionar se a parte contrária tem legitimidade para propor a ação',
            'decadencia': 'Arguir decadência: questionar se o direito material já foi extinto pelo decurso do tempo'
        }
        return interpretacoes.get(estrategia, f'Estratégia não mapeada: {estrategia}')
    
    def gerar_relatorio_caso(self, caso: Dict, caminho: str = None) -> str:
        """Gera relatório completo para um caso específico"""
        if caminho is None:
            caso_id = caso.get('id', 'caso')
            caminho = f'modelos_juridicos/reports/relatorio_{caso_id}.json'
        
        # Gerar recomendação completa
        recomendacao = self.recomendar_estrategia_completa(caso)
        
        # Salvar relatório
        import os
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(recomendacao, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Relatório do caso salvo em: {caminho}")
        return caminho
    
    def comparar_estrategias(self, caso: Dict, estrategias_teste: List[str]) -> Dict:
        """Compara diferentes combinações de estratégias"""
        if not self.coeficientes_conhecidos:
            return {'erro': 'Coeficientes não disponíveis para comparação'}
        
        comparacoes = {}
        
        for estrategia in estrategias_teste:
            if estrategia in self.estrategias_disponiveis:
                coef_key = f'bin__{estrategia}'
                if coef_key in self.coeficientes_conhecidos:
                    comparacoes[estrategia] = {
                        'coeficiente': self.coeficientes_conhecidos[coef_key],
                        'impacto_relativo': 'Alto' if abs(self.coeficientes_conhecidos[coef_key]) > 0.2 else 'Baixo',
                        'recomendado': self.coeficientes_conhecidos[coef_key] > 0
                    }
        
        # Ordenar por coeficiente (impacto esperado)
        estrategias_ordenadas = sorted(
            comparacoes.items(), 
            key=lambda x: x[1]['coeficiente'], 
            reverse=True
        )
        
        return {
            'comparacao_detalhada': comparacoes,
            'ranking_estrategias': estrategias_ordenadas,
            'melhor_opcao': estrategias_ordenadas[0][0] if estrategias_ordenadas else 'N/A'
        }