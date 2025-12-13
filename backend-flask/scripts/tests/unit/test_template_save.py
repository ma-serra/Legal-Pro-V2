#!/usr/bin/env python3
"""
Teste completo do sistema de salvamento de templates
Simula uma edição real e valida todo o fluxo
"""

import requests
import json
import time

def test_template_save_functionality():
    """Testa completamente o sistema de salvamento de templates"""
    
    base_url = "http://localhost:5000"
    template_id = 46  # Template de Recurso em Sentido Estrito
    
    print("🧪 Iniciando teste completo do sistema de salvamento...")
    
    # 1. Verificar se o template existe
    print(f"📋 Verificando template ID {template_id}...")
    try:
        response = requests.get(f"{base_url}/legal-design-pro-v2/api/template/{template_id}")
        if response.status_code != 200:
            print(f"❌ Erro ao buscar template: {response.status_code}")
            return False
        
        template_data = response.json()
        if not template_data.get('success'):
            print(f"❌ Template não encontrado: {template_data}")
            return False
        
        original_content = template_data['template']['conteudo_html']
        print(f"✅ Template encontrado: {template_data['template']['nome']}")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    # 2. Simular uma edição real no conteúdo
    print("✏️ Simulando edição no template...")
    
    # Adicionar timestamp para marcar a edição
    timestamp = int(time.time())
    
    modified_content = f"""
    <div class="document-validation-test" style="border: 2px solid #28a745; padding: 15px; margin: 20px 0; background: #f8fff8;">
        <h3 style="color: #28a745;">✅ TESTE DE VALIDAÇÃO REALIZADO</h3>
        <p><strong>Data/Hora:</strong> {time.strftime('%d/%m/%Y %H:%M:%S')}</p>
        <p><strong>Timestamp:</strong> {timestamp}</p>
        <p><strong>Status:</strong> Sistema de salvamento funcionando corretamente</p>
    </div>
    
    {original_content}
    
    <div class="footer-validation" style="margin-top: 30px; padding: 10px; background: #e8f4fd; border-left: 4px solid #007bff;">
        <p><small>Última validação do sistema: {time.strftime('%d/%m/%Y às %H:%M:%S')}</small></p>
    </div>
    """
    
    # 3. Tentar salvar o conteúdo modificado
    print("💾 Salvando conteúdo modificado...")
    
    save_data = {
        "conteudo_html": modified_content
    }
    
    try:
        response = requests.post(
            f"{base_url}/legal-design-pro-v2/api/template/{template_id}/save",
            headers={'Content-Type': 'application/json'},
            json=save_data
        )
        
        if response.status_code != 200:
            print(f"❌ Erro HTTP ao salvar: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
        
        save_result = response.json()
        if not save_result.get('success'):
            print(f"❌ Erro ao salvar: {save_result}")
            return False
        
        print(f"✅ Salvamento realizado: {save_result['message']}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return False
    
    # 4. Verificar se o salvamento foi persistido
    print("🔍 Verificando persistência dos dados...")
    
    try:
        time.sleep(1)  # Aguardar 1 segundo
        
        response = requests.get(f"{base_url}/legal-design-pro-v2/api/template/{template_id}")
        verify_data = response.json()
        
        if not verify_data.get('success'):
            print(f"❌ Erro na verificação: {verify_data}")
            return False
        
        saved_content = verify_data['template']['conteudo_html']
        
        # Verificar se nossa marcação está presente
        if str(timestamp) in saved_content and "TESTE DE VALIDAÇÃO REALIZADO" in saved_content:
            print("✅ Dados persistidos corretamente no banco!")
            print(f"🔍 Timestamp encontrado: {timestamp}")
            return True
        else:
            print("❌ Dados não foram persistidos corretamente")
            print("Conteúdo salvo não contém nossas modificações")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    """Executa o teste principal"""
    print("=" * 60)
    print("🔧 TESTE DE VALIDAÇÃO DO SISTEMA DE TEMPLATES")
    print("=" * 60)
    
    success = test_template_save_functionality()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de edição e salvamento funcionando corretamente")
        print("✅ Persistência de dados validada")
        print("✅ API respondendo adequadamente")
    else:
        print("❌ TESTES FALHARAM!")
        print("⚠️  Sistema apresenta inconsistências")
        print("🔧 Correções necessárias identificadas")
    
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()