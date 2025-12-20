
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from decimal import Decimal
import logging
import re

# Configuração DB (Pode ser sobrescrito por variável de ambiente)
DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
os.environ['DATABASE_URL'] = DEFAULT_DB_URL

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
        return pd.to_datetime(value).to_pydatetime()
    except:
        return None

def get_natureza_id(natureza_str):
    if not natureza_str or pd.isna(natureza_str):
        # logger.warning(f"Natureza Vazia/Null. Valor original: {natureza_str}")
        return 1 # Default Tributário se vazio (ou 14 Adm?)
    
    nat = str(natureza_str).lower().strip()
    
    if 'tribut' in nat or 'fiscal' in nat or 'execução fiscal' in nat:
        return 1
    elif 'trabalh' in nat or 'reclama' in nat or 'tst' in nat:
        return 2
    elif 'civel' in nat or 'cível' in nat or 'civil' in nat or 'indeniza' in nat or 'monit' in nat or 'busca' in nat:
        return 3
    elif 'penal' in nat or 'crime' in nat:
        return 10
    elif 'administ' in nat:
        return 14
    elif 'const' in nat:
        return 15
    elif 'previd' in nat:
        return 4
    
    # logger.warning(f"Natureza não identificada: '{nat}'. Usando Default (1).")
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
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        logger.error(f"Erro ao ler Excel: {e}")
        return
        
    logger.info(f"Total de linhas encontradas: {len(df)}")

    try:
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = DEFAULT_DB_URL
    except RuntimeError as e:
        logger.error(f"Failed to create app: {e}")
        raise e
    
    # Bypass ORM for Client/Tenancy due to ProgrammingError
    # Get or Create default client via SQL
    client_id_map = {}
    default_client_id = None
    
    try:
        import psycopg2
        conn = psycopg2.connect(DEFAULT_DB_URL)
        cur = conn.cursor()
        
        # Ensure Tenancy
        cur.execute("INSERT INTO tenancy (name, slug, domain, status) VALUES ('Legal Pro Hub', 'legal-pro-hub', 'app.legalprohub.com', 'active') ON CONFLICT (slug) DO UPDATE SET name=EXCLUDED.name RETURNING id")
        tenancy_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Tenancy ID: {tenancy_id}")
        
        # Load existing clients
        cur.execute("SELECT name, id FROM client WHERE tenancy_id = %s", (tenancy_id,))
        for r in cur.fetchall():
            client_id_map[r[0]] = r[1]
            
        default_client_id = list(client_id_map.values())[0] if client_id_map else None
        
        conn.close()
    except Exception as e:
        logger.error(f"SQL Fallback failed: {e}")
        # Continue and try to fail gracefully inside loop
    
    with app.app_context():
        # Contadores
        criados = 0
        atualizados = 0
        erros = 0

        for index, row in df.iterrows():
            try:
                # Dados Básicos
                cnj = str(row.get('numero_cnj', '')).strip() if pd.notna(row.get('numero_cnj')) else None
                cliente_nome = str(row.get('cliente', '')).strip() if pd.notna(row.get('cliente')) else "Cliente Desconhecido"
                
                pasta_ref = str(row.get('id')) if pd.notna(row.get('id')) else f"IMP-{index+1}"
                pasta = f"PROC-{pasta_ref}"

                # 2. Resolver Cliente (via Map ou SQL)
                cid = client_id_map.get(cliente_nome)
                if not cid:
                    # Create via SQL inside loop (slow but safe)
                    try:
                        conn2 = psycopg2.connect(DEFAULT_DB_URL)
                        cur2 = conn2.cursor()
                        cur2.execute("INSERT INTO client (name, tenancy_id, status) VALUES (%s, %s, 'active') RETURNING id", (cliente_nome, tenancy_id))
                        cid = cur2.fetchone()[0]
                        conn2.commit()
                        conn2.close()
                        client_id_map[cliente_nome] = cid
                        logger.info(f"Cliente criado (SQL): {cliente_nome}")
                    except Exception as e2:
                        logger.error(f"Erro criando cliente {cliente_nome}: {e2}")
                        cid = default_client_id # Fallback
                
                # 3. Verificar Duplicidade
                processo = None
                if cnj:
                    processo = Processo.query.filter_by(numero_cnj=cnj).first()
                if not processo:
                    processo = Processo.query.filter_by(pasta=pasta).first()
                
                is_new = False
                if not processo:
                    is_new = True
                    processo = Processo()
                    processo.data_criacao = datetime.utcnow()
                
                # 4. Popula Processo
                processo.numero_cnj = cnj
                processo.pasta = pasta
                processo.cliente_id = cid # Usa ID resolvido via SQL
                processo.natureza_id = get_natureza_id(row.get('natureza'))
                processo.status_id = get_status_id(row.get('status'))
                processo.valor_causa = clean_currency(row.get('valor_causa'))
                processo.data_distribuicao = clean_date(row.get('data_distribuicao'))
                
                titulo_proc = row.get('titulo') if pd.notna(row.get('titulo')) else f"Processo {client.name}"
                processo.titulo = titulo_proc
                processo.autor = str(row.get('autor', ''))[:255] if pd.notna(row.get('autor')) else None
                processo.reu = str(row.get('reu', ''))[:255] if pd.notna(row.get('reu')) else None
                
                obs = []
                if pd.notna(row.get('observacoes')): obs.append(str(row.get('observacoes')))
                if pd.notna(row.get('descricao')): obs.append(str(row.get('descricao')))
                processo.observacao_pasta = "\n".join(obs)

                db.session.add(processo)
                db.session.flush()

                # 5. Dados Específicos por Natureza
                if processo.natureza_id == 1: # Tributário
                    proc_trib = ProcessoTributario.query.filter_by(processo_id=processo.id_processo).first()
                    if not proc_trib:
                        proc_trib = ProcessoTributario(processo_id=processo.id_processo)
                    
                    proc_trib.valor_principal = clean_currency(row.get('valor_imposto', row.get('valor_principal')))
                    proc_trib.numero_cda = str(row.get('numero_inscricao', ''))[:100] if pd.notna(row.get('numero_inscricao')) else None
                    proc_trib.numero_aiim = str(row.get('auto_infracao', ''))[:100] if pd.notna(row.get('auto_infracao')) else None
                    db.session.add(proc_trib)
                    
                elif processo.natureza_id == 2: # Trabalhista
                    proc_trab = ProcessoTrabalhista.query.filter_by(processo_id=processo.id_processo).first()
                    if not proc_trab:
                        proc_trab = ProcessoTrabalhista(processo_id=processo.id_processo)
                    db.session.add(proc_trab)

                elif processo.natureza_id == 3: # Cível
                    proc_civ = ProcessoCivel.query.filter_by(processo_id=processo.id_processo).first()
                    if not proc_civ:
                        proc_civ = ProcessoCivel(processo_id=processo.id_processo)
                    db.session.add(proc_civ)
                
                db.session.commit()
                
                if is_new:
                    criados += 1
                else:
                    atualizados += 1
                    
            except Exception as e:
                db.session.rollback()
                erros += 1
                logger.error(f"Erro na linha {index}: {str(e)}")
                continue

        logger.info("="*50)
        logger.info(f"IMPORTACAO CONCLUIDA. Criados: {criados}, Atualizados: {atualizados}, Erros: {erros}")
        logger.info("="*50)

if __name__ == "__main__":
    try:
        run_import()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
