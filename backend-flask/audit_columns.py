import pandas as pd
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway'

# 1. Colunas do Excel ETL
df = pd.read_excel(r'D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx', nrows=1)
print('=' * 60)
print('COLUNAS DO EXCEL ETL (Tabela_Processos_ETL.xlsx)')
print('=' * 60)
for i, col in enumerate(df.columns, 1):
    print(f'{i:2}. {col}')
print(f'\nTotal: {len(df.columns)} colunas')

# 2. Colunas da tabela processos no banco
print('\n' + '=' * 60)
print('COLUNAS DA TABELA processos NO BANCO')
print('=' * 60)

from main import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('processos')
    for i, col in enumerate(columns, 1):
        print(f"{i:2}. {col['name']} ({col['type']})")
    print(f'\nTotal: {len(columns)} colunas na tabela processos')
