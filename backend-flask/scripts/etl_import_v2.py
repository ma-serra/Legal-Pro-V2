
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

print("DEBUG: STARTING IMPORT V2...")


# Imports de modelos movidos para dentro de run_import para evitar erro de inicialização prematura


# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('etl_import_v2.log', encoding='utf-8')
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
        return 5 # Default Tributário
    
    nat = str(natureza_str).lower()
    
    if 'tribut' in nat:
        return 5
    elif 'cível' in nat or 'civil' in nat:
        return 13
    elif 'trabalh' in nat:
        return 3
    elif 'previdenci' in nat:
        return 4
    elif 'penal' in nat:
        return 10
    elif 'constitucional' in nat:
        return 15
    elif 'administrativ' in nat:
        return 14
        
    return 5 # Default

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

    from main import create_app
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = DEFAULT_DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        # Imports tardios para evitar problemas de contexto
        from main import db
        from models import (
            Processo, 
            ProcessoTributario, 
            ProcessoTrabalhista, 
            ProcessoCivel
        )
        from models_saas import Client, Tenancy
        try:
            from models_processos import Tributo, TeseTributaria
        except ImportError:
            print("WARNING: Could not import Tributo/TeseTributaria")

        # 1. Garantir Tenancy Principal
        tenancy = Tenancy.query.filter_by(slug='legal-pro-hub').first()
        if not tenancy:
            logger.info("Criando Tenancy padrão 'legal-pro-hub'...")
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

        criados = 0
        atualizados = 0
        erros = 0

        for index, row in df.iterrows():
            try:
                # Extração
                cnj = str(row.get('numero_cnj', '')).strip() if pd.notna(row.get('numero_cnj')) else None
                cliente_nome = str(row.get('cliente', '')).strip() if pd.notna(row.get('cliente')) else "Cliente Desconhecido"
                if not cnj:
                    # Se não tem CNJ, usa ID para gerar algo unico ou pula
                    # logger.warning(f"Linha {index} sem CNJ. Pulando.")
                    # continue
                    pass

                # Pasta
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
                    db.session.flush()

                # 3. Verificar Duplicidade
                processo = None
                if cnj:
                    processo = Processo.query.filter_by(numero_cnj=cnj).first()
                
                is_new = False
                if not processo:
                    is_new = True
                    processo = Processo()
                    processo.data_criacao = datetime.utcnow()
                    processo.uuid = db.text("gen_random_uuid()") # Deixar banco gerar ou python uuid
                    import uuid
                    processo.uuid = uuid.uuid4()

                # 4. Dados Processo
                processo.numero_cnj = cnj
                processo.pasta = pasta
                processo.cliente_id = client.id
                processo.tenant_id = tenancy.id
                
                # Mapeamento de Natureza
                processo.natureza_id = get_natureza_id(row.get('natureza'))
                processo.status_id = get_status_id(row.get('status'))
                
                processo.valor_causa = clean_currency(row.get('valor_causa'))
                processo.data_distribuicao = clean_date(row.get('data_distribuicao'))
                
                titulo_proc = row.get('titulo') 
                if pd.isna(titulo_proc):
                    natureza_texto = row.get('natureza', 'Processo')
                    titulo_proc = f"{natureza_texto} - {cliente_nome}"
                processo.titulo = titulo_proc
                
                processo.autor = str(row.get('autor', ''))[:255] if pd.notna(row.get('autor')) else None
                processo.reu = str(row.get('reu', ''))[:255] if pd.notna(row.get('reu')) else None
                
                obs_list = []
                if pd.notna(row.get('observacoes')): obs_list.append(str(row.get('observacoes')))
                if pd.notna(row.get('descricao')): obs_list.append(str(row.get('descricao')))
                processo.observacao_pasta = "\n".join(obs_list)

                db.session.add(processo)
                db.session.flush()

                # 5. Dados Específicos - Tributário (ID 5)
                # Assumindo que Natureza 5 = Tributário
                if processo.natureza_id == 5: 
                    # Verificar se existe ProcessoTributario
                    proc_trib = ProcessoTributario.query.filter_by(processo_id=processo.id_processo).first()
                    if not proc_trib:
                        proc_trib = ProcessoTributario(processo_id=processo.id_processo)
                    
                    val_principal = clean_currency(row.get('valor_imposto', row.get('valor_principal')))
                    if val_principal:
                        proc_trib.valor_principal = val_principal
                        
                    insc = str(row.get('numero_inscricao', ''))
                    if insc and pd.notna(row.get('numero_inscricao')):
                        proc_trib.numero_cda = insc[:100]
                        
                    aiim = str(row.get('auto_infracao', ''))
                    if aiim and pd.notna(row.get('auto_infracao')):
                        proc_trib.numero_aiim = aiim[:100]
                        
                    db.session.add(proc_trib)

                db.session.commit()
                
                if is_new:
                    criados += 1
                    logger.info(f"Novo Processo: {pasta} ({cnj}) - Nat: {processo.natureza_id}")
                else:
                    atualizados += 1
                    
            except Exception as e:
                db.session.rollback()
                erros += 1
                logger.error(f"Erro linha {index}: {e}")

        logger.info("="*30)
        logger.info(f"Importação Finalizada. Criados: {criados}, Atualizados: {atualizados}, Erros: {erros}")
        logger.info("="*30)

if __name__ == "__main__":
    try:
        run_import()
    except Exception as e:
        print(f"FATAL: {e}")
        import traceback
        traceback.print_exc()
