#!/usr/bin/env python3
"""
Sistema de Sincronização de Bases de Dados - Legal Pro
Sincroniza dados entre Development e Production de forma segura
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseSyncer:
    def __init__(self):
        self.dev_conn = None
        self.prod_conn = None
        
    def connect_databases(self):
        """Conectar às bases de dados Development e Production"""
        try:
            # Development Database
            dev_url = "postgresql://neondb_owner:npg_F3M8RaEktGdQ@ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
            self.dev_conn = psycopg2.connect(dev_url)
            logger.info("✅ Conectado à base Development (Neon)")
            
            # Production Database
            prod_url = "postgresql://neondb_owner:npg_dNFh9jaHLf7k@ep-sweet-boat-af7qtkoo.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
            self.prod_conn = psycopg2.connect(prod_url)
            logger.info("✅ Conectado à base Production (Neon)")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar bases: {str(e)}")
            return False
    
    def get_table_schemas(self, conn, exclude_tables=None):
        """Obter esquemas das tabelas"""
        if exclude_tables is None:
            exclude_tables = ['pg_', 'information_schema']
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                AND table_name NOT LIKE ANY(%s)
                ORDER BY table_name, ordinal_position
            """, (exclude_tables,))
            
            return cur.fetchall()
    
    def compare_schemas(self):
        """Comparar esquemas das bases"""
        logger.info("🔍 Comparando esquemas das bases...")
        
        dev_schema = self.get_table_schemas(self.dev_conn)
        prod_schema = self.get_table_schemas(self.prod_conn)
        
        dev_tables = set(row['table_name'] for row in dev_schema)
        prod_tables = set(row['table_name'] for row in prod_schema)
        
        # Tabelas só em Development
        dev_only = dev_tables - prod_tables
        if dev_only:
            logger.info(f"📊 Tabelas só em Development: {', '.join(dev_only)}")
        
        # Tabelas só em Production
        prod_only = prod_tables - dev_tables
        if prod_only:
            logger.info(f"🏢 Tabelas só em Production: {', '.join(prod_only)}")
        
        # Tabelas comuns
        common_tables = dev_tables & prod_tables
        logger.info(f"🔄 Tabelas comuns: {len(common_tables)}")
        
        return {
            'dev_only': dev_only,
            'prod_only': prod_only,
            'common': common_tables,
            'dev_schema': dev_schema,
            'prod_schema': prod_schema
        }
    
    def sync_table_data(self, table_name, direction='dev_to_prod', backup_first=True):
        """Sincronizar dados de uma tabela específica"""
        logger.info(f"🔄 Sincronizando tabela: {table_name} ({direction})")
        
        try:
            source_conn = self.dev_conn if direction == 'dev_to_prod' else self.prod_conn
            target_conn = self.prod_conn if direction == 'dev_to_prod' else self.dev_conn
            
            # Backup da tabela de destino
            if backup_first:
                self._backup_table(target_conn, table_name)
            
            # Obter dados da fonte
            with source_conn.cursor(cursor_factory=RealDictCursor) as source_cur:
                source_cur.execute(f"SELECT * FROM {table_name}")
                source_data = source_cur.fetchall()
                
                if not source_data:
                    logger.info(f"⚠️ Tabela {table_name} vazia na fonte")
                    return True
            
            # Limpar tabela de destino
            with target_conn.cursor() as target_cur:
                target_cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
                
                # Inserir dados
                if source_data:
                    columns = list(source_data[0].keys())
                    placeholders = ', '.join(['%s'] * len(columns))
                    
                    insert_query = f"""
                        INSERT INTO {table_name} ({', '.join(columns)})
                        VALUES ({placeholders})
                    """
                    
                    for row in source_data:
                        values = [row[col] for col in columns]
                        target_cur.execute(insert_query, values)
                
                target_conn.commit()
                logger.info(f"✅ Sincronizada tabela {table_name}: {len(source_data)} registros")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar {table_name}: {str(e)}")
            if target_conn:
                target_conn.rollback()
            return False
    
    def _backup_table(self, conn, table_name):
        """Criar backup de uma tabela"""
        backup_name = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            with conn.cursor() as cur:
                cur.execute(f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}")
                conn.commit()
                logger.info(f"💾 Backup criado: {backup_name}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao criar backup: {str(e)}")
    
    def sync_critical_tables(self, direction='dev_to_prod'):
        """Sincronizar tabelas críticas do sistema"""
        critical_tables = [
            'user',
            'role', 
            'processo_juridico',
            'analise_processo_ia',
            'assistente_juridico',
            'categoria_assistente',
            'template_juridico'
        ]
        
        logger.info(f"🚀 Iniciando sincronização crítica ({direction})")
        success_count = 0
        
        for table in critical_tables:
            if self._table_exists(self.dev_conn, table) and self._table_exists(self.prod_conn, table):
                if self.sync_table_data(table, direction):
                    success_count += 1
            else:
                logger.warning(f"⚠️ Tabela {table} não existe em uma das bases")
        
        logger.info(f"✅ Sincronização concluída: {success_count}/{len(critical_tables)} tabelas")
        return success_count == len(critical_tables)
    
    def _table_exists(self, conn, table_name):
        """Verificar se tabela existe"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = %s
                )
            """, (table_name,))
            return cur.fetchone()[0]
    
    def generate_sync_report(self):
        """Gerar relatório de sincronização"""
        logger.info("📋 Gerando relatório de sincronização...")
        
        schema_comparison = self.compare_schemas()
        
        # Contar registros em tabelas comuns
        record_counts = {}
        for table in schema_comparison['common']:
            try:
                # Development count
                with self.dev_conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    dev_count = cur.fetchone()[0]
                
                # Production count
                with self.prod_conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    prod_count = cur.fetchone()[0]
                
                record_counts[table] = {
                    'development': dev_count,
                    'production': prod_count,
                    'difference': dev_count - prod_count
                }
                
            except Exception as e:
                logger.warning(f"Erro ao contar registros em {table}: {str(e)}")
        
        # Criar relatório
        report = {
            'timestamp': datetime.now().isoformat(),
            'schema_comparison': {
                'dev_only_tables': list(schema_comparison['dev_only']),
                'prod_only_tables': list(schema_comparison['prod_only']),
                'common_tables': list(schema_comparison['common'])
            },
            'record_counts': record_counts
        }
        
        # Salvar relatório
        report_file = f"sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo: {report_file}")
        return report
    
    def close_connections(self):
        """Fechar conexões"""
        if self.dev_conn:
            self.dev_conn.close()
        if self.prod_conn:
            self.prod_conn.close()
        logger.info("🔐 Conexões fechadas")

