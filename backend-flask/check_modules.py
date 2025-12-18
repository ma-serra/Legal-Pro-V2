
import sys
import os
sys.path.append(os.getcwd())
# Simulate what etl script does
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

try:
    import main
    import models
    # import models_processos # Don't import yet
    
    print("MODULES LOADED:")
    for m in sorted(sys.modules.keys()):
        if 'models' in m:
            print(f" - {m} : {sys.modules[m]}")

except Exception as e:
    print(e)
