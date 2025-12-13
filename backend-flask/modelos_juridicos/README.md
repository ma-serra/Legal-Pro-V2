# Módulo de Modelos Jurídicos Estatísticos

## Visão Geral
Sistema completo de análise estatística e recomendações para processos jurídicos integrado ao Legal Pro. Implementa múltiplos modelos estatísticos baseados nos dois projetos Python fornecidos.

## Funcionalidades Principais

### 1. Modelo de Defesa
- **Regressão Logística** para prever probabilidade de vitória
- Análise de 6 estratégias de defesa
- Contextualização por foro e área jurídica
- Métricas de performance (AUC-ROC, acurácia)

### 2. Modelos de Especificidade
- **Regressão Beta**: Análise de especificidade observada
- **GLM Binomial**: Modelagem de TN/N_neg
- **Análise Bayesiana Bivariada**: Correlação sensibilidade vs especificidade
- **Modelo de Scores**: Threshold ótimo por foro

### 3. Sistema de Recomendações
- Recomendações inteligentes de estratégias
- Análise de impacto esperado
- Contexto histórico por foro/área
- Comparação de múltiplas estratégias

### 4. Visualizações
- Gráficos estatísticos interativos
- Dashboard com Plotly
- Matriz de correlação
- Distribuições dos dados

## Dados Base
- **2.000 casos sintéticos** baseados em dados reais
- **6 estratégias de defesa**: prescrição, impugnação de perícia, nulidade de prova, acordo, ilegitimidade, decadência
- **4 foros**: SP, RJ, MG, RS
- **4 áreas jurídicas**: cível, trabalhista, consumidor, agrário

## Rotas Disponíveis
- `/modelos-juridicos/` - Dashboard principal
- `/modelos-juridicos/treinar-modelo` - Interface de treinamento
- `/modelos-juridicos/analisar-especificidade` - Análise de especificidade
- `/modelos-juridicos/recomendar-defesa` - Sistema de recomendações
- `/modelos-juridicos/visualizacoes` - Gráficos e visualizações

## APIs
- `/modelos-juridicos/api/prever-caso` - Previsão de casos via API
- `/modelos-juridicos/api/comparar-estrategias` - Comparação de estratégias

## Como Usar

### 1. Treinamento do Modelo
1. Acesse `/modelos-juridicos/treinar-modelo`
2. Configure o tamanho do conjunto de teste (padrão: 20%)
3. Clique em "Iniciar Treinamento"
4. Visualize métricas de performance

### 2. Análise de Especificidade
1. Acesse `/modelos-juridicos/analisar-especificidade`
2. Selecione os modelos desejados:
   - Regressão Beta
   - GLM Binomial
   - Bayesiano Bivariado
   - Modelo de Scores
3. Execute a análise

### 3. Recomendação de Defesas
1. Acesse `/modelos-juridicos/recomendar-defesa`
2. Preencha dados do caso:
   - Foro, área jurídica, valor da causa
   - Estratégias atuais em uso
3. Obtenha recomendações personalizadas

## Arquivos Principais

### Módulo Core
- `modulo_modelos_juridicos.py` - Classes principais dos modelos
- `recomendador.py` - Sistema de recomendações
- `visualizador.py` - Geração de gráficos

### Integração Flask
- `routes_modelos_juridicos.py` - Rotas e APIs
- `templates/modelos_juridicos/` - Interface web

### Dados
- `data/` - Datasets CSV com dados sintéticos
- `reports/` - Relatórios e gráficos gerados

## Exemplo de Uso via Python

```python
from modelos_juridicos import ModeloDefesa, RecomendadorDefesa

# Treinar modelo
modelo = ModeloDefesa()
resultado = modelo.treinar()
print(f"AUC: {resultado['auc']:.3f}")

# Fazer recomendação
recomendador = RecomendadorDefesa()
caso = {
    'foro': 'SP',
    'area': 'cível',
    'valor_causa': 50000,
    'ano': 2024
}
recomendacao = recomendador.recomendar_estrategia_completa(caso)
print(recomendacao['recomendacao_final']['resumo_executivo'])
```

## Integração com Legal Pro
O módulo está totalmente integrado ao sistema Legal Pro:
- Sistema de autenticação (login_required)
- Permissões por usuário
- Interface consistente com o tema
- Logs e monitoramento

## Métricas Esperadas
- **AUC-ROC**: 0.75 - 0.85
- **Acurácia**: 70% - 80%
- **Tempo de treinamento**: < 30 segundos
- **Tempo de recomendação**: < 5 segundos

## Status
✅ **PRODUÇÃO READY**
- Todos os modelos implementados
- Interface web completa
- APIs funcionais
- Integração com Legal Pro ativa
- Dados sintéticos carregados
- Visualizações funcionando

Desenvolvido em 31/08/2025 - Versão 1.0.0