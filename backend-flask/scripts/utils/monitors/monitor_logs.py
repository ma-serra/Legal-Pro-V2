#!/usr/bin/env python3
"""
Monitor de logs em tempo real para identificar e corrigir erros JavaScript e backend
"""

import time
import re
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogMonitor:
    def __init__(self):
        self.error_patterns = {
            'javascript': [
                r"Cannot read properties of null",
                r"TypeError:",
                r"ReferenceError:",
                r"Uncaught",
                r"undefined is not a function",
                r"Cannot read property",
                r"getElementById.*null"
            ],
            'python': [
                r"ERROR:",
                r"Traceback",
                r"AttributeError:",
                r"KeyError:",
                r"TypeError:",
                r"ValueError:",
                r"ImportError:",
                r"NameError:"
            ],
            'api': [
                r"404 Not Found",
                r"500 Internal Server Error",
                r"403 Forbidden",
                r"Connection refused",
                r"timeout",
                r"API key",
                r"authentication failed"
            ]
        }
        
        self.solutions = {
            'getElementById.*null': 'Elemento HTML não encontrado - verificar IDs no template',
            'Cannot read properties of null': 'Tentativa de acessar propriedade de elemento nulo',
            'checked.*undefined': 'Elemento não é checkbox - usar .value para selects',
            'Cannot read property.*checked': 'Elemento select sendo tratado como checkbox',
            'ASSEMBLYAI_API_KEY': 'Chave API AssemblyAI não configurada',
            'Connection refused': 'Serviço não está rodando ou endpoint incorreto',
            '404 Not Found': 'Rota não encontrada - verificar URLs',
            'ImportError': 'Biblioteca não instalada ou importação incorreta'
        }
    
    def analyze_error(self, error_message):
        """Analisa uma mensagem de erro e sugere solução"""
        
        error_type = 'unknown'
        severity = 'low'
        solution = 'Erro não catalogado'
        
        # Identificar tipo de erro
        for error_category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    error_type = error_category
                    severity = 'high' if error_category in ['javascript', 'api'] else 'medium'
                    break
        
        # Buscar solução específica
        for pattern, suggested_solution in self.solutions.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                solution = suggested_solution
                break
        
        return {
            'type': error_type,
            'severity': severity,
            'message': error_message,
            'solution': solution,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_fix_suggestions(self, errors):
        """Gera sugestões de correção baseadas nos erros encontrados"""
        
        fixes = []
        
        for error in errors:
            if 'getElementById' in error['message'] and 'null' in error['message']:
                fixes.append({
                    'file': 'templates/video_transcription.html',
                    'action': 'Verificar se todos os IDs referenciados no JavaScript existem no HTML',
                    'priority': 'high'
                })
            
            elif 'checked' in error['message'] and 'select' in error['message'].lower():
                fixes.append({
                    'file': 'templates/video_transcription.html',
                    'action': 'Substituir .checked por .value em elementos select',
                    'priority': 'high'
                })
            
            elif 'ASSEMBLYAI_API_KEY' in error['message']:
                fixes.append({
                    'file': '.env',
                    'action': 'Configurar ASSEMBLYAI_API_KEY com chave válida',
                    'priority': 'critical'
                })
        
        return fixes
    
    def check_common_issues(self):
        """Verifica problemas comuns conhecidos"""
        
        issues = []
        
        # Verificar se arquivo principal existe
        try:
            with open('templates/video_transcription.html', 'r') as f:
                content = f.read()
                
                # Verificar IDs JavaScript vs HTML
                js_ids = re.findall(r"getElementById\('([^']+)'\)", content)
                html_ids = re.findall(r'id="([^"]+)"', content)
                
                missing_ids = [id_name for id_name in js_ids if id_name not in html_ids]
                if missing_ids:
                    issues.append(f"IDs JavaScript não encontrados no HTML: {missing_ids}")
                
                # Verificar uso de .checked em selects
                if re.search(r"getElementById.*\.checked", content):
                    issues.append("Uso de .checked detectado - verificar se elementos são checkboxes")
        
        except FileNotFoundError:
            issues.append("Arquivo templates/video_transcription.html não encontrado")
        
        return issues
    
    def monitor_realtime(self, duration_seconds=60):
        """Monitora logs em tempo real por um período específico"""
        
        logger.info(f"🔍 Iniciando monitoramento de logs por {duration_seconds} segundos...")
        
        start_time = time.time()
        errors_found = []
        
        while time.time() - start_time < duration_seconds:
            # Verificar problemas comuns
            issues = self.check_common_issues()
            
            for issue in issues:
                if issue not in [e['message'] for e in errors_found]:
                    error_analysis = self.analyze_error(issue)
                    errors_found.append(error_analysis)
                    logger.warning(f"⚠️ Problema detectado: {issue}")
            
            time.sleep(2)
        
        return errors_found
    
    def generate_report(self, errors):
        """Gera relatório detalhado dos erros encontrados"""
        
        if not errors:
            return "✅ Nenhum erro detectado durante o monitoramento"
        
        report = f"\n📊 RELATÓRIO DE MONITORAMENTO ({len(errors)} problemas)\n"
        report += "=" * 60 + "\n\n"
        
        high_priority = [e for e in errors if e['severity'] == 'high']
        medium_priority = [e for e in errors if e['severity'] == 'medium']
        low_priority = [e for e in errors if e['severity'] == 'low']
        
        if high_priority:
            report += "🚨 PRIORIDADE ALTA:\n"
            for error in high_priority:
                report += f"  • {error['message']}\n"
                report += f"    Solução: {error['solution']}\n\n"
        
        if medium_priority:
            report += "⚠️ PRIORIDADE MÉDIA:\n"
            for error in medium_priority:
                report += f"  • {error['message']}\n"
                report += f"    Solução: {error['solution']}\n\n"
        
        # Gerar sugestões de correção
        fixes = self.generate_fix_suggestions(errors)
        if fixes:
            report += "🔧 CORREÇÕES SUGERIDAS:\n"
            for fix in fixes:
                report += f"  • Arquivo: {fix['file']}\n"
                report += f"    Ação: {fix['action']}\n"
                report += f"    Prioridade: {fix['priority']}\n\n"
        
        return report

def main():
    """Função principal de monitoramento"""
    
    monitor = LogMonitor()
    
    # Monitorar por 30 segundos
    logger.info("🔄 Iniciando análise de logs...")
    errors = monitor.monitor_realtime(30)
    
    # Gerar e exibir relatório
    report = monitor.generate_report(errors)
    print(report)
    
    # Status final
    if not errors:
        logger.info("✅ Sistema funcionando sem erros detectados")
    else:
        logger.warning(f"⚠️ {len(errors)} problemas identificados - verifique o relatório acima")

if __name__ == "__main__":
    main()