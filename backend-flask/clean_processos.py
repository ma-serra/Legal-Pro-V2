
import psycopg2
import os

DB_URL = os.environ.get('DATABASE_URL', "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway")

def clean():
    print("Iniciando limpeza da tabela de processos...")
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Deletar tabelas filhas primeiro para evitar FK errors se não for cascade
        print("Apagando tabelas filhas...")
        tables = ['processo_tributario', 'processo_trabalhista', 'processo_civel', 'processo_penal', 'processo_administrativo']
        
        # Verificar quais existem antes de apagar
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        existing_tables = [r[0] for r in cur.fetchall()]
        
        for t in tables:
            if t in existing_tables:
                cur.execute(f"TRUNCATE TABLE {t} CASCADE")
                print(f" - {t} limpa.")
            else:
                print(f" - {t} não existe (ignorado).")

        # Apagar tabela pai
        print("Apagando tabela processos...")
        cur.execute("TRUNCATE TABLE processos CASCADE")
        
        # Resetar sequencia (opcional, mas bom pra "limpeza")
        try:
            cur.execute("ALTER SEQUENCE processos_id_processo_seq RESTART WITH 1")
            print(" - Sequência reiniciada.")
        except Exception as e:
            print(f" - Aviso: Não foi possível resetar sequência: {e}")

        conn.commit()
        print("Limpeza Concluída com Sucesso!")
        conn.close()
        
    except Exception as e:
        print(f"ERRO CRÍTICO NA LIMPEZA: {e}")
        if 'conn' in locals(): conn.rollback()

if __name__ == "__main__":
    clean()
