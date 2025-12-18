
import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime
import uuid

# Config
DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('etl_sql_final.log', encoding='utf-8')]
)
logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(DB_URL)

def get_natureza_id(natureza_str):
    if not natureza_str or pd.isna(natureza_str): return 5
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
    if not status_str or pd.isna(status_str): return 1 
    st = str(status_str).lower()
    if 'ativo' in st or 'andamento' in st: return 1
    if 'arquivado' in st or 'encerrado' in st: return 2
    if 'suspenso' in st: return 3
    return 1

def clean_curr(val):
    if pd.isna(val) or val == '': return None
    if isinstance(val, (int, float)): return float(val)
    s = str(val).replace('R$', '').replace(' ', '')
    try:
        s = s.replace('.', '').replace(',', '.') if ',' in s and '.' in s else s.replace(',', '.')
        return float(s)
    except: return None

def clean_dt(val):
    if pd.isna(val) or val == '': return None
    try:
        return pd.to_datetime(val)
    except: return None

def run_import():
    excel_path = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
    if not os.path.exists(excel_path):
        logger.error("Arquivo excel não encontrado.")
        return

    logger.info("Lendo Excel...")
    df = pd.read_excel(excel_path)
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 1. Tenancy
        cur.execute("SELECT id FROM tenancy WHERE slug = %s", ('legal-pro-hub',))
        res = cur.fetchone()
        if res:
            tenancy_id = res['id']
        else:
            logger.info("Criando Tenancy...")
            cur.execute("""
                INSERT INTO tenancy (name, slug, domain, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, ('Legal Pro Hub Matriz', 'legal-pro-hub', 'app', 'active'))
            tenancy_id = cur.fetchone()['id']
            conn.commit()
            
        stats = {'created': 0, 'updated': 0, 'errors': 0}
        
        for idx, row in df.iterrows():
            try:
                cnj = row.get('numero_cnj')
                if pd.isna(cnj) or not str(cnj).strip(): continue
                cnj = str(cnj).strip()
                
                # 2. Client
                c_name = str(row.get('cliente', 'Desconhecido')).strip()
                cur.execute("SELECT id FROM client WHERE name = %s AND tenancy_id = %s", (c_name, tenancy_id))
                res_c = cur.fetchone()
                if res_c:
                    client_id = res_c['id']
                else:
                    cur.execute("""
                        INSERT INTO client (name, tenancy_id, status, created_at, updated_at)
                        VALUES (%s, %s, %s, NOW(), NOW())
                        RETURNING id
                    """, (c_name, tenancy_id, 'active'))
                    client_id = cur.fetchone()['id']
                
                # 3. Processo
                cur.execute("SELECT id_processo FROM processos WHERE numero_cnj = %s", (cnj,))
                res_p = cur.fetchone()
                
                pasta_val = f"PROC-{row.get('id', idx)}"
                nat_id = get_natureza_id(row.get('natureza'))
                stat_id = get_status_id(row.get('status'))
                val_causa = clean_curr(row.get('valor_causa'))
                dt_dist = clean_dt(row.get('data_distribuicao'))
                tit = row.get('titulo') or f"Proc. {cnj}"
                autor = str(row.get('autor', ''))[:255]
                reu = str(row.get('reu', ''))[:255]
                obs = str(row.get('observacoes', ''))
                
                if res_p:
                    # Update
                    proc_id = res_p['id_processo']
                    cur.execute("""
                        UPDATE processos SET
                            pasta = %s, natureza_id = %s, status_id = %s,
                            valor_causa = %s, data_distribuicao = %s,
                            titulo = %s, autor = %s, reu = %s, observacao_pasta = %s,
                            data_atualizacao = NOW()
                        WHERE id_processo = %s
                    """, (pasta_val, nat_id, stat_id, val_causa, dt_dist, tit, autor, reu, obs, proc_id))
                    stats['updated'] += 1
                else:
                    # Insert
                    new_uuid = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO processos (
                            uuid, numero_cnj, pasta, natureza_id, status_id,
                            valor_causa, data_distribuicao, titulo, autor, reu, observacao_pasta,
                            cliente_id, tenant_id, data_criacao, data_atualizacao, ativo
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, NOW(), NOW(), true
                        ) RETURNING id_processo
                    """, (new_uuid, cnj, pasta_val, nat_id, stat_id, val_causa, dt_dist, tit, autor, reu, obs, client_id, tenancy_id))
                    proc_id = cur.fetchone()['id_processo']
                    stats['created'] += 1
                
                # 4. Tributario
                if nat_id == 5:
                    cur.execute("SELECT id FROM processo_tributario WHERE processo_id = %s", (proc_id,))
                    res_pt = cur.fetchone()
                    
                    val_princ = clean_curr(row.get('valor_imposto') or row.get('valor_principal'))
                    n_cda = str(row.get('numero_inscricao', ''))[:100]
                    n_aiim = str(row.get('auto_infracao', ''))[:100]
                    
                    if res_pt:
                        cur.execute("""
                            UPDATE processo_tributario SET
                                valor_principal = %s, numero_cda = %s, numero_aiim = %s,
                                ultima_atualizacao = NOW()
                            WHERE processo_id = %s
                        """, (val_princ, n_cda, n_aiim, proc_id))
                    else:
                        cur.execute("""
                            INSERT INTO processo_tributario (
                                processo_id, valor_principal, numero_cda, numero_aiim,
                                data_cadastro, ultima_atualizacao
                            ) VALUES (%s, %s, %s, %s, NOW(), NOW())
                        """, (proc_id, val_princ, n_cda, n_aiim))

                conn.commit()
                
            except Exception as row_err:
                conn.rollback()
                logger.error(f"Erro linha {idx}: {row_err}")
                stats['errors'] += 1
        
        logger.info(f"Fim. Criados: {stats['created']}, Atualizados: {stats['updated']}, Erros: {stats['errors']}")
        
    except Exception as e:
        logger.error(f"Erro Geral: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_import()
