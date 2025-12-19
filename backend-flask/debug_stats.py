import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway'

from main import create_app, db
from models import Processo
from sqlalchemy import func

app = create_app()
with app.app_context():
    try:
        print("1. Count...")
        total = Processo.query.count()
        print(f"   Total: {total}")
        
        print("2. Por natureza...")
        por_natureza = db.session.query(
            Processo.natureza_id,
            func.count(Processo.id_processo).label('count')
        ).group_by(Processo.natureza_id).all()
        print(f"   Result: {por_natureza}")
        
        print("3. Por status...")
        por_status = db.session.query(
            Processo.status_id,
            func.count(Processo.id_processo).label('count')
        ).group_by(Processo.status_id).all()
        print(f"   Result: {por_status}")
        
        print("4. Por risco...")
        por_risco = db.session.query(
            Processo.risco_id,
            func.count(Processo.id_processo).label('count')
        ).group_by(Processo.risco_id).all()
        print(f"   Result: {por_risco}")
        
        print("5. Valores...")
        valores = db.session.query(
            func.sum(Processo.valor_causa).label('total_valor_causa'),
            func.sum(Processo.valor_envolvido).label('total_valor_envolvido'),
            func.sum(Processo.contingencia).label('total_contingencia'),
            func.avg(Processo.valor_causa).label('media_valor_causa')
        ).first()
        print(f"   total_valor_causa: {valores.total_valor_causa}")
        print(f"   total_contingencia: {valores.total_contingencia}")
        
        print("6. Por ano...")
        por_ano = db.session.query(
            func.extract('year', Processo.data_distribuicao).label('ano'),
            func.count(Processo.id_processo).label('count')
        ).filter(Processo.data_distribuicao != None).group_by('ano').order_by('ano').all()
        print(f"   Result: {por_ano}")
        
        print("7. Building JSON response...")
        result = {
            'total_processos': total,
            'por_natureza': {
                int(nat_id) if nat_id else 0: count 
                for nat_id, count in por_natureza
            },
            'por_status': {
                int(status_id) if status_id else 0: count 
                for status_id, count in por_status
            },
            'por_risco': {
                int(risco_id) if risco_id else 0: count 
                for risco_id, count in por_risco
            },
            'valores_financeiros': {
                'total_valor_causa': float(valores.total_valor_causa or 0),
                'total_valor_envolvido': float(valores.total_valor_envolvido or 0),
                'total_contingencia': float(valores.total_contingencia or 0),
                'media_valor_causa': float(valores.media_valor_causa or 0)
            },
            'por_ano': {
                int(ano) if ano else 0: count 
                for ano, count in por_ano if ano is not None
            }
        }
        print("SUCCESS!")
        print(result)
        
    except Exception as e:
        print(f"ERROR at step: {e}")
        import traceback
        traceback.print_exc()
