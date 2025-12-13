#!/usr/bin/env python3
"""Script simplificado para popular historico_pagamentos"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import app, db
from models import ProcessoJuridico, HistoricoPagamento
from datetime import datetime, timedelta
from decimal import Decimal
import random

TIPOS = ['Honorários Advocatícios', 'Custas Processuais', 'Depósito Judicial', 
         'Acordo', 'Taxa de Recurso', 'Honorários Periciais']
FORMAS = ['PIX', 'Transferência Bancária', 'Boleto', 'Depósito']

with app.app_context():
    print("Iniciando...")
    
    # Limpar tabela
    HistoricoPagamento.query.delete()
    db.session.commit()
    
    processos = ProcessoJuridico.query.all()
    total = 0
    
    for p in processos:
        # 3 a 6 pagamentos por processo
        for i in range(random.randint(3, 6)):
            valor = (p.valor_da_causa or 50000) * random.uniform(0.01, 0.15)
            data = p.data_distribuicao or datetime(2023, 6, 1)
            data = data + timedelta(days=random.randint(0, 500))
            
            pag = HistoricoPagamento(
                processo_id=p.id,
                data_pagamento=data,
                tipo_pagamento=random.choice(TIPOS),
                valor=Decimal(str(round(valor, 2))),
                descricao=f'Pagamento processo {p.numero_processo_cnj}',
                forma_pagamento=random.choice(FORMAS),
                status='Realizado'
            )
            db.session.add(pag)
            total += 1
        
        if p.id % 50 == 0:
            db.session.commit()
            print(f"Processados {p.id} processos...")
    
    db.session.commit()
    print(f"✅ Concluído! {total} pagamentos criados para {len(processos)} processos")
