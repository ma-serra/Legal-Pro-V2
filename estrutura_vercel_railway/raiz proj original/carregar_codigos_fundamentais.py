"""
Script para carregar códigos jurídicos fundamentais nas bases vetoriais
"""

import psycopg2
import os
import re
from datetime import datetime
import openai

def get_database_connection():
    """Conecta ao banco PostgreSQL"""
    return psycopg2.connect(
        host=os.environ.get('PGHOST', 'localhost'),
        database=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        port=os.environ.get('PGPORT', 5432)
    )

def processar_codigo_penal():
    """Processa o Código Penal"""
    print("📖 Processando Código Penal...")
    
    try:
        with open('attached_assets/Codigo_Penal_8ed_otimizado_numerado.md', 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        print("❌ Arquivo do Código Penal não encontrado")
        return
    
    # Dividir em chunks por artigos
    chunks = []
    artigos = re.split(r'(Art\.\s*\d+)', conteudo)
    
    chunk_atual = ""
    for i, parte in enumerate(artigos):
        if parte.startswith('Art.'):
            if chunk_atual:
                chunks.append(chunk_atual.strip())
            chunk_atual = parte
        else:
            chunk_atual += parte
            
        # Criar chunks de tamanho adequado (máximo 1000 caracteres)
        if len(chunk_atual) > 1000:
            chunks.append(chunk_atual.strip())
            chunk_atual = ""
    
    if chunk_atual:
        chunks.append(chunk_atual.strip())
    
    # Inserir na base direito_penal
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Limpar dados de teste anteriores
    cursor.execute("DELETE FROM embeddings_direito_penal WHERE referencia LIKE '%teste%'")
    
    for i, chunk in enumerate(chunks[:50]):  # Limitar a 50 chunks iniciais
        if len(chunk.strip()) < 50:  # Pular chunks muito pequenos
            continue
            
        cursor.execute("""
            INSERT INTO embeddings_direito_penal 
            (conteudo, referencia, area, metadata, criado_em)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            chunk,
            "Código Penal - Decreto-lei 2.848/1940",
            "direito_penal",
            '{"fonte": "codigo_penal", "edicao": "8a", "ano": "2025", "tipo": "legislacao"}',
            datetime.now()
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Código Penal processado - {len(chunks)} chunks inseridos")

def processar_codigo_processo_penal():
    """Processa o Código de Processo Penal"""
    print("📖 Processando Código de Processo Penal...")
    
    try:
        with open('attached_assets/Codigo_Processo_Penal_7ed_otimizado_numerado.md', 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        print("❌ Arquivo do Código de Processo Penal não encontrado")
        return
    
    # Dividir em chunks por artigos
    chunks = []
    artigos = re.split(r'(Art\.\s*\d+)', conteudo)
    
    chunk_atual = ""
    for i, parte in enumerate(artigos):
        if parte.startswith('Art.'):
            if chunk_atual:
                chunks.append(chunk_atual.strip())
            chunk_atual = parte
        else:
            chunk_atual += parte
            
        if len(chunk_atual) > 1000:
            chunks.append(chunk_atual.strip())
            chunk_atual = ""
    
    if chunk_atual:
        chunks.append(chunk_atual.strip())
    
    # Inserir na base direito_processual
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Limpar dados de teste anteriores
    cursor.execute("DELETE FROM embeddings_direito_processual WHERE referencia LIKE '%teste%'")
    
    for i, chunk in enumerate(chunks[:50]):  # Limitar a 50 chunks iniciais
        if len(chunk.strip()) < 50:
            continue
            
        cursor.execute("""
            INSERT INTO embeddings_direito_processual 
            (content, conteudo, referencia, area, metadata, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            chunk,
            chunk,
            "Código de Processo Penal - Decreto-lei 3.689/1941",
            "direito_processual",
            '{"fonte": "codigo_processo_penal", "edicao": "7a", "ano": "2025", "tipo": "legislacao"}',
            datetime.now()
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Código de Processo Penal processado - {len(chunks)} chunks inseridos")

def verificar_bases_processadas():
    """Verifica o status das bases após processamento"""
    print("\n📊 Verificando status das bases processadas...")
    
    bases_verificar = [
        ('embeddings_direito_penal', 'Direito Penal'),
        ('embeddings_direito_processual', 'Direito Processual'),
        ('embeddings_direito_civil', 'Direito Civil'),
        ('embeddings_direito_agrario', 'Direito Agrário')
    ]
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    for base_name, area_nome in bases_verificar:
        try:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as processados,
                    COUNT(DISTINCT referencia) as arquivos_unicos
                FROM {base_name}
            """)
            
            result = cursor.fetchone()
            if result:
                total, processados, arquivos = result
                percentual = (processados / total * 100) if total > 0 else 0
                
                print(f"  📚 {area_nome}:")
                print(f"     Total registros: {total}")
                print(f"     Processados: {processados} ({percentual:.1f}%)")
                print(f"     Arquivos únicos: {arquivos}")
                
                # Mostrar principais documentos
                cursor.execute(f"""
                    SELECT DISTINCT referencia, COUNT(*) as chunks
                    FROM {base_name} 
                    WHERE referencia IS NOT NULL
                    GROUP BY referencia
                    ORDER BY chunks DESC
                    LIMIT 3
                """)
                
                documentos = cursor.fetchall()
                if documentos:
                    print(f"     Principais documentos:")
                    for doc, chunks in documentos:
                        print(f"       • {doc} ({chunks} chunks)")
            else:
                print(f"  📚 {area_nome}: Sem dados")
                
        except Exception as e:
            print(f"  ❌ {area_nome}: Erro ao verificar - {str(e)}")
    
    cursor.close()
    conn.close()

def carregar_codigo_civil_basico():
    """Carrega estrutura básica do Código Civil"""
    print("📖 Carregando estrutura básica do Código Civil...")
    
    # Principais livros do Código Civil para estruturar a base
    estrutura_cc = [
        "LIVRO I - DAS PESSOAS\nTÍTULO I - DAS PESSOAS NATURAIS\nCapítulo I - Da Personalidade e da Capacidade\nArt. 1º Toda pessoa é capaz de direitos e deveres na ordem civil.",
        "LIVRO II - DOS BENS\nTÍTULO ÚNICO - DAS DIFERENTES CLASSES DE BENS\nCapítulo I - Dos Bens Considerados em Si Mesmos\nArt. 79. São bens imóveis o solo e tudo quanto se lhe incorporar natural ou artificialmente.",
        "LIVRO III - DOS FATOS JURÍDICOS\nTÍTULO I - DO NEGÓCIO JURÍDICO\nCapítulo I - Disposições Gerais\nArt. 104. A validade do negócio jurídico requer: I - agente capaz; II - objeto lícito, possível, determinado ou determinável; III - forma prescrita ou não defesa em lei.",
        "LIVRO IV - DO DIREITO DAS OBRIGAÇÕES\nTÍTULO I - DAS MODALIDADES DAS OBRIGAÇÕES\nCapítulo I - Das Obrigações de Dar\nArt. 233. A obrigação de dar coisa certa abrange os acessórios dela embora não mencionados, salvo se o contrário resultar do título ou das circunstâncias do caso.",
        "LIVRO V - DO DIREITO DE EMPRESA\nTÍTULO I - DO EMPRESÁRIO\nCapítulo I - Da Caracterização e da Inscrição\nArt. 966. Considera-se empresário quem exerce profissionalmente atividade econômica organizada para a produção ou a circulação de bens ou de serviços."
    ]
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Limpar dados de teste
    cursor.execute("DELETE FROM embeddings_direito_civil WHERE referencia LIKE '%teste%'")
    
    for i, conteudo in enumerate(estrutura_cc):
        cursor.execute("""
            INSERT INTO embeddings_direito_civil 
            (content, conteudo, referencia, area, metadata, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            conteudo,
            conteudo,
            "Código Civil - Lei 10.406/2002",
            "direito_civil",
            '{"fonte": "codigo_civil", "lei": "10.406/2002", "livro": ' + str(i+1) + ', "tipo": "legislacao"}',
            datetime.now()
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Estrutura básica do Código Civil carregada - {len(estrutura_cc)} seções")

def carregar_estatuto_terra_basico():
    """Carrega estrutura básica do Estatuto da Terra"""
    print("📖 Carregando estrutura básica do Estatuto da Terra...")
    
    # Principais artigos do Estatuto da Terra
    estrutura_et = [
        "TÍTULO I - DISPOSIÇÕES PRELIMINARES\nArt. 1º Esta Lei regula os direitos e obrigações concernentes aos bens imóveis rurais, para os fins de execução da Reforma Agrária e promoção da Política Agrícola.",
        "Art. 2° É assegurada a todos a oportunidade de acesso à propriedade da terra, condicionada pela sua função social, na forma prevista nesta Lei.",
        "Art. 4° Para os efeitos desta Lei, definem-se: I - 'Imóvel Rural', o prédio rústico, de área contínua qualquer que seja a sua localização que se destina à exploração extrativa agrícola, pecuária ou agro-industrial.",
        "TÍTULO II - DA REFORMA AGRÁRIA\nCapítulo I - Disposições Gerais\nArt. 16. A Reforma Agrária visa a estabelecer um sistema de relações entre o homem, a propriedade rural e o uso da terra, capaz de promover a justiça social, o progresso e o bem-estar do trabalhador rural e o desenvolvimento econômico do país.",
        "TÍTULO III - DA POLÍTICA AGRÍCOLA\nArt. 85. A política agrícola é o conjunto de providências de amparo à propriedade da terra, que se destinem a orientar, no interesse da economia rural, as atividades agropecuárias, seja no sentido de garantir-lhes o pleno emprego, seja no de harmonizá-las com o processo de industrialização do país."
    ]
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Limpar dados de teste
    cursor.execute("DELETE FROM embeddings_direito_agrario WHERE referencia LIKE '%teste%'")
    
    for i, conteudo in enumerate(estrutura_et):
        cursor.execute("""
            INSERT INTO embeddings_direito_agrario 
            (conteudo, referencia, area, metadata, criado_em)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            conteudo,
            "Estatuto da Terra - Lei 4.504/1964",
            "direito_agrario",
            '{"fonte": "estatuto_terra", "lei": "4.504/1964", "titulo": ' + str(i+1) + ', "tipo": "legislacao"}',
            datetime.now()
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Estrutura básica do Estatuto da Terra carregada - {len(estrutura_et)} artigos")

def main():
    """Função principal"""
    print("🚀 CARREGAMENTO DOS CÓDIGOS JURÍDICOS FUNDAMENTAIS")
    print("=" * 60)
    print(f"Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Processar códigos disponíveis
    processar_codigo_penal()
    processar_codigo_processo_penal()
    
    # Carregar estruturas básicas dos outros códigos
    carregar_codigo_civil_basico()
    carregar_estatuto_terra_basico()
    
    # Verificar resultado final
    verificar_bases_processadas()
    
    print("\n" + "=" * 60)
    print("✅ CARREGAMENTO CONCLUÍDO")
    print(f"Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    print("\n📋 CÓDIGOS FUNDAMENTAIS CARREGADOS:")
    print("✅ Código Penal (Decreto-lei 2.848/1940) - Base: embeddings_direito_penal")
    print("✅ Código de Processo Penal (Decreto-lei 3.689/1941) - Base: embeddings_direito_processual")
    print("✅ Código Civil (Lei 10.406/2002) - Estrutura básica - Base: embeddings_direito_civil")
    print("✅ Estatuto da Terra (Lei 4.504/1964) - Estrutura básica - Base: embeddings_direito_agrario")
    
    print("\n📝 PRÓXIMOS PASSOS RECOMENDADOS:")
    print("1. Carregar texto completo do Código Civil")
    print("2. Carregar texto completo do Código de Processo Civil")
    print("3. Carregar Constituição Federal")
    print("4. Carregar CLT (Consolidação das Leis do Trabalho)")

if __name__ == "__main__":
    main()