#!/usr/bin/env python3
"""
Script para atualizar comarcas e varas dos processos com dados reais
baseados na lista oficial de Varas e Comarcas do Brasil.
"""

import sys
import os
import random
from faker import Faker

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models import ProcessoJuridico

# Configurar Faker para Brasil
fake = Faker('pt_BR')

# Lista de Varas e Comarcas reais baseada no arquivo fornecido
VARAS_COMARCAS_REAIS = [
    # São Paulo (SP)
    ("1ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("2ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("3ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("4ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("5ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("10ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("15ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("20ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("25ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("30ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("35ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    ("40ª Vara Cível São Paulo SP", "São Paulo", "SP"),
    
    # Região Metropolitana de São Paulo
    ("1ª Vara Cível Guarulhos SP", "Guarulhos", "SP"),
    ("2ª Vara Cível Guarulhos SP", "Guarulhos", "SP"),
    ("3ª Vara Cível Guarulhos SP", "Guarulhos", "SP"),
    ("1ª Vara Cível Santo André SP", "Santo André", "SP"),
    ("2ª Vara Cível Santo André SP", "Santo André", "SP"),
    ("1ª Vara Cível São Bernardo do Campo SP", "São Bernardo do Campo", "SP"),
    ("2ª Vara Cível São Bernardo do Campo SP", "São Bernardo do Campo", "SP"),
    ("1ª Vara Cível Osasco SP", "Osasco", "SP"),
    ("2ª Vara Cível Osasco SP", "Osasco", "SP"),
    ("1ª Vara Cível Campinas SP", "Campinas", "SP"),
    ("2ª Vara Cível Campinas SP", "Campinas", "SP"),
    ("3ª Vara Cível Campinas SP", "Campinas", "SP"),
    
    # Interior de São Paulo
    ("1ª Vara Cível Ribeirão Preto SP", "Ribeirão Preto", "SP"),
    ("2ª Vara Cível Ribeirão Preto SP", "Ribeirão Preto", "SP"),
    ("1ª Vara Cível Sorocaba SP", "Sorocaba", "SP"),
    ("2ª Vara Cível Sorocaba SP", "Sorocaba", "SP"),
    ("1ª Vara Cível Santos SP", "Santos", "SP"),
    ("2ª Vara Cível Santos SP", "Santos", "SP"),
    ("1ª Vara Cível São José dos Campos SP", "São José dos Campos", "SP"),
    ("2ª Vara Cível São José dos Campos SP", "São José dos Campos", "SP"),
    ("1ª Vara Cível Bauru SP", "Bauru", "SP"),
    ("1ª Vara Cível Piracicaba SP", "Piracicaba", "SP"),
    ("1ª Vara Cível Jundiaí SP", "Jundiaí", "SP"),
    ("1ª Vara Cível Taubaté SP", "Taubaté", "SP"),
    ("Vara Cível Americana SP", "Americana", "SP"),
    ("Vara Cível São Carlos SP", "São Carlos", "SP"),
    ("Vara Cível Rio Claro SP", "Rio Claro", "SP"),
    ("Vara Cível Limeira SP", "Limeira", "SP"),
    
    # Rio de Janeiro (RJ)
    ("1ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("2ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("5ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("10ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("15ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("20ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("25ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("30ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    ("35ª Vara Cível Rio de Janeiro RJ", "Rio de Janeiro", "RJ"),
    
    # Região Metropolitana do Rio de Janeiro
    ("1ª Vara Cível Niterói RJ", "Niterói", "RJ"),
    ("2ª Vara Cível Niterói RJ", "Niterói", "RJ"),
    ("1ª Vara Cível Duque de Caxias RJ", "Duque de Caxias", "RJ"),
    ("2ª Vara Cível Duque de Caxias RJ", "Duque de Caxias", "RJ"),
    ("1ª Vara Cível São Gonçalo RJ", "São Gonçalo", "RJ"),
    ("2ª Vara Cível São Gonçalo RJ", "São Gonçalo", "RJ"),
    ("1ª Vara Cível Nova Iguaçu RJ", "Nova Iguaçu", "RJ"),
    
    # Interior do Rio de Janeiro
    ("1ª Vara Cível Campos dos Goytacazes RJ", "Campos dos Goytacazes", "RJ"),
    ("1ª Vara Cível Volta Redonda RJ", "Volta Redonda", "RJ"),
    ("1ª Vara Cível Petrópolis RJ", "Petrópolis", "RJ"),
    ("Vara Cível Cabo Frio RJ", "Cabo Frio", "RJ"),
    ("Vara Cível Macaé RJ", "Macaé", "RJ"),
    ("Vara Cível Angra dos Reis RJ", "Angra dos Reis", "RJ"),
    ("Vara Cível Resende RJ", "Resende", "RJ"),
    
    # Minas Gerais (MG)
    ("1ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("2ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("5ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("10ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("15ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("20ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("25ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    ("30ª Vara Cível Belo Horizonte MG", "Belo Horizonte", "MG"),
    
    # Região Metropolitana de Belo Horizonte
    ("1ª Vara Cível Contagem MG", "Contagem", "MG"),
    ("2ª Vara Cível Contagem MG", "Contagem", "MG"),
    ("1ª Vara Cível Betim MG", "Betim", "MG"),
    ("Vara Cível Ribeirão das Neves MG", "Ribeirão das Neves", "MG"),
    
    # Interior de Minas Gerais
    ("1ª Vara Cível Juiz de Fora MG", "Juiz de Fora", "MG"),
    ("2ª Vara Cível Juiz de Fora MG", "Juiz de Fora", "MG"),
    ("1ª Vara Cível Uberlândia MG", "Uberlândia", "MG"),
    ("2ª Vara Cível Uberlândia MG", "Uberlândia", "MG"),
    ("1ª Vara Cível Montes Claros MG", "Montes Claros", "MG"),
    ("1ª Vara Cível Uberaba MG", "Uberaba", "MG"),
    ("Vara Cível Governador Valadares MG", "Governador Valadares", "MG"),
    ("Vara Cível Poços de Caldas MG", "Poços de Caldas", "MG"),
    ("Vara Cível Varginha MG", "Varginha", "MG"),
    ("Vara Cível Divinópolis MG", "Divinópolis", "MG"),
    ("Vara Cível Ipatinga MG", "Ipatinga", "MG"),
    
    # Espírito Santo (ES)
    ("1ª Vara Cível Vitória ES", "Vitória", "ES"),
    ("2ª Vara Cível Vitória ES", "Vitória", "ES"),
    ("3ª Vara Cível Vitória ES", "Vitória", "ES"),
    ("1ª Vara Cível Vila Velha ES", "Vila Velha", "ES"),
    ("2ª Vara Cível Vila Velha ES", "Vila Velha", "ES"),
    ("1ª Vara Cível Serra ES", "Serra", "ES"),
    ("1ª Vara Cível Cariacica ES", "Cariacica", "ES"),
    ("1ª Vara Cível Cachoeiro de Itapemirim ES", "Cachoeiro de Itapemirim", "ES"),
    ("1ª Vara Cível Linhares ES", "Linhares", "ES"),
    ("Vara Cível São Mateus ES", "São Mateus", "ES"),
    ("Vara Cível Colatina ES", "Colatina", "ES"),
    ("Vara Cível Guarapari ES", "Guarapari", "ES"),
    
    # Distrito Federal (DF)
    ("1ª Vara Cível Brasília DF", "Brasília", "DF"),
    ("2ª Vara Cível Brasília DF", "Brasília", "DF"),
    ("5ª Vara Cível Brasília DF", "Brasília", "DF"),
    ("10ª Vara Cível Brasília DF", "Brasília", "DF"),
    ("15ª Vara Cível Brasília DF", "Brasília", "DF"),
    ("20ª Vara Cível Brasília DF", "Brasília", "DF"),
    ("1ª Vara Cível Taguatinga DF", "Taguatinga", "DF"),
    ("2ª Vara Cível Taguatinga DF", "Taguatinga", "DF"),
    ("1ª Vara Cível Ceilândia DF", "Ceilândia", "DF"),
    ("Vara Cível Gama DF", "Gama", "DF"),
    ("Vara Cível Planaltina DF", "Planaltina", "DF"),
    ("Vara Cível Águas Claras DF", "Águas Claras", "DF"),
    
    # Rio Grande do Sul (RS)
    ("1ª Vara Cível Porto Alegre RS", "Porto Alegre", "RS"),
    ("2ª Vara Cível Porto Alegre RS", "Porto Alegre", "RS"),
    ("5ª Vara Cível Porto Alegre RS", "Porto Alegre", "RS"),
    ("10ª Vara Cível Porto Alegre RS", "Porto Alegre", "RS"),
    ("15ª Vara Cível Porto Alegre RS", "Porto Alegre", "RS"),
    ("20ª Vara Cível Porto Alegre RS", "Porto Alegre", "RS"),
    ("1ª Vara Cível Canoas RS", "Canoas", "RS"),
    ("2ª Vara Cível Canoas RS", "Canoas", "RS"),
    ("1ª Vara Cível Novo Hamburgo RS", "Novo Hamburgo", "RS"),
    ("1ª Vara Cível São Leopoldo RS", "São Leopoldo", "RS"),
    ("1ª Vara Cível Caxias do Sul RS", "Caxias do Sul", "RS"),
    ("2ª Vara Cível Caxias do Sul RS", "Caxias do Sul", "RS"),
    ("1ª Vara Cível Pelotas RS", "Pelotas", "RS"),
    ("1ª Vara Cível Santa Maria RS", "Santa Maria", "RS"),
    ("1ª Vara Cível Passo Fundo RS", "Passo Fundo", "RS"),
    ("Vara Cível Rio Grande RS", "Rio Grande", "RS"),
    ("Vara Cível Bagé RS", "Bagé", "RS"),
    ("Vara Cível Uruguaiana RS", "Uruguaiana", "RS"),
]

def atualizar_comarcas_varas():
    """Atualiza todos os processos com comarcas e varas reais."""
    
    print("🏛️ Iniciando atualização de comarcas e varas com dados reais...")
    
    with app.app_context():
        # Buscar todos os processos
        processos = ProcessoJuridico.query.all()
        total_processos = len(processos)
        
        print(f"📊 Total de processos encontrados: {total_processos}")
        
        if total_processos == 0:
            print("❌ Nenhum processo encontrado!")
            return
        
        processos_atualizados = 0
        
        for i, processo in enumerate(processos, 1):
            # Escolher uma vara/comarca aleatória da lista
            vara_comarca = random.choice(VARAS_COMARCAS_REAIS)
            vara, comarca, estado = vara_comarca
            
            # Atualizar os campos
            processo.juizo = vara  # Campo juizo = vara
            processo.comarca = comarca
            processo.estado = estado
            
            # Definir instância baseada no padrão brasileiro
            processo.instancia = "1ª Instância"  # Maioria das varas cíveis são de 1ª instância
            
            processos_atualizados += 1
            
            # Log de progresso a cada 100 processos
            if i % 100 == 0 or i == total_processos:
                print(f"📈 Progresso: {i}/{total_processos} processos ({(i/total_processos)*100:.1f}%)")
                print(f"   📍 Último processo: {vara} - {comarca}/{estado}")
        
        # Salvar todas as alterações
        try:
            db.session.commit()
            print(f"✅ Atualização concluída com sucesso!")
            print(f"📊 {processos_atualizados} processos atualizados com dados reais")
            
            # Mostrar estatísticas por estado
            print("\n📈 Distribuição por estado:")
            for estado in sorted(set([vc[2] for vc in VARAS_COMARCAS_REAIS])):
                count = ProcessoJuridico.query.filter_by(estado=estado).count()
                print(f"   • {estado}: {count} processos")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao salvar no banco: {e}")
            return False
    
    return True

def verificar_dados():
    """Verifica se ainda existem dados genéricos."""
    
    print("\n🔍 Verificando dados genéricos restantes...")
    
    with app.app_context():
        # Verificar comarcas genéricas
        comarcas_genericas = ProcessoJuridico.query.filter(
            ProcessoJuridico.comarca.like('Comarca %')
        ).count()
        
        # Verificar juízos genéricos
        juizos_genericos = ProcessoJuridico.query.filter(
            ProcessoJuridico.juizo.like('Juízo %')
        ).count()
        
        print(f"🔍 Comarcas genéricas restantes: {comarcas_genericas}")
        print(f"🔍 Juízos genéricos restantes: {juizos_genericos}")
        
        if comarcas_genericas == 0 and juizos_genericos == 0:
            print("✅ Todos os dados foram atualizados com sucesso!")
        else:
            print("⚠️ Ainda existem alguns dados genéricos")
        
        # Mostrar amostra dos novos dados
        print("\n📋 Amostra dos dados atualizados:")
        amostras = ProcessoJuridico.query.limit(5).all()
        for processo in amostras:
            print(f"   • {processo.juizo} - {processo.comarca}/{processo.estado}")

if __name__ == "__main__":
    print("🏛️ Sistema de Atualização de Comarcas e Varas Reais")
    print("=" * 60)
    
    # Executar atualização
    if atualizar_comarcas_varas():
        verificar_dados()
    else:
        print("❌ Falha na atualização!")