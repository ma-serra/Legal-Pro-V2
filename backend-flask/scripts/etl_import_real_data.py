
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from decimal import Decimal
import logging
import re

import logging
import re

# Configuração DB (Pode ser sobrescrito por variável de ambiente)
# DB URL fornecida: postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway
DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
os.environ['DATABASE_URL'] = DEFAULT_DB_URL
print(f"DEBUG: Pre-import DATABASE_URL set to {os.environ.get('DATABASE_URL')}")

# Adicionar diretório pai ao path para importar main e models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app, db
from models import Processo, ProcessoTributario, ProcessoTrabalhista, ProcessoCivel
from models_saas import Client, Tenancy

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('etl_import_processos.log')
    ]
)
logger = logging.getLogger(__name__)

def clean_currency(value):
    if pd.isna(value) or value == '':
        return None
    if isinstance(value, (int, float)):
        return value
    
    # Remove R$, espaços, pontos de milhar e troca vírgula por ponto
    value_str = str(value).replace('R$', '').replace(' ', '')
    try:
        # Padrão brasileiro: 1.000,00 -> 1000.00
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
        return pd.to_datetime(value).to_pydatetime()
    except:
        return None

def get_natureza_id(natureza_str):
    if not natureza_str or pd.isna(natureza_str):
        return 1 # Default Tributário
    
    nat = str(natureza_str).lower()
    if 'tribut' in nat:
        return 1
    elif 'trabalh' in nat:
        return 2
    elif 'civel' in nat or 'cível' in nat:
        return 3
    return 1 # Default

def get_status_id(status_str):
    if not status_str or pd.isna(status_str):
        return 1 # Default Ativo
        
    st = str(status_str).lower()
    if 'ativo' in st or 'andamento' in st:
        return 1
    elif 'arquivado' in st or 'encerrado' in st:
        return 2
    elif 'suspenso' in st:
        return 3
    return 1

