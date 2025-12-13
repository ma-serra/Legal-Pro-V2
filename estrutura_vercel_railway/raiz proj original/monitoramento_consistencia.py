#!/usr/bin/env python3
"""
Script de Monitoramento Contínuo de Consistência
Monitora em tempo real a consistência entre as duas interfaces
"""

import time
import requests
import json
import os
from datetime import datetime
from urllib.parse import urlparse
import psycopg2

class MonitorConsistencia:
    def __init__(self):
        self.last_check = None
        self.inconsistencies_found = 0
        self.total_checks = 0
        
    def verificar_agente_especifico(self, agente_id=250):
        """Verifica consistência de um agente específico"""
        try:
            # API
            response = requests.get(f"http://localhost:5000/api/especialistas", timeout=10)
            if response.status_code != 200:
                return False, "API indisponível"
            
            data = response.json()
            agente_api = None
            for esp in data.get('especialistas', []):
                if esp['id'] == agente_id:
                    agente_api = esp
                    break
            
            if not agente_api:
                return False, f"Agente {agente_id} não encontrado na API"
            
            # SQL
            database_url = os.environ.get('DATABASE_URL')
            parsed = urlparse(database_url)
            conn = psycopg2.connect(
                host=parsed.hostname,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                port=parsed.port or 5432
            )
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.nome, a.capacidades
                FROM agente_juridico a 
                WHERE a.id = %s AND a.ativo = true
            """, (agente_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not row:
                return False, f"Agente {agente_id} não encontrado no SQL"
            
            nome_sql = row[0]
            capacidades_sql = json.loads(row[1]) if row[1] else []
            
            # Comparar
            if agente_api['nome'] != nome_sql:
                return False, f"Nome diferente: API='{agente_api['nome']}' vs SQL='{nome_sql}'"
            
            if sorted(agente_api['capacidades']) != sorted(capacidades_sql):
                return False, f"Capacidades diferentes"
            
            return True, "Consistente"
            
        except Exception as e:
            return False, f"Erro: {e}"
    
    def verificar_total_agentes(self):
        """Verifica se o total de agentes é igual"""
        try:
            # API
            response = requests.get("http://localhost:5000/api/especialistas", timeout=10)
            total_api = len(response.json().get('especialistas', [])) if response.status_code == 200 else 0
            
            # SQL
            database_url = os.environ.get('DATABASE_URL')
            parsed = urlparse(database_url)
            conn = psycopg2.connect(
                host=parsed.hostname,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                port=parsed.port or 5432
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM agente_juridico WHERE ativo = true")
            total_sql = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return total_api == total_sql, total_api, total_sql
            
        except Exception as e:
            return False, 0, 0
    
    def relatorio_status(self):
        """Gera relatório de status atual"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{'='*60}")
        print(f"🔍 MONITORAMENTO - {timestamp}")
        print(f"{'='*60}")
        
        # Verificar totais
        total_ok, api_total, sql_total = self.verificar_total_agentes()
        print(f"📊 Total de Agentes:")
        print(f"   API: {api_total} | SQL: {sql_total} | {'✅' if total_ok else '❌'}")
        
        # Verificar agente específico (ID 250 - corrigido)
        consistente, msg = self.verificar_agente_especifico(250)
        print(f"🎯 Agente ID 250 (Analista de Ações Constitucionais):")
        print(f"   Status: {'✅' if consistente else '❌'} {msg}")
        
        # Verificar alguns agentes aleatórios
        agentes_teste = [195, 250, 300, 350, 400]  # IDs diversos
        inconsistentes = 0
        
        for agente_id in agentes_teste:
            if agente_id <= sql_total:  # Verificar se existe
                ok, _ = self.verificar_agente_especifico(agente_id)
                if not ok:
                    inconsistentes += 1
        
        print(f"🔍 Amostra Aleatória ({len(agentes_teste)} agentes):")
        print(f"   Consistentes: {len(agentes_teste) - inconsistentes}/{len(agentes_teste)}")
        
        self.total_checks += 1
        if inconsistentes > 0:
            self.inconsistencies_found += 1
        
        print(f"📈 Estatísticas:")
        print(f"   Total de verificações: {self.total_checks}")
        print(f"   Problemas encontrados: {self.inconsistencies_found}")
        print(f"   Taxa de sucesso: {((self.total_checks - self.inconsistencies_found) / self.total_checks * 100):.1f}%")
        
        return total_ok and inconsistentes == 0

def main():
    """Executa monitoramento"""
    monitor = MonitorConsistencia()
    
    print("🚀 Iniciando Monitoramento de Consistência")
    print("⏹️ Pressione Ctrl+C para parar")
    
    try:
        while True:
            status_ok = monitor.relatorio_status()
            
            if status_ok:
                print("✅ Sistema funcionando perfeitamente!")
            else:
                print("⚠️ Problemas detectados - revisar sistema!")
            
            time.sleep(30)  # Verificar a cada 30 segundos
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoramento finalizado")
        print(f"Resumo: {monitor.total_checks} verificações, {monitor.inconsistencies_found} problemas")

if __name__ == "__main__":
    main()