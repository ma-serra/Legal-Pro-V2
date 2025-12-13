#!/usr/bin/env python3
"""
Monitor de logs em tempo real do sistema de transcrição
"""

import time
import subprocess
import threading
import sys
from datetime import datetime

class LogMonitor:
    def __init__(self):
        self.running = True
        self.log_patterns = {
            'timeout': ['WORKER TIMEOUT', 'SystemExit: 1'],
            'assemblyai': ['assemblyai', 'transcription', 'upload'],
            'errors': ['ERROR', 'CRITICAL', 'Failed'],
            'success': ['✅', 'SUCCESS', 'completed'],
            'api_calls': ['POST', 'GET', 'api.assemblyai.com']
        }
        
    def analyze_line(self, line):
        """Analisa linha do log e categoriza"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line_lower = line.lower()
        
        # Categorizar e colorir saída
        if any(pattern in line for pattern in self.log_patterns['timeout']):
            print(f"\033[91m🚨 [{timestamp}] TIMEOUT: {line}\033[0m")
            
        elif any(pattern in line_lower for pattern in self.log_patterns['assemblyai']):
            if 'error' in line_lower or 'failed' in line_lower:
                print(f"\033[93m⚠️ [{timestamp}] ASSEMBLYAI: {line}\033[0m")
            else:
                print(f"\033[96m🔗 [{timestamp}] ASSEMBLYAI: {line}\033[0m")
                
        elif any(pattern in line for pattern in self.log_patterns['errors']):
            print(f"\033[91m❌ [{timestamp}] ERROR: {line}\033[0m")
            
        elif any(pattern in line for pattern in self.log_patterns['success']):
            print(f"\033[92m✅ [{timestamp}] SUCCESS: {line}\033[0m")
            
        elif any(pattern in line_lower for pattern in self.log_patterns['api_calls']):
            print(f"\033[94m🌐 [{timestamp}] API: {line}\033[0m")
            
        elif 'reloading' in line or 'exiting' in line:
            print(f"\033[95m🔄 [{timestamp}] SYSTEM: {line}\033[0m")
            
        else:
            # Log normal
            print(f"\033[90m📋 [{timestamp}] {line}\033[0m")
    
    def monitor_workflow_logs(self):
        """Monitora logs do workflow em tempo real"""
        print("🔍 Monitorando logs do sistema em tempo real...")
        print("Pressione Ctrl+C para parar\n")
        
        try:
            # Usar docker logs para capturar saída do container
            process = subprocess.Popen(
                ['docker', 'logs', '--follow', '--tail', '20', 'replit-container-name'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            while self.running:
                line = process.stdout.readline()
                if line:
                    self.analyze_line(line.strip())
                    
        except FileNotFoundError:
            # Fallback para logs locais se docker não disponível
            self.monitor_local_logs()
    
    def monitor_local_logs(self):
        """Monitora logs locais como fallback"""
        print("Monitorando logs locais...")
        
        import requests
        import json
        
        # Fazer chamadas periódicas para verificar status
        while self.running:
            try:
                # Testar endpoint de transcrição
                response = requests.get('http://localhost:5000/video/', timeout=5)
                if response.status_code == 200:
                    self.analyze_line("Sistema de transcrição respondendo normalmente")
                else:
                    self.analyze_line(f"Sistema retornou status {response.status_code}")
                    
                # Aguardar 5 segundos
                time.sleep(5)
                
            except requests.exceptions.RequestException as e:
                self.analyze_line(f"Erro na conexão: {str(e)}")
                time.sleep(5)
            except KeyboardInterrupt:
                break
    
    def run(self):
        """Executa o monitor"""
        print("🖥️ Monitor de Logs do Sistema de Transcrição")
        print("=" * 50)
        
        try:
            self.monitor_workflow_logs()
        except KeyboardInterrupt:
            print("\n\n📊 Monitor encerrado pelo usuário")
            self.running = False
        except Exception as e:
            print(f"\n❌ Erro no monitor: {str(e)}")
            self.running = False

if __name__ == "__main__":
    monitor = LogMonitor()
    monitor.run()