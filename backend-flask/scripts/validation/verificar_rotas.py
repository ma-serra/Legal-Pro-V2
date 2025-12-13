#!/usr/bin/env python3
"""
Script para verificar todas as rotas registradas no sistema
"""
import sys
import os

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def listar_rotas():
    """Lista todas as rotas registradas no Flask app"""
    try:
        from main import app
        
        print("🔍 ROTAS REGISTRADAS NO SISTEMA:")
        print("=" * 50)
        
        # Filtrar rotas relacionadas a fluxo/fluxos
        rotas_fluxo = []
        todas_rotas = []
        
        for rule in app.url_map.iter_rules():
            rota_info = f"{list(rule.methods)} {rule.rule}"
            todas_rotas.append(rota_info)
            
            if 'fluxo' in rule.rule.lower():
                rotas_fluxo.append(rota_info)
        
        print(f"📊 Total de rotas encontradas: {len(todas_rotas)}")
        print()
        
        if rotas_fluxo:
            print("🎯 ROTAS RELACIONADAS A FLUXO/FLUXOS:")
            print("-" * 40)
            for rota in rotas_fluxo:
                print(f"  ✓ {rota}")
        else:
            print("⚠️ Nenhuma rota com 'fluxo' encontrada")
        
        print()
        print("🔍 VERIFICAÇÃO ESPECÍFICA:")
        print("-" * 40)
        
        # Verificar se existe rota /fluxo/ (singular - incorreta)
        rota_incorreta_encontrada = False
        for rule in app.url_map.iter_rules():
            if rule.rule == '/fluxo/' or rule.rule.startswith('/fluxo/'):
                print(f"❌ ROTA INCORRETA ENCONTRADA: {list(rule.methods)} {rule.rule}")
                rota_incorreta_encontrada = True
        
        # Verificar se existe rota /fluxos/ (plural - correta)
        rota_correta_encontrada = False
        for rule in app.url_map.iter_rules():
            if rule.rule == '/fluxos/' or rule.rule.startswith('/fluxos/'):
                print(f"✅ ROTA CORRETA ENCONTRADA: {list(rule.methods)} {rule.rule}")
                rota_correta_encontrada = True
        
        if not rota_incorreta_encontrada:
            print("✅ Nenhuma rota '/fluxo/' (singular) encontrada")
        
        if not rota_correta_encontrada:
            print("⚠️ Rota '/fluxos/' (plural) não encontrada")
        
        return rota_incorreta_encontrada, rota_correta_encontrada
        
    except Exception as e:
        print(f"❌ Erro ao verificar rotas: {str(e)}")
        return False, False

if __name__ == "__main__":
    listar_rotas()