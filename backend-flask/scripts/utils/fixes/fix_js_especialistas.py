#!/usr/bin/env python3
"""
Script para corrigir erros de JavaScript na página especialistas
"""

def fix_especialistas_template():
    """Corrige os erros de JavaScript no template especialistas.html"""
    
    file_path = 'templates/juridico/especialistas.html'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Analisando template especialistas.html...")
        
        # Separar em linhas para análise
        lines = content.split('\n')
        
        # Encontrar áreas problemáticas com base no debug
        problem_areas = []
        
        # Verificar linha 3844 (} catch (err) {)
        if len(lines) > 3843:
            line_3844 = lines[3843].strip()  # linha 3844 (índice 3843)
            print(f"Linha 3844: {line_3844}")
            
        # Verificar linha 4499-4504
        if len(lines) > 4498:
            for i in range(4498, min(4505, len(lines))):
                line_content = lines[i].strip()
                print(f"Linha {i+1}: {line_content}")
        
        # Buscar por padrões de erro comum
        fixed_content = content
        
        # Corrigir chaves extras após try/catch
        fixed_content = fixed_content.replace('} } catch (err) {', '} catch (err) {')
        fixed_content = fixed_content.replace('} } catch (error) {', '} catch (error) {')
        
        # Corrigir chaves duplas consecutivas
        import re
        fixed_content = re.sub(r'}\s*}\s*catch', '} catch', fixed_content)
        fixed_content = re.sub(r';\s*}\s*;', '};', fixed_content)
        
        # Salvar versão corrigida
        backup_file = file_path + '.backup'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Template corrigido! Backup salvo em {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir template: {e}")
        return False

def validate_js_syntax():
    """Valida sintaxe JavaScript usando Node.js se disponível"""
    import subprocess
    import os
    import tempfile
    
    # Extrair JavaScript do template
    file_path = 'templates/juridico/especialistas.html'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair blocos script
        import re
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL)
        
        print(f"📄 Encontrados {len(scripts)} blocos de script")
        
        for i, script_content in enumerate(scripts):
            # Criar arquivo temporário para validação
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
                temp_file.write(script_content)
                temp_file_path = temp_file.name
            
            try:
                # Tentar validar com node.js
                result = subprocess.run(['node', '-c', temp_file_path], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    print(f"✅ Script #{i+1}: Sintaxe válida")
                else:
                    print(f"❌ Script #{i+1}: Erro de sintaxe")
                    print(f"   {result.stderr}")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"⚠️ Script #{i+1}: Validação não disponível (Node.js não encontrado)")
            
            finally:
                os.unlink(temp_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def main():
    print("🔧 CORREÇÃO DE ERROS JAVASCRIPT - ESPECIALISTAS")
    print("="*50)
    
    # Tentar corrigir
    if fix_especialistas_template():
        print("\n🔍 Validando sintaxe...")
        validate_js_syntax()
    else:
        print("❌ Falha na correção")
    
    print("\n✅ Processo finalizado")

if __name__ == "__main__":
    main()