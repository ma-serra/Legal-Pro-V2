
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import re

# 1. Configurar Ambiente ANTES de qualquer import do projeto
DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
os.environ['DATABASE_URL'] = DEFAULT_DB_URL
os.environ['FLASK_APP'] = 'main.py'

# Adicionar root ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('etl_v4.log')]
)
logger = logging.getLogger(__name__)

def get_natureza_id(natureza_str):
    """
    Mapeamento solicitado pelo usuário:
    Tributária -> 5
    Cível -> 13
    Trabalhista -> 3
    Previdenciária -> 4
    Penal -> 10
    Constitucional -> 15
    Administrativo -> 14
    """
    if not natureza_str or pd.isna(natureza_str):
        return 5 # Default
    
    nat = str(natureza_str).lower()
    if 'tribut' in nat: return 5
    if 'cível' in nat or 'civil' in nat: return 13
    if 'trabalh' in nat: return 3
    if 'previdenci' in nat: return 4
    if 'penal' in nat: return 10
    if 'constitucional' in nat: return 15
    if 'administrativ' in nat: return 14
    return 5 

def clean_currency(value):
    if pd.isna(value) or value == '': return None
    if isinstance(value, (int, float)): return value
    s = str(value).replace('R$', '').replace(' ', '')
    try:
        s = s.replace('.', '').replace(',', '.') if ',' in s and '.' in s else s.replace(',', '.')
        return float(s)
    except: return None

def clean_date(value):
    if pd.isna(value) or value == '': return None
    try: return pd.to_datetime(value).to_pydatetime()
    except: return None

def run():
    # Deferred imports to avoid module loading issues before app creation
    from main import create_app, db
    
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = DEFAULT_DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        logger.info("App Context Active. Importing models now...")
        
        # Import models INSIDE context check to see if it helps
        # Also, check sys.modules to prevent duplications if possible
        import models
        import models_processos
        import models_saas
        
        # Aliases
        Processo = models.Processo
        ProcessoTributario = models.ProcessoTributario
        Client = models_saas.Client
        Tenancy = models_saas.Tenancy
        
        # models_processos classes
        # Assuming we fixed models_processos.py to have Tributo etc.
        Tributo = getattr(models_processos, 'Tributo', None)
        
        logger.info(f"Models loaded. Processo: {Processo}, Tributo: {Tributo}")

        # ETL Logic
        excel_path = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
        df = pd.read_excel(excel_path)
        logger.info(f"Carregado {len(df)} registros.")

        # Tenancy
        tenancy = Tenancy.query.filter_by(slug='legal-pro-hub').first()
        if not tenancy:
            tenancy = Tenancy(name="Legal Pro Hub Matriz", slug="legal-pro-hub", domain="app", status="active")
            db.session.add(tenancy)
            db.session.commit()
            
        count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                cnj = row.get('numero_cnj')
                if pd.isna(cnj) or not str(cnj).strip(): continue
                cnj = str(cnj).strip()
                
                # Check exist
                proc = Processo.query.filter_by(numero_cnj=cnj).first()
                if not proc:
                    proc = Processo()
                    proc.data_criacao = datetime.utcnow()
                    import uuid
                    proc.uuid = uuid.uuid4()
                    is_new = True
                else:
                    is_new = False
                
                # Update fields
                proc.numero_cnj = cnj
                proc.pasta = f"PROC-{row.get('id', idx)}"
                proc.natureza_id = get_natureza_id(row.get('natureza'))
                proc.valor_causa = clean_currency(row.get('valor_causa'))
                proc.data_distribuicao = clean_date(row.get('data_distribuicao'))
                proc.titulo = row.get('titulo') or f"Proc. {cnj}"
                
                # Client
                c_name = str(row.get('cliente', 'Desconhecido')).strip()
                client = Client.query.filter_by(name=c_name, tenancy_id=tenancy.id).first()
                if not client:
                    client = Client(name=c_name, tenancy_id=tenancy.id, status='active')
                    db.session.add(client)
                    db.session.flush()
                proc.cliente_id = client.id
                proc.tenant_id = tenancy.id
                
                db.session.add(proc)
                db.session.flush()

                # Tributario specifics (using user ID 5)
                if proc.natureza_id == 5:
                    pt = ProcessoTributario.query.filter_by(processo_id=proc.id_processo).first()
                    if not pt:
                        pt = ProcessoTributario(processo_id=proc.id_processo)
                    
                    pt.valor_principal = clean_currency(row.get('valor_imposto', row.get('valor_principal')))
                    pt.numero_cda = str(row.get('numero_inscricao', ''))[:100]
                    pt.numero_aiim = str(row.get('auto_infracao', ''))[:100]
                    db.session.add(pt)

                db.session.commit()
                if is_new: count += 1
                
            except Exception as e:
                db.session.rollback()
                error_count += 1
                logger.error(f"Row {idx} error: {e}")
        
        logger.info(f"DONE. Imported: {count}. Errors: {error_count}")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"FATAL: {e}")
