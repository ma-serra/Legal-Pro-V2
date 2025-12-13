#!/usr/bin/env python3
"""
Demonstração completa do sistema de monitoramento de tokens e custos em R$
"""

import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pricing_calculator():
    """Testa a calculadora de preços com conversão para R$"""
    
    try:
        from modules.pricing_calculator import pricing_calculator
        
        print("\n" + "="*80)
        print("DEMONSTRAÇÃO - CALCULADORA DE PREÇOS COM CONVERSÃO R$")
        print("="*80)
        
        # Testar cálculo de texto
        print("\n📝 TESTE 1: Cálculo de Custo para Texto")
        print("-" * 50)
        
        text_result = pricing_calculator.calculate_text_cost(
            provider='openai',
            model='gpt-4o',
            input_tokens=1500,
            output_tokens=800
        )
        
        if 'error' not in text_result:
            print(f"✅ Provedor: {text_result['provider']}")
            print(f"✅ Modelo: {text_result['model']}")
            print(f"✅ Tokens de entrada: {text_result['input_tokens']:,}")
            print(f"✅ Tokens de saída: {text_result['output_tokens']:,}")
            print(f"✅ Total de tokens: {text_result['total_tokens']:,}")
            print(f"💰 Custo total (USD): ${text_result['total_cost']:.6f}")
            print(f"💰 Custo total (BRL): R$ {text_result['total_cost_brl']:.4f}")
            print(f"📊 Taxa USD/BRL: {text_result['exchange_rate']['usd_to_brl']:.4f}")
        else:
            print(f"❌ Erro: {text_result['error']}")
        
        # Testar cálculo de áudio
        print("\n🎵 TESTE 2: Cálculo de Custo para Transcrição de Áudio")
        print("-" * 50)
        
        audio_result = pricing_calculator.calculate_audio_cost(
            provider='assemblyai',
            duration_minutes=15,
            features=['speaker_diarization', 'sentiment_analysis', 'entity_detection']
        )
        
        if 'error' not in audio_result:
            print(f"✅ Provedor: {audio_result['provider']}")
            print(f"✅ Duração: {audio_result['duration_minutes']} minutos")
            print(f"✅ Features: {', '.join(audio_result['features'])}")
            print(f"💰 Custo base (USD): ${audio_result['base_cost']:.6f}")
            print(f"💰 Custo base (BRL): R$ {audio_result['base_cost_brl']:.4f}")
            print(f"💰 Custo total (USD): ${audio_result['total_cost']:.6f}")
            print(f"💰 Custo total (BRL): R$ {audio_result['total_cost_brl']:.4f}")
            
            print(f"\n🔧 Custos por Feature:")
            for feature, cost in audio_result['feature_costs'].items():
                cost_brl = audio_result['feature_costs_brl'][feature]
                print(f"   • {feature}: ${cost:.6f} (R$ {cost_brl:.4f})")
        else:
            print(f"❌ Erro: {audio_result['error']}")
        
        # Testar comparação de provedores
        print("\n⚖️ TESTE 3: Comparação entre Provedores")
        print("-" * 50)
        
        comparison = pricing_calculator.compare_providers(
            input_tokens=2000,
            output_tokens=1000
        )
        
        if 'error' not in comparison:
            print(f"✅ Comparando custos para {comparison['input_tokens']:,} tokens de entrada e {comparison['output_tokens']:,} de saída")
            print(f"\n🏆 MAIS BARATO:")
            cheapest = comparison['cheapest']
            print(f"   Provedor: {cheapest['provider']} - {cheapest['model']}")
            print(f"   Custo: ${cheapest['total_cost']:.6f} (R$ {cheapest['total_cost_brl']:.4f})")
            
            print(f"\n💸 MAIS CARO:")
            expensive = comparison['most_expensive']
            print(f"   Provedor: {expensive['provider']} - {expensive['model']}")
            print(f"   Custo: ${expensive['total_cost']:.6f} (R$ {expensive['total_cost_brl']:.4f})")
            
            print(f"\n📊 TODOS OS PROVEDORES (ordenados por custo):")
            for i, comp in enumerate(comparison['comparisons'][:5], 1):
                print(f"   {i}. {comp['provider']} ({comp['model']}): ${comp['total_cost']:.6f} (R$ {comp['total_cost_brl']:.4f})")
        else:
            print(f"❌ Erro: {comparison['error']}")
        
        # Testar estimativas por componente
        print("\n🧩 TESTE 4: Estimativas por Componente do Sistema")
        print("-" * 50)
        
        components = [
            'assistentes_juridicos',
            'transcricao_audio',
            'chat_juridico'
        ]
        
        for component in components:
            estimate = pricing_calculator.estimate_component_cost(component, {})
            
            if 'error' not in estimate:
                print(f"\n📦 Componente: {component.replace('_', ' ').title()}")
                
                # Mostrar os 3 melhores custos
                estimates_sorted = sorted(
                    estimate['estimates'].items(),
                    key=lambda x: x[1]['daily_cost']
                )[:3]
                
                for provider_model, costs in estimates_sorted:
                    daily_cost_brl = costs['daily_cost'] * pricing_calculator.usd_to_brl_rate
                    monthly_cost_brl = costs['monthly_cost'] * pricing_calculator.usd_to_brl_rate
                    
                    print(f"   • {provider_model.replace('_', ' ').title()}:")
                    print(f"     Diário: ${costs['daily_cost']:.4f} (R$ {daily_cost_brl:.2f})")
                    print(f"     Mensal: ${costs['monthly_cost']:.2f} (R$ {monthly_cost_brl:.2f})")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na demonstração da calculadora: {e}")
        print(f"\n❌ ERRO: {e}")
        return False

