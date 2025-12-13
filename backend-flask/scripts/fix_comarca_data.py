#!/usr/bin/env python3
"""
Script simplificado para corrigir dados genéricos de comarcas e varas.
"""

import sys
import os
import random

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models import ProcessoJuridico

# Lista reduzida e focada de varas reais
VARAS_REAIS = [
    # São Paulo
    ("1ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("2ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("5ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("10ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("1ª Vara Cível Guarulhos SP", "Guarulhos", "SP"),
    ("2ª Vara Cível Guarulhos SP", "Guarulhos", "SP"),
    ("1ª Vara Cível Santo André SP", "Santo André", "SP"),
    ("1ª Vara Cível Campinas SP", "Campinas", "SP"),
    ("2ª Vara Cível Campinas SP", "Campinas", "SP"),
    ("1ª Vara Cível Santos SP", "Santos", "SP"),
    ("1ª Vara Cível Ribeirão Preto SP", "Ribeirão Preto", "SP"),
    ("1ª Vara Cível Sorocaba SP", "Sorocaba", "SP"),
    
    # Rio de Janeiro
    ("1ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("2ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("5ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("10ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("1ª Vara Cível Niterói RJ", "Niterói", "RJ"),
    ("2ª Vara Cível Niterói RJ", "Niterói", "RJ"),
    ("1ª Vara Cível Duque de Caxias RJ", "Duque de Caxias", "RJ"),
    ("1ª Vara Cível Nova Iguaçu RJ", "Nova Iguaçu", "RJ"),
    ("Vara Cível Cabo Frio RJ", "Cabo Frio", "RJ"),
    
    # Minas Gerais
    ("1ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("2ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("5ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("1ª Vara Cível Contagem MG", "Contagem", "MG"),
    ("1ª Vara Cível Juiz de Fora MG", "Juiz de Fora", "MG"),
    ("1ª Vara Cível Uberlândia MG", "Uberlândia", "MG"),
    ("Vara Cível Poços de Caldas MG", "Poços de Caldas", "MG"),
    
    # Espírito Santo
    ("1ª Vara Cível Vitória ES", "Vitória", "ES"),
    ("2ª Vara Cível Vitória ES", "Vitória", "ES"),
    ("1ª Vara Cível Vila Velha ES", "Vila Velha", "ES"),
    ("1ª Vara Cível Serra ES", "Serra", "ES"),
    
    # Distrito Federal
    ("1ª Vara Cível Brasília DF", "Brasília", "DF"),
    ("2ª Vara Cível Brasília DF", "Brasília", "DF"),
    ("5ª Vara Cível Brasília DF", "Brasília", "DF"),
    ("1ª Vara Cível Taguatinga DF", "Taguatinga", "DF"),
    ("1ª Vara Cível Ceilândia DF", "Ceilândia", "DF"),
    
    # Rio Grande do Sul
    ("1ª Vara Cível Porto Alegre RS", "Porto Alegre", "RS"),
    ("2ª Vara Cível Porto Alegre RS", "Porto Alegre", "RS"),
    ("5ª Vara Cível Porto Alegre RS", "Porto Alegre", "RS"),
    ("1ª Vara Cível Caxias do Sul RS", "Caxias do Sul", "RS"),
    ("1ª Vara Cível Pelotas RS", "Pelotas", "RS"),
]

def main():
    print("🔧 Correção de dados genéricos - Comarcas e Varas")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Buscar processos com dados genéricos
            processos_genericos = ProcessoJuridico.query.filter(
                (ProcessoJuridico.comarca.like('Comarca %')) |
                (ProcessoJuridico.juizo.like('Juízo %'))
            ).all()
            
            print(f"📊 Processos com dados genéricos: {len(processos_genericos)}")
            
            if len(processos_genericos) == 0:
                print("✅ Nenhum processo com dados genéricos encontrado!")
                return
            
            # Atualizar cada processo
            for i, processo in enumerate(processos_genericos, 1):
                vara_data = random.choice(VARAS_REAIS)
                vara, comarca, estado = vara_data
                
                processo.juizo = vara
                processo.comarca = comarca
                processo.estado = estado
                processo.instancia = "1ª Instância"
                
                if i % 100 == 0:
                    print(f"📈 Processados: {i}/{len(processos_genericos)}")
            
            # Commit das mudanças
            db.session.commit()
            print(f"✅ {len(processos_genericos)} processos atualizados com sucesso!")
            
            # Verificação final
            restantes = ProcessoJuridico.query.filter(
                (ProcessoJuridico.comarca.like('Comarca %')) |
                (ProcessoJuridico.juizo.like('Juízo %'))
            ).count()
            
            print(f"🔍 Processos genéricos restantes: {restantes}")
            
            if restantes == 0:
                print("🎉 Todos os dados foram corrigidos!")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main()