def main():
    """Função principal"""
    syncer = DatabaseSyncer()
    
    try:
        # Conectar às bases
        if not syncer.connect_databases():
            logger.error("❌ Falha ao conectar às bases de dados")
            return 1
        
        # Gerar relatório
        report = syncer.generate_sync_report()
        
        # Menu interativo
        while True:
            print("\n" + "="*50)
            print("🔄 SISTEMA DE SINCRONIZAÇÃO - LEGAL PRO")
            print("="*50)
            print("1. Ver relatório de diferenças")
            print("2. Sincronizar Development → Production") 
            print("3. Sincronizar Production → Development")
            print("4. Sincronizar tabela específica")
            print("5. Gerar novo relatório")
            print("0. Sair")
            print("="*50)
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                print("\n📊 RELATÓRIO DE DIFERENÇAS:")
                for table, counts in report['record_counts'].items():
                    dev_count = counts['development']
                    prod_count = counts['production']
                    diff = counts['difference']
                    status = "✅" if diff == 0 else "⚠️" if abs(diff) < 10 else "❌"
                    print(f"{status} {table}: Dev={dev_count}, Prod={prod_count}, Diff={diff:+d}")
            
            elif choice == '2':
                confirm = input("⚠️ Confirma sincronização Dev→Prod? (sim/não): ")
                if confirm.lower() in ['sim', 's', 'yes', 'y']:
                    syncer.sync_critical_tables('dev_to_prod')
            
            elif choice == '3':
                confirm = input("⚠️ Confirma sincronização Prod→Dev? (sim/não): ")
                if confirm.lower() in ['sim', 's', 'yes', 'y']:
                    syncer.sync_critical_tables('prod_to_dev')
            
            elif choice == '4':
                table_name = input("Nome da tabela: ").strip()
                direction = input("Direção (dev_to_prod/prod_to_dev): ").strip()
                syncer.sync_table_data(table_name, direction)
            
            elif choice == '5':
                report = syncer.generate_sync_report()
                print("✅ Novo relatório gerado")
    
    except KeyboardInterrupt:
        logger.info("\n🛑 Operação cancelada pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {str(e)}")
        return 1
    finally:
        syncer.close_connections()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())