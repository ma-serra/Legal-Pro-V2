
import os
import psycopg2
import logging

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

def check():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        print("Checking columns in 'client' table...")
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'client'")
        rows = cur.fetchall()
        
        found_tenancy = False
        for r in rows:
            print(f" - {r[0]} ({r[1]})")
            if r[0] == 'tenancy_id':
                found_tenancy = True
                
        if not found_tenancy:
            print("❌ Column 'tenancy_id' MISSING in 'client'")
        else:
            print("✅ Column 'tenancy_id' exists")

    except Exception as e:
        print(e)
    finally:
        if 'conn' in locals(): conn.close()
        
if __name__ == "__main__":
    check()
