
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.etl_import_real_data import run_import
import traceback

if __name__ == "__main__":
    try:
        run_import()
    except Exception:
        traceback.print_exc()
