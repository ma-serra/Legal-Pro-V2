#!/usr/bin/env python3
"""
Auditoria Completa de Segurança do Sistema Multi-Agente Jurídico
Verifica vulnerabilidades, configurações e pontos críticos de segurança
"""

import os
import re
import json
import psycopg2
from datetime import datetime
import hashlib
import secrets

class SecurityAuditor:
    def __init__(self):
        self.vulnerabilities = []
        self.warnings = []
        self.recommendations = []
        self.critical_issues = []
        
    def scan_environment_variables(self):
        """Verifica configurações de variáveis de ambiente"""
        critical_vars = [
            'DATABASE_URL', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY',
            'ASSEMBLYAI_API_KEY', 'SESSION_SECRET'
        ]
        
        missing_vars = []
        weak_secrets = []
        
        for var in critical_vars:
            value = os.environ.get(var)
            if not value:
                missing_vars.append(var)
            elif var == 'SESSION_SECRET' and len(value) < 32:
                weak_secrets.append(f"{var}: muito curta ({len(value)} chars)")
                
        if missing_vars:
            self.critical_issues.append(f"Variáveis críticas ausentes: {missing_vars}")
        
        if weak_secrets:
            self.vulnerabilities.append(f"Secrets fracas: {weak_secrets}")
            
        return {
            'missing_vars': missing_vars,
            'weak_secrets': weak_secrets,
            'status': 'CRÍTICO' if missing_vars or weak_secrets else 'OK'
        }
    
    def scan_database_security(self):
        """Verifica configurações de segurança do banco"""
        try:
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            cursor = conn.cursor()
            
            # Verificar usuários com senhas fracas
            cursor.execute("""
                SELECT username, password_hash 
                FROM user 
                WHERE LENGTH(password_hash) < 60 OR password_hash IS NULL
            """)
            weak_passwords = cursor.fetchall()
            
            # Verificar usuários admin
            cursor.execute("""
                SELECT username, is_admin, active 
                FROM user 
                WHERE is_admin = true
            """)
            admin_users = cursor.fetchall()
            
            # Verificar sessões ativas antigas
            cursor.execute("""
                SELECT COUNT(*) 
                FROM sessao_usuario 
                WHERE created_at < NOW() - INTERVAL '7 days' AND active = true
            """)
            old_sessions = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            if weak_passwords:
                self.vulnerabilities.append(f"Usuários com senhas fracas: {len(weak_passwords)}")
            
            if old_sessions > 0:
                self.warnings.append(f"Sessões antigas ativas: {old_sessions}")
                
            return {
                'weak_passwords': len(weak_passwords),
                'admin_users': len(admin_users),
                'old_sessions': old_sessions,
                'status': 'ATENÇÃO' if weak_passwords or old_sessions > 10 else 'OK'
            }
            
        except Exception as e:
            self.critical_issues.append(f"Erro ao acessar banco: {e}")
            return {'status': 'ERRO', 'error': str(e)}
    
    def scan_file_permissions(self):
        """Verifica permissões de arquivos críticos"""
        critical_files = [
            'app.py', 'main.py', 'models.py', '.env',
            'security_utils.py', 'auth.py'
        ]
        
        permission_issues = []
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                stat_info = os.stat(file_path)
                perms = oct(stat_info.st_mode)[-3:]
                
                # Verificar se arquivo é world-readable/writable
                if perms[-1] != '0':
                    permission_issues.append(f"{file_path}: permissões {perms}")
        
        if permission_issues:
            self.vulnerabilities.append(f"Permissões inseguras: {permission_issues}")
            
        return {
            'issues': permission_issues,
            'status': 'ATENÇÃO' if permission_issues else 'OK'
        }
    
    def scan_code_vulnerabilities(self):
        """Busca vulnerabilidades no código"""
        vulnerable_patterns = {
            'sql_injection': r'f["\'].*SELECT.*{.*}.*["\']',
            'command_injection': r'os\.system\(.*\+.*\)',
            'path_traversal': r'open\(.*\+.*\)',
            'hardcoded_secrets': r'["\'][A-Za-z0-9]{20,}["\']',
            'eval_usage': r'eval\(',
            'exec_usage': r'exec\(',
            'pickle_usage': r'pickle\.loads?\('
        }
        
        code_files = ['app.py', 'main.py', 'models.py', 'auth.py']
        vulnerabilities_found = {}
        
        for file_path in code_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for vuln_type, pattern in vulnerable_patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        if vuln_type not in vulnerabilities_found:
                            vulnerabilities_found[vuln_type] = []
                        vulnerabilities_found[vuln_type].extend([f"{file_path}: {match[:50]}..." for match in matches])
        
        if vulnerabilities_found:
            for vuln_type, instances in vulnerabilities_found.items():
                if vuln_type in ['sql_injection', 'command_injection', 'eval_usage']:
                    self.critical_issues.append(f"{vuln_type.upper()}: {len(instances)} instâncias")
                else:
                    self.warnings.append(f"{vuln_type}: {len(instances)} instâncias")
                    
        return {
            'vulnerabilities': vulnerabilities_found,
            'status': 'CRÍTICO' if any(k in vulnerabilities_found for k in ['sql_injection', 'command_injection', 'eval_usage']) else 'OK'
        }
    
    def scan_api_security(self):
        """Verifica configurações de segurança das APIs"""
        security_checks = {
            'rate_limiting': False,
            'authentication': False,
            'input_validation': False,
            'cors_configured': False,
            'https_enforced': False
        }
        
        # Verificar se Flask-Limiter está configurado
        if os.path.exists('app.py'):
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'flask_limiter' in content.lower():
                    security_checks['rate_limiting'] = True
                if '@login_required' in content or 'login_required' in content:
                    security_checks['authentication'] = True
                if 'request.json' in content and 'validate' in content:
                    security_checks['input_validation'] = True
                if 'CORS' in content or 'cors' in content:
                    security_checks['cors_configured'] = True
                if 'https' in content.lower() or 'ssl' in content.lower():
                    security_checks['https_enforced'] = True
        
        missing_security = [k for k, v in security_checks.items() if not v]
        
        if missing_security:
            self.warnings.append(f"Configurações de segurança ausentes: {missing_security}")
            
        return {
            'configured': security_checks,
            'missing': missing_security,
            'status': 'ATENÇÃO' if len(missing_security) > 2 else 'OK'
        }
    
    def scan_upload_security(self):
        """Verifica segurança do sistema de upload"""
        upload_vulnerabilities = []
        
        if os.path.exists('app.py'):
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Verificar validação de tipos de arquivo
                if 'allowed_file' not in content and 'secure_filename' not in content:
                    upload_vulnerabilities.append("Sem validação de tipos de arquivo")
                
                # Verificar limite de tamanho
                if 'MAX_CONTENT_LENGTH' not in content:
                    upload_vulnerabilities.append("Sem limite de tamanho de arquivo")
                
                # Verificar sanitização de nomes
                if 'secure_filename' not in content:
                    upload_vulnerabilities.append("Sem sanitização de nomes de arquivo")
                
                # Verificar quarentena de uploads
                if 'uploads' in content and 'virus_scan' not in content:
                    upload_vulnerabilities.append("Sem verificação de malware")
        
        if upload_vulnerabilities:
            self.vulnerabilities.append(f"Vulnerabilidades de upload: {upload_vulnerabilities}")
            
        return {
            'vulnerabilities': upload_vulnerabilities,
            'status': 'ATENÇÃO' if upload_vulnerabilities else 'OK'
        }
    
    def scan_logging_security(self):
        """Verifica configurações de logging e auditoria"""
        logging_issues = []
        
        if os.path.exists('app.py'):
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Verificar se senhas podem vazar em logs
                if 'password' in content and 'logging' in content:
                    if 'password.*log' in content.lower():
                        logging_issues.append("Possível vazamento de senhas em logs")
                
                # Verificar logs de auditoria
                if 'login' in content and 'app.logger' not in content:
                    logging_issues.append("Sem logs de auditoria para login")
                
                # Verificar logs de acesso a dados sensíveis
                if 'agente_juridico' in content and 'audit' not in content:
                    logging_issues.append("Sem auditoria de acesso a dados")
        
        if logging_issues:
            self.warnings.append(f"Problemas de logging: {logging_issues}")
            
        return {
            'issues': logging_issues,
            'status': 'ATENÇÃO' if logging_issues else 'OK'
        }
    
    def generate_security_report(self):
        """Gera relatório completo de segurança"""
        print("🔒 AUDITORIA DE SEGURANÇA DO SISTEMA")
        print("=" * 50)
        
        # Executar todas as verificações
        env_result = self.scan_environment_variables()
        db_result = self.scan_database_security()
        file_result = self.scan_file_permissions()
        code_result = self.scan_code_vulnerabilities()
        api_result = self.scan_api_security()
        upload_result = self.scan_upload_security()
        logging_result = self.scan_logging_security()
        
        # Compilar resultados
        report = {
            'timestamp': datetime.now().isoformat(),
            'environment_security': env_result,
            'database_security': db_result,
            'file_permissions': file_result,
            'code_vulnerabilities': code_result,
            'api_security': api_result,
            'upload_security': upload_result,
            'logging_security': logging_result,
            'critical_issues': self.critical_issues,
            'vulnerabilities': self.vulnerabilities,
            'warnings': self.warnings,
            'recommendations': self.recommendations
        }
        
        # Determinar nível de risco geral
        if self.critical_issues:
            risk_level = "CRÍTICO"
            risk_color = "🔴"
        elif len(self.vulnerabilities) > 3:
            risk_level = "Alto"
            risk_color = "🟠"
        elif len(self.warnings) > 5:
            risk_level = "MÉDIO"
            risk_color = "🟡"
        else:
            risk_level = "Baixo"
            risk_color = "🟢"
        
        report['risk_level'] = risk_level
        
        # Exibir resumo
        print(f"\n{risk_color} NÍVEL DE RISCO: {risk_level}")
        print(f"📊 Problemas críticos: {len(self.critical_issues)}")
        print(f"⚠️  Vulnerabilidades: {len(self.vulnerabilities)}")
        print(f"💡 Avisos: {len(self.warnings)}")
        
        if self.critical_issues:
            print(f"\n🚨 PROBLEMAS CRÍTICOS:")
            for issue in self.critical_issues:
                print(f"   • {issue}")
        
        if self.vulnerabilities:
            print(f"\n⚠️  VULNERABILIDADES:")
            for vuln in self.vulnerabilities:
                print(f"   • {vuln}")
        
        if self.warnings:
            print(f"\n💡 AVISOS:")
            for warning in self.warnings[:5]:  # Mostrar apenas os 5 primeiros
                print(f"   • {warning}")
            if len(self.warnings) > 5:
                print(f"   ... e mais {len(self.warnings) - 5} avisos")
        
        # Recomendações de segurança
        self.generate_recommendations()
        
        if self.recommendations:
            print(f"\n🔧 RECOMENDAÇÕES:")
            for rec in self.recommendations:
                print(f"   • {rec}")
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"security_audit_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Relatório detalhado salvo: {filename}")
        
        return report
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos problemas encontrados"""
        if self.critical_issues:
            self.recommendations.append("Corrigir imediatamente todos os problemas críticos")
        
        if any('senha' in str(v).lower() for v in self.vulnerabilities):
            self.recommendations.append("Implementar política de senhas mais forte")
        
        if any('upload' in str(v).lower() for v in self.vulnerabilities):
            self.recommendations.append("Fortalecer validação de uploads")
        
        if any('sql' in str(v).lower() for v in self.vulnerabilities):
            self.recommendations.append("Revisar consultas SQL para prevenir injection")
        
        if len(self.warnings) > 3:
            self.recommendations.append("Implementar monitoramento de segurança contínuo")
        
        self.recommendations.extend([
            "Configurar HTTPS obrigatório",
            "Implementar rate limiting em todas as APIs",
            "Configurar backup automático seguro",
            "Implementar rotação automática de secrets",
            "Configurar monitoramento de intrusão"
        ])

def main():
    """Função principal da auditoria"""
    print("🚀 INICIANDO AUDITORIA DE SEGURANÇA")
    
    auditor = SecurityAuditor()
    report = auditor.generate_security_report()
    
    if report['risk_level'] == 'CRÍTICO':
        print("\n🚨 SISTEMA REQUER ATENÇÃO IMEDIATA!")
    elif report['risk_level'] == 'Alto':
        print("\n⚠️  SISTEMA REQUER CORREÇÕES DE SEGURANÇA")
    elif report['risk_level'] == 'MÉDIO':
        print("\n💡 SISTEMA PODE SER MELHORADO")
    else:
        print("\n✅ SISTEMA COM BOA SEGURANÇA")
    
    return report['risk_level'] not in ['CRÍTICO', 'Alto']

if __name__ == "__main__":
    main()