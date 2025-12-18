
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import re

# Configuração DB
DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
os.environ['DATABASE_URL'] = DEFAULT_DB_URL

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ESTRATÉGIA IMPORTAR TUDO APENAS DE models_processos
# models_processos agora é um FACADE que importa de models.py
# Se importarmos de ambos, podemos disparar duplicidade dependendo de como o import system funciona (embora python devesse cachear)
# O problema "Table 'processos' is already defined" sugere que o arquivo models.py está sendo EXECUDADO duas vezes como __main__ ou algo assim?
# Ou sqlalchemy metadata está global e sendo populado por dois caminhos distintos.

from main import create_app, db

# TENTATIVA: Importar apenas de models_processos, que teoricamente tem tudo
try:
    from models_processos import (
        Processo,
        ProcessoTributario,
        Tributo,
        TeseTributaria
    )
    # Tenancy e Client ainda de models_saas
    from models_saas import Client, Tenancy
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    # Fallback to models
    from models import Processo, ProcessoTributario
    from models_saas import Client, Tenancy
    # Dummy classes for Tributo if missing
    class Tributo(db.Model):
        __tablename__ = 'tributos_dummy'
        id_tributo = db.Column(db.Integer, primary_key=True)
    class TeseTributaria(db.Model):
        __tablename__ = 'teses_dummy'
        id_tese = db.Column(db.Integer, primary_key=True)

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('etl_import_v3.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def clean_currency(value):
    if pd.isna(value) or value == '':
        return None
    if isinstance(value, (int, float)):
        return value
    
    value_str = str(value).replace('R$', '').replace(' ', '')
    try:
        if ',' in value_str and '.' in value_str:
            value_str = value_str.replace('.', '').replace(',', '.')
        elif ',' in value_str:
            value_str = value_str.replace(',', '.')
        return float(value_str)
    except:
        return None

def clean_date(value):
    if pd.isna(value) or value == '':
        return None
    try:
        dt = pd.to_datetime(value)
        return dt.to_pydatetime()
    except:
        return None

def get_natureza_id(natureza_str):
    if not natureza_str or pd.isna(natureza_str):
        return 5 # Default Tributário
    
    nat = str(natureza_str).lower()
    
    if 'tribut' in nat: return 5
    if 'cível' in nat or 'civil' in nat: return 13
    if 'trabalh' in nat: return 3
    if 'previdenci' in nat: return 4
    if 'penal' in nat: return 10
    if 'constitucional' in nat: return 15
    if 'administrativ' in nat: return 14
        
    return 5 

def get_status_id(status_str):
    if not status_str or pd.isna(status_str):
        return 1 
        
    st = str(status_str).lower()
    if 'ativo' in st or 'andamento' in st: return 1
    elif 'arquivado' in st or 'encerrado' in st: return 2
    elif 'suspenso' in st: return 3
    return 1

def run_import():
    try:
        excel_path = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
        if not os.path.exists(excel_path):
            logger.error(f"Arquivo não encontrado: {excel_path}")
            return

        logger.info("Iniciando leitura do Excel (v3)...")
        df = pd.read_excel(excel_path)
        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = DEFAULT_DB_URL
        
        with app.app_context():
            logger.info("Contexto da aplicação carregado com sucesso.")
            
            # 1. Garantir Tenancy
            tenancy = Tenancy.query.filter_by(slug='legal-pro-hub').first()
            if not tenancy:
                tenancy = Tenancy(name="Legal Pro Hub Matriz", slug="legal-pro-hub", domain="app", status="active")
                db.session.add(tenancy)
                db.session.commit()
            
            criados = 0
            
            for index, row in df.iterrows():
                try:
                    cnj = str(row.get('numero_cnj', '')).strip() if pd.notna(row.get('numero_cnj')) else None
                    if not cnj: continue # Skip sem CNJ
                    
                    cliente_nome = str(row.get('cliente', 'Cliente Desconhecido')).strip()
                    pasta = f"PROC-{row.get('id', index+1)}"
                    
                    # 2. Cliente
                    client = Client.query.filter_by(name=cliente_nome, tenancy_id=tenancy.id).first()
                    if not client:
                        client = Client(name=cliente_nome, tenancy_id=tenancy.id, status='active')
                        db.session.add(client)
                        db.session.flush()
                    
                    # 3. Processo
                    processo = Processo.query.filter_by(numero_cnj=cnj).first()
                    is_new = False
                    if not processo:
                        is_new = True
                        processo = Processo()
                        processo.data_criacao = datetime.utcnow()
                        import uuid
                        processo.uuid = uuid.uuid4()
                    
                    processo.numero_cnj = cnj
                    processo.pasta = pasta
                    processo.cliente_id = client.id
                    processo.tenant_id = tenancy.id
                    processo.natureza_id = get_natureza_id(row.get('natureza'))
                    processo.status_id = get_status_id(row.get('status'))
                    processo.valor_causa = clean_currency(row.get('valor_causa'))
                    processo.data_distribuicao = clean_date(row.get('data_distribuicao'))
                    
                    titulo = row.get('titulo') if pd.notna(row.get('titulo')) else f"Proc. {cliente_nome}"
                    processo.titulo = titulo
                    processo.autor = str(row.get('autor', ''))[:255]
                    processo.reu = str(row.get('reu', ''))[:255]
                    
                    obs = []
                    if pd.notna(row.get('observacoes')): obs.append(str(row.get('observacoes')))
                    processo.observacao_pasta = "\n".join(obs)
                    
                    db.session.add(processo)
                    db.session.flush()
                    
                    # 4. Tributario
                    if processo.natureza_id == 5:
                        proc_trib = ProcessoTributario.query.filter_by(processo_id=processo.id_processo).first()
                        if not proc_trib:
                            proc_trib = ProcessoTributario(processo_id=processo.id_processo)
                        
                        proc_trib.valor_principal = clean_currency(row.get('valor_imposto'))
                        proc_trib.numero_cda = str(row.get('numero_inscricao', ''))[:100]
                        proc_trib.numero_aiim = str(row.get('auto_infracao', ''))[:100]
                        db.session.add(proc_trib)
                        
                    db.session.commit()
                    if is_new: criados += 1
                    
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Erro item {index}: {e}")
            
            logger.info(f"Sucesso! Criados: {criados}")

    except Exception as fatal:
        print(f"FATAL ERROR V3: {fatal}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_import()
