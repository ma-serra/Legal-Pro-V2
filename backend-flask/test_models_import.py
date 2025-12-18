
import sys
import os
sys.path.append(os.getcwd())
try:
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
        ProcessoAtualizacaoMonetaria
    )
    print("SUCCESS: All models imported from models.py")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"ERROR: {e}")
