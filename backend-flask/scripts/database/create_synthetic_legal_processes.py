#!/usr/bin/env python3
"""
Script para criar processos jurídicos sintéticos com resultados variados.
Cria 10 processos por área jurídica com dados realistas.
"""
import os
import sys
import random
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database_connection():
    """Obtém conexão com o banco de dados"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        return psycopg2.connect(database_url)
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def get_legal_process_templates():
    """Define templates de processos por área jurídica"""
    
    # Lista de resultados possíveis
    resultados = [
        'Acordo', 'Administrativo', 'Arquivado', 'Ausência', 'Exclusão da Lide',
        'Extinto', 'Improcedente', 'Não é parte', 'Obrigação de fazer', 
        'Procedente', 'Procedente em parte', 'Quitado', 'Sem decisão'
    ]
    
    # Valores monetários por complexidade
    valores_baixo = (5000, 25000)
    valores_medio = (25000, 100000)
    valores_alto = (100000, 500000)
    
    # Estados brasileiros - Sul, Sudeste e Centro-Oeste apenas
    estados = ['SP', 'RJ', 'MG', 'ES', 'RS', 'PR', 'SC', 'GO', 'MT', 'MS', 'DF']
    
    # Cidades principais - Sul, Sudeste e Centro-Oeste apenas
    cidades = {
        'SP': ['São Paulo', 'Campinas', 'Santos', 'Ribeirão Preto', 'Sorocaba', 'São José dos Campos'],
        'RJ': ['Rio de Janeiro', 'Niterói', 'Campos dos Goytacazes', 'Nova Iguaçu', 'Duque de Caxias'],
        'MG': ['Belo Horizonte', 'Uberlândia', 'Juiz de Fora', 'Contagem', 'Montes Claros'],
        'ES': ['Vitória', 'Serra', 'Vila Velha', 'Cariacica', 'Linhares'],
        'RS': ['Porto Alegre', 'Caxias do Sul', 'Santa Maria', 'Pelotas', 'Canoas'],
        'PR': ['Curitiba', 'Londrina', 'Maringá', 'Ponta Grossa', 'Cascavel'],
        'SC': ['Florianópolis', 'Joinville', 'Blumenau', 'Chapecó', 'Criciúma'],
        'GO': ['Goiânia', 'Aparecida de Goiânia', 'Anápolis', 'Rio Verde', 'Luziânia'],
        'MT': ['Cuiabá', 'Várzea Grande', 'Rondonópolis', 'Sinop', 'Tangará da Serra'],
        'MS': ['Campo Grande', 'Dourados', 'Três Lagoas', 'Corumbá', 'Ponta Porã'],
        'DF': ['Brasília', 'Taguatinga', 'Ceilândia', 'Gama', 'Guará']
    }
    
    process_templates = {
        # DIREITO BANCÁRIO
        "Direito Bancário": [
            {
                "numero": "0001234-56.2024.4.03.0001",
                "empresa": "Banco Nacional S.A.",
                "autor": "Maria Silva Santos",
                "cpf": "123.456.789-01",
                "cnpj": "12.345.678/0001-90",
                "advogado_autor": "Dr. João Bancário",
                "advogado_reu": "Dra. Ana Defesa",
                "descricao": "Ação revisional de contrato bancário com alegação de juros abusivos e capitalização indevida em financiamento habitacional.",
                "valor_base": valores_alto,
                "risco": "Alto"
            },
            {
                "numero": "0002345-67.2024.4.03.0002",
                "empresa": "Caixa Econômica Federal",
                "autor": "Carlos Oliveira Lima",
                "cpf": "234.567.890-12",
                "cnpj": "00.360.305/0001-04",
                "advogado_autor": "Dra. Roberta Consumidor",
                "advogado_reu": "Dr. Paulo Bancário",
                "descricao": "Questionamento de tarifa de manutenção de conta e pedido de restituição de valores cobrados indevidamente.",
                "valor_base": valores_medio,
                "risco": "Médio"
            }
        ],
        
        # DIREITO TRABALHISTA
        "Direito Trabalhista": [
            {
                "numero": "0003456-78.2024.5.02.0003",
                "empresa": "Indústria Metalúrgica Ltda",
                "autor": "José Carlos Trabalhador",
                "cpf": "345.678.901-23",
                "cnpj": "23.456.789/0001-01",
                "advogado_autor": "Dr. Sindical Forte",
                "advogado_reu": "Dra. Empresa Defesa",
                "descricao": "Reclamação trabalhista por horas extras não pagas, adicional de insalubridade e diferenças de FGTS.",
                "valor_base": valores_medio,
                "risco": "Alto"
            },
            {
                "numero": "0004567-89.2024.5.02.0004",
                "empresa": "Comércio Varejista S.A.",
                "autor": "Ana Paula Vendedora",
                "cpf": "456.789.012-34",
                "cnpj": "34.567.890/0001-12",
                "advogado_autor": "Dra. Trabalhista Forte",
                "advogado_reu": "Dr. Corporativo Defesa",
                "descricao": "Ação por equiparação salarial e assédio moral no ambiente de trabalho com pedido de indenização.",
                "valor_base": valores_alto,
                "risco": "Alto"
            }
        ],
        
        # DIREITO PENAL
        "Direito Penal": [
            {
                "numero": "0005678-90.2024.8.26.0005",
                "empresa": "Empresa Comercial Ltda",
                "autor": "Ministério Público",
                "cpf": "567.890.123-45",
                "cnpj": "45.678.901/0001-23",
                "advogado_autor": "Dr. Promotor Público",
                "advogado_reu": "Dr. Criminalista Defesa",
                "descricao": "Denúncia por crime contra a ordem econômica e sonegação fiscal com pedido de sequestro de bens.",
                "valor_base": valores_alto,
                "risco": "Alto"
            },
            {
                "numero": "0006789-01.2024.8.26.0006",
                "empresa": "Construtora Urbana S.A.",
                "autor": "Ministério Público",
                "cpf": "678.901.234-56",
                "cnpj": "56.789.012/0001-34",
                "advogado_autor": "Dra. Promotora Criminal",
                "advogado_reu": "Dr. Defensor Criminal",
                "descricao": "Ação penal por crime ambiental e construção irregular em área de preservação permanente.",
                "valor_base": valores_alto,
                "risco": "Alto"
            }
        ],
        
        # DIREITO TRIBUTÁRIO
        "Direito Tributário": [
            {
                "numero": "0007890-12.2024.4.01.0007",
                "empresa": "Importadora Nacional Ltda",
                "autor": "Fazenda Nacional",
                "cpf": "789.012.345-67",
                "cnpj": "67.890.123/0001-45",
                "advogado_autor": "Dr. Procurador Fazenda",
                "advogado_reu": "Dra. Tributarista Defesa",
                "descricao": "Execução fiscal de ICMS não recolhido com aplicação de multa e juros de mora.",
                "valor_base": valores_alto,
                "risco": "Alto"
            },
            {
                "numero": "0008901-23.2024.4.01.0008",
                "empresa": "Tecnologia Digital S.A.",
                "autor": "Receita Federal",
                "cpf": "890.123.456-78",
                "cnpj": "78.901.234/0001-56",
                "advogado_autor": "Dra. Fazenda Pública",
                "advogado_reu": "Dr. Fiscal Defesa",
                "descricao": "Autuação por ISS não recolhido sobre serviços de tecnologia prestados a terceiros.",
                "valor_base": valores_medio,
                "risco": "Médio"
            }
        ],
        
        # DIREITO EMPRESARIAL
        "Direito Empresarial": [
            {
                "numero": "0009012-34.2024.8.26.0009",
                "empresa": "Holding Empresarial S.A.",
                "autor": "Sócio Minoritário Ltda",
                "cpf": "901.234.567-89",
                "cnpj": "89.012.345/0001-67",
                "advogado_autor": "Dr. Societário Autor",
                "advogado_reu": "Dra. Empresarial Defesa",
                "descricao": "Ação de dissolução parcial de sociedade por quebra da affectio societatis e apuração de haveres.",
                "valor_base": valores_alto,
                "risco": "Alto"
            },
            {
                "numero": "0010123-45.2024.8.26.0010",
                "empresa": "Startup Inovação Ltda",
                "autor": "Investidor Anjo S.A.",
                "cpf": "012.345.678-90",
                "cnpj": "90.123.456/0001-78",
                "advogado_autor": "Dra. Venture Capital",
                "advogado_reu": "Dr. Startup Defesa",
                "descricao": "Ação por descumprimento de acordo de investimento e pedido de ressarcimento de aportes.",
                "valor_base": valores_alto,
                "risco": "Médio"
            }
        ],
        
        # DIREITO SECURITÁRIO
        "Direito Securitário": [
            {
                "numero": "0011234-56.2024.8.26.0011",
                "empresa": "Seguradora Nacional S.A.",
                "autor": "Empresa Segurada Ltda",
                "cpf": "123.456.789-02",
                "cnpj": "01.234.567/0001-89",
                "advogado_autor": "Dr. Segurado Defesa",
                "advogado_reu": "Dra. Seguradora Legal",
                "descricao": "Ação de cobrança de indenização securitária negada por alegada má-fé do segurado.",
                "valor_base": valores_alto,
                "risco": "Alto"
            },
            {
                "numero": "0012345-67.2024.8.26.0012",
                "empresa": "Resseguradora Internacional",
                "autor": "Corretora de Seguros S.A.",
                "cpf": "234.567.890-13",
                "cnpj": "12.345.678/0001-91",
                "advogado_autor": "Dra. Corretora Direitos",
                "advogado_reu": "Dr. Resseguros Defesa",
                "descricao": "Disputa sobre comissão de corretagem em operação de resseguro internacional.",
                "valor_base": valores_medio,
                "risco": "Médio"
            }
        ]
    }
    
    return process_templates, resultados, estados, cidades

def create_synthetic_processes():
    """Cria processos sintéticos para todas as áreas"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        process_templates, resultados, estados, cidades = get_legal_process_templates()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🏭 CRIANDO PROCESSOS JURÍDICOS SINTÉTICOS...")
        print("📊 Meta: 10 processos por área jurídica")
        
        total_created = 0
        
        for area_juridica, templates in process_templates.items():
            print(f"\n🎯 ÁREA: {area_juridica}")
            
            # Cria 10 processos por área
            for i in range(10):
                # Seleciona template base (alterna entre os disponíveis)
                template = templates[i % len(templates)]
                
                # Randomiza dados
                estado = random.choice(estados)
                cidade = random.choice(cidades[estado])
                resultado = random.choice(resultados)
                
                # Calcula valores
                valor_min, valor_max = template["valor_base"]
                valor_pedido = round(random.uniform(valor_min, valor_max), 2)
                valor_acordado = round(valor_pedido * random.uniform(0.3, 0.9), 2) if resultado in ['Acordo', 'Procedente em parte'] else 0.0
                valor_condenacao = valor_pedido if resultado == 'Procedente' else valor_acordado if resultado in ['Acordo', 'Procedente em parte'] else 0.0
                
                # Gera datas
                data_ajuizamento = datetime.now() - timedelta(days=random.randint(30, 730))
                data_audiencia = data_ajuizamento + timedelta(days=random.randint(60, 300)) if random.choice([True, False]) else None
                
                # Número do processo único
                numero_processo = f"{(1000000 + total_created):07d}-{random.randint(10,99)}.2024.{random.choice(['4','5','8'])}.{random.randint(10,99)}.{random.randint(1000,9999):04d}"
                
                # Modifica alguns dados para criar variação
                sufixos = [" Júnior", " Senior", " Filho", " Neto", ""]
                novo_autor = template["autor"] + random.choice(sufixos)
                nova_empresa = template["empresa"].replace("Ltda", random.choice(["S.A.", "Ltda", "ME", "EIRELI"]))
                
                # CPF e CNPJ únicos
                cpf_base = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
                cnpj_base = f"{random.randint(10,99)}.{random.randint(100,999)}.{random.randint(100,999)}/0001-{random.randint(10,99)}"
                
                # Vara/tribunal
                vara = f"{random.randint(1,50)}ª Vara {random.choice(['Cível', 'Criminal', 'Trabalhista', 'Federal'])} de {cidade}"
                
                try:
                    cursor.execute("""
                        INSERT INTO processo_juridico 
                        (numero_processo, area_juridica, empresa_reu, nome_autor, cpf_autor, cnpj_reu,
                         advogado_autor, advogado_reu, criado_por, data_ajuizamento, data_audiencia,
                         estado, cidade, vara_tribunal, descricao_caso, valor_pedido, valor_acordado,
                         valor_condenacao, valor_custas, risco_processo, resultado, user_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        numero_processo, area_juridica, nova_empresa, novo_autor, cpf_base, cnpj_base,
                        template["advogado_autor"], template["advogado_reu"], 'Sistema Sintético',
                        data_ajuizamento, data_audiencia, estado, cidade, vara,
                        template["descricao"], valor_pedido, valor_acordado, valor_condenacao, 0.0,
                        template["risco"], resultado, 1
                    ))
                    
                    total_created += 1
                    print(f"   ✅ Processo {total_created}: {numero_processo} - {resultado}")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao criar processo {i+1}: {e}")
                    continue
            
            print(f"   📊 {area_juridica}: Processos criados com variação de resultados")
        
        conn.commit()
        
        print(f"\n🎉 CRIAÇÃO CONCLUÍDA!")
        print(f"📊 Total de processos criados: {total_created}")
        print(f"🎯 Distribuição por resultados:")
        
        # Mostra estatísticas de resultados
        cursor.execute("""
            SELECT resultado, COUNT(*) as quantidade
            FROM processo_juridico 
            WHERE resultado IS NOT NULL
            GROUP BY resultado
            ORDER BY quantidade DESC
        """)
        
        stats = cursor.fetchall()
        for stat in stats:
            print(f"   • {stat['resultado']}: {stat['quantidade']} processos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na criação: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_existing_processes():
    """Atualiza processos existentes com resultados"""
    conn = get_database_connection()
    if not conn:
        return
    
    try:
        _, resultados, _, _ = get_legal_process_templates()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n🔄 ATUALIZANDO PROCESSOS EXISTENTES...")
        
        # Atualiza processos sem resultado
        cursor.execute("""
            UPDATE processo_juridico 
            SET resultado = (ARRAY%s)[1 + (id %% %s)]
            WHERE resultado IS NULL OR resultado = ''
        """, (resultados, len(resultados)))
        
        updated = cursor.rowcount
        conn.commit()
        
        print(f"✅ {updated} processos existentes atualizados com resultados")
        
    except Exception as e:
        print(f"❌ Erro na atualização: {e}")
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 INICIANDO CRIAÇÃO DE PROCESSOS SINTÉTICOS...")
    
    # Atualiza processos existentes
    update_existing_processes()
    
    # Cria novos processos
    if create_synthetic_processes():
        print("\n🎯 Processos sintéticos criados com sucesso!")
        print("📋 Todos os processos agora têm resultados preenchidos!")
    else:
        print("\n❌ Falha na criação!")
        sys.exit(1)

if __name__ == "__main__":
    main()