def run_import():
    excel_path = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
    
    if not os.path.exists(excel_path):
        logger.error(f"Arquivo não encontrado: {excel_path}")
        return

    logger.info("Iniciando leitura do Excel...")
    df = pd.read_excel(excel_path)
    logger.info(f"Total de linhas encontradas: {len(df)}")

    # Setup App Context
    os.environ['DATABASE_URL'] = DEFAULT_DB_URL
    print(f"DEBUG: Setting DATABASE_URL to {DEFAULT_DB_URL}")
    print(f"DEBUG: os.environ['DATABASE_URL'] is now {os.environ.get('DATABASE_URL')}")
    
    try:
        app = create_app()
        # Force config just in case main.py logic missed it
        app.config['SQLALCHEMY_DATABASE_URI'] = DEFAULT_DB_URL
        print(f"DEBUG: app.config['SQLALCHEMY_DATABASE_URI'] set to {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    except RuntimeError as e:
        logger.error(f"Failed to create app: {e}")
        # Try to fix app if returned or just fail
        raise e
    
    with app.app_context():
        # 1. Garantir Tenancy Principal
        tenancy = Tenancy.query.filter_by(slug='legal-pro-hub').first()
        if not tenancy:
            logger.info("Criando Tenancy padrão...")
            tenancy = Tenancy(
                name="Legal Pro Hub Matriz",
                slug="legal-pro-hub",
                domain="app.legalprohub.com",
                status="active"
            )
            db.session.add(tenancy)
            db.session.commit()
            logger.info(f"Tenancy criado ID: {tenancy.id}")
        else:
            logger.info(f"Usando Tenancy ID: {tenancy.id}")

        # Contadores
        criados = 0
        atualizados = 0
        erros = 0
        skipped = 0

        for index, row in df.iterrows():
            try:
                # Dados Básicos
                cnj = str(row.get('numero_cnj', '')).strip() if pd.notna(row.get('numero_cnj')) else None
                cliente_nome = str(row.get('cliente', '')).strip() if pd.notna(row.get('cliente')) else "Cliente Desconhecido"
                
                # Gerar Pasta se não existir
                # Usando ID do excel ou sequencial
                pasta_ref = str(row.get('id')) if pd.notna(row.get('id')) else f"IMP-{index+1}"
                pasta = f"PROC-{pasta_ref}"

                # 2. Resolver Cliente
                client = Client.query.filter_by(name=cliente_nome, tenancy_id=tenancy.id).first()
                if not client:
                    client = Client(
                        name=cliente_nome,
                        tenancy_id=tenancy.id,
                        status='active'
                    )
                    db.session.add(client)
                    db.session.flush() # Para ter ID
                    logger.info(f"Cliente criado: {cliente_nome}")
                
                # 3. Verificar Duplicidade (CNJ)
                processo = None
                if cnj:
                    processo = Processo.query.filter_by(numero_cnj=cnj).first()
                
                is_new = False
                if not processo:
                    is_new = True
                    processo = Processo()
                    processo.data_criacao = datetime.utcnow()
                
                # 4. Popula Processo
                processo.numero_cnj = cnj
                processo.pasta = pasta
                processo.cliente_id = client.id
                processo.natureza_id = get_natureza_id(row.get('natureza'))
                processo.status_id = get_status_id(row.get('status'))
                processo.valor_causa = clean_currency(row.get('valor_causa'))
                processo.data_distribuicao = clean_date(row.get('data_distribuicao'))
                processo.comarca_id = None # TODO: Implementar lookup de comarca
                
                # Metadados
                titulo_proc = row.get('titulo') if pd.notna(row.get('titulo')) else f"Processo {client.name}"
                processo.titulo = titulo_proc
                processo.autor = str(row.get('autor', ''))[:255] if pd.notna(row.get('autor')) else None
                processo.reu = str(row.get('reu', ''))[:255] if pd.notna(row.get('reu')) else None
                
                # Observações extras na observação
                obs = []
                if pd.notna(row.get('observacoes')): obs.append(str(row.get('observacoes')))
                if pd.notna(row.get('descricao')): obs.append(str(row.get('descricao')))
                processo.observacao_pasta = "\n".join(obs)

                db.session.add(processo)
                db.session.flush() # Ter ID do processo

                # 5. Dados Específicos por Natureza
                if processo.natureza_id == 1: # Tributário
                    proc_trib = ProcessoTributario.query.filter_by(processo_id=processo.id_processo).first()
                    if not proc_trib:
                        proc_trib = ProcessoTributario(processo_id=processo.id_processo)
                    
                    # Tentar mapear campos tributários específicos se existirem no Excel
                    # Mapa de exemplo baseada nas colunas vistas
                    proc_trib.valor_principal = clean_currency(row.get('valor_imposto', row.get('valor_principal')))
                    proc_trib.numero_cda = str(row.get('numero_inscricao', ''))[:100] if pd.notna(row.get('numero_inscricao')) else None
                    proc_trib.numero_aiim = str(row.get('auto_infracao', ''))[:100] if pd.notna(row.get('auto_infracao')) else None
                    
                    db.session.add(proc_trib)
                
                # Commit a cada registro ou em batch
                db.session.commit()
                
                if is_new:
                    criados += 1
                    logger.info(f"Processo criado: {pasta} ({cliente_nome})")
                else:
                    atualizados += 1
                    logger.info(f"Processo atualizado: {pasta}")
                    
            except Exception as e:
                db.session.rollback()
                erros += 1
                logger.error(f"Erro na linha {index}: {str(e)}")
                continue

        logger.info("="*50)
        logger.info("RESUMO DA IMPORTAÇÃO")
        logger.info(f"Criados: {criados}")
        logger.info(f"Atualizados: {atualizados}")
        logger.info(f"Erros: {erros}")
        logger.info("="*50)

if __name__ == "__main__":
    try:
        print("Starting ETL Process...")
        run_import()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