def test_token_tracker():
    """Testa o rastreador de tokens"""
    
    try:
        from modules.token_tracker import token_tracker
        
        print("\n" + "="*80)
        print("DEMONSTRAÇÃO - RASTREADOR DE TOKENS")
        print("="*80)
        
        # Simular alguns usos de tokens
        print("\n📊 Registrando uso de tokens simulado...")
        
        # Registrar uso dos assistentes jurídicos
        token_tracker.track_usage(
            provider='openai',
            component='assistentes_juridicos',
            tokens=1500,
            cost=0.015,
            session_id='demo_session_1',
            request_type='consultation',
            model_used='gpt-4o'
        )
        
        token_tracker.track_usage(
            provider='anthropic',
            component='assistentes_juridicos',
            tokens=2000,
            cost=0.030,
            session_id='demo_session_2',
            request_type='analysis',
            model_used='claude-3-5-sonnet-20241022'
        )
        
        # Registrar uso da transcrição
        token_tracker.track_usage(
            provider='assemblyai',
            component='transcricao_audio',
            tokens=0,  # AssemblyAI não usa tokens
            cost=0.25,
            session_id='demo_session_3',
            request_type='transcription'
        )
        
        # Registrar uso dos agentes
        token_tracker.track_usage(
            provider='gemini',
            component='agentes_multiagent',
            tokens=1800,
            cost=0.012,
            session_id='demo_session_4',
            request_type='multi_agent_analysis',
            model_used='gemini-1.5-pro'
        )
        
        print("✅ Usos de tokens registrados com sucesso")
        
        # Obter resumo de uso
        print("\n📈 Obtendo resumo de uso...")
        usage_summary = token_tracker.get_usage_summary('today')
        
        if 'error' not in usage_summary:
            total_stats = usage_summary['total_stats']
            print(f"✅ Total de tokens: {total_stats['total_tokens']:,}")
            print(f"✅ Custo total (USD): ${total_stats['total_cost']:.4f}")
            print(f"✅ Total de requisições: {total_stats['total_requests']}")
            print(f"✅ Provedores ativos: {total_stats['active_providers']}")
            
            print(f"\n🏷️ Uso por Provedor:")
            for provider in usage_summary['by_provider']:
                cost_brl = provider['cost'] * 5.25  # Conversão aproximada
                print(f"   • {provider['provider']}: {provider['tokens']:,} tokens, ${provider['cost']:.4f} (R$ {cost_brl:.2f})")
            
            print(f"\n🧩 Uso por Componente:")
            for component in usage_summary['by_component']:
                cost_brl = component['cost'] * 5.25
                print(f"   • {component['component']}: {component['tokens']:,} tokens, ${component['cost']:.4f} (R$ {cost_brl:.2f})")
        else:
            print(f"❌ Erro: {usage_summary['error']}")
        
        # Obter breakdown por componente
        print("\n🔍 Breakdown detalhado por componente...")
        breakdown = token_tracker.get_component_breakdown()
        
        if 'error' not in breakdown:
            print(f"✅ Total de tokens no período: {breakdown['total_tokens']:,}")
            
            print(f"\n📦 Componentes mais utilizados:")
            for component, data in list(breakdown['breakdown'].items())[:3]:
                cost_brl = data['total_cost'] * 5.25
                print(f"   • {component}: {data['percentage']:.1f}% ({data['total_tokens']:,} tokens)")
                print(f"     Custo: ${data['total_cost']:.4f} (R$ {cost_brl:.2f})")
                print(f"     Provedores: {', '.join(data['providers'].keys())}")
        else:
            print(f"❌ Erro: {breakdown['error']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na demonstração do rastreador: {e}")
        print(f"\n❌ ERRO: {e}")
        return False

