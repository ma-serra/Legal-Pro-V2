# ============================================================================
# SISTEMA DE PROCESSOS DINÂMICOS - COMPATIBILIDADE (REDIRECT)
# ============================================================================
# Este arquivo é mantido para compatibilidade com códigos que importam de
# models_processos. Todos os modelos agora residem em models.py.
# Evita erro: "Table 'tributos' is already defined"
# ============================================================================

from models import (
    Processo,
    ProcessoCamposEspecificos,
    ProcessoTributario,
    ProcessoTese,
    ProcessoPrognosticoTributario,
    ProcessoTrabalhista,
    ProcessoPrognosticoTrabalhista,
    ProcessoCivel,
    ProcessoPrognosticoCivel,
    ProcessoAtualizacaoMonetaria,
    # Adicionando classes que estavam duplicadas aqui:
    Tributo,
    TeseTributaria,
    IndiceMonetario,
    HistoricoIndice,
    ConfiguracaoFormulario
)
