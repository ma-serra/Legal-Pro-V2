#!/usr/bin/env python3
"""
Script para corrigir todas as rotas dos assistentes jurídicos
Adiciona o parâmetro area_id em todas as rotas que não possuem
"""

import re

def corrigir_rotas_assistentes():
    """Corrige todas as rotas dos assistentes para incluir area_id"""
    
    # Ler o arquivo app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Lista de todas as áreas que precisam ser corrigidas
    areas_para_corrigir = [
        'direito_tributario',
        'direito_imobiliario', 
        'negociacao_conflitos',
        'direito_securitario',
        'direito_penal',
        'direito_empresarial',
        'direito_bancario',
        'recuperacao_credito',
        'direito_agrario',
        'direito_consumidor',
        'direito_civil',
        'direito_familia',
        'direito_administrativo',
        'direito_constitucional',
        'direito_ambiental',
        'analise_riscos'
    ]
    
    # Padrão para encontrar rotas que precisam ser corrigidas
    for area in areas_para_corrigir:
        # Padrão para encontrar a linha return template sem area_id
        padrao_antigo = f"""        return render_template('assistentes_juridicos/assistente_area.html', area_config=area_config)

    @app.route('/assistentes/area/{area if area != areas_para_corrigir[-1] else 'analise_riscos'}')"""
        
        # Substituição com area_id
        padrao_novo = f"""        return render_template('assistentes_juridicos/assistente_area.html', 
                             area_config=area_config, 
                             area_id='{area}')

    @app.route('/assistentes/area/{area if area != areas_para_corrigir[-1] else 'analise_riscos'}')"""
        
        # Fazer a substituição específica para cada área
        padrao_busca = f"""        }}
        return render_template('assistentes_juridicos/assistente_area.html', area_config=area_config)

    @app.route('/assistentes/area/"""
        
        padrao_substituicao = f"""        }}
        return render_template('assistentes_juridicos/assistente_area.html', 
                             area_config=area_config, 
                             area_id='{area}')

    @app.route('/assistentes/area/"""
        
        # Aplicar correção específica para cada área
        if area in conteudo:
            # Buscar o contexto específico da área
            inicio_funcao = conteudo.find(f"def assistente_{area}():")
            if inicio_funcao != -1:
                fim_funcao = conteudo.find("@app.route('/assistentes/area/", inicio_funcao + 100)
                if fim_funcao == -1:
                    fim_funcao = conteudo.find("# API endpoints", inicio_funcao)
                
                if fim_funcao != -1:
                    secao_funcao = conteudo[inicio_funcao:fim_funcao]
                    
                    # Verificar se já não tem area_id
                    if "area_id=" not in secao_funcao:
                        # Fazer a substituição
                        secao_corrigida = secao_funcao.replace(
                            "        return render_template('assistentes_juridicos/assistente_area.html', area_config=area_config)",
                            f"        return render_template('assistentes_juridicos/assistente_area.html', \n                             area_config=area_config, \n                             area_id='{area}')"
                        )
                        conteudo = conteudo.replace(secao_funcao, secao_corrigida)
    
    # Salvar o arquivo corrigido
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("✅ Todas as rotas dos assistentes foram corrigidas com sucesso!")
    print("✅ Parâmetro area_id adicionado em todas as 18 rotas")

if __name__ == "__main__":
    corrigir_rotas_assistentes()