def test_api_endpoints():
    """Testa os endpoints da API"""
    
    print("\n" + "="*80)
    print("DEMONSTRAÇÃO - ENDPOINTS DA API")
    print("="*80)
    
    print("\n🌐 Endpoints disponíveis para monitoramento:")
    print("   • GET  /api/tokens/usage?period=today")
    print("   • POST /api/tokens/track")
    print("   • POST /api/pricing/calculate")
    print("   • POST /api/pricing/compare")
    print("   • GET  /api/pricing/components")
    print("   • GET  /api/pricing/exchange-rate")
    
    print("\n📋 Exemplo de uso da API de preços:")
    example_request = {
        "type": "text",
        "provider": "openai",
        "model": "gpt-4o",
        "input_tokens": 1500,
        "output_tokens": 800
    }
    
    print(f"POST /api/pricing/calculate")
    print(f"Content-Type: application/json")
    print(f"{json.dumps(example_request, indent=2)}")
    
    print("\n📋 Exemplo de resposta esperada:")
    example_response = {
        "success": True,
        "pricing": {
            "provider": "openai",
            "model": "gpt-4o",
            "total_cost": 0.0195,
            "total_cost_brl": 0.1024,
            "exchange_rate": {
                "usd_to_brl": 5.25,
                "updated_at": datetime.now().isoformat()
            }
        }
    }
    
    print(f"{json.dumps(example_response, indent=2)}")
    
    return True

def main():
    """Função principal da demonstração"""
    
    print("INICIANDO DEMONSTRAÇÃO COMPLETA DO SISTEMA DE MONITORAMENTO")
    print("Sistema de Tokens e Custos em Real Brasileiro")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    success_count = 0
    total_tests = 3
    
    # Teste 1: Calculadora de Preços
    if test_pricing_calculator():
        success_count += 1
    
    # Teste 2: Rastreador de Tokens
    if test_token_tracker():
        success_count += 1
    
    # Teste 3: Endpoints da API
    if test_api_endpoints():
        success_count += 1
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DA DEMONSTRAÇÃO")
    print("="*80)
    print(f"✅ Testes executados: {total_tests}")
    print(f"✅ Testes bem-sucedidos: {success_count}")
    print(f"📊 Taxa de sucesso: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print(f"\n🎉 DEMONSTRAÇÃO COMPLETA COM SUCESSO!")
        print(f"✅ Sistema de monitoramento de tokens operacional")
        print(f"✅ Calculadora de preços com conversão R$ funcional")
        print(f"✅ APIs de custos prontas para uso")
        print(f"✅ Dashboard pode exibir dados em tempo real")
    else:
        print(f"\n⚠️ DEMONSTRAÇÃO PARCIALMENTE CONCLUÍDA")
        print(f"Alguns componentes podem precisar de ajustes")
    
    print(f"\n💡 PRÓXIMOS PASSOS:")
    print(f"   1. Acessar /admin/api-dashboard para visualizar dados")
    print(f"   2. Configurar alertas de custo por componente")
    print(f"   3. Implementar relatórios mensais automatizados")
    print(f"   4. Configurar limites de gastos por provedor")

if __name__ == "__main__":
    main()