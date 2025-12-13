#!/usr/bin/env python3
"""
Script para sincronizar componentes do fluxo atual com a biblioteca do editor
"""

import os
import sys
import json
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models import ComponenteEditor, Fluxo

def sincronizar_componentes_fluxo(fluxo_id):
    """Sincroniza componentes de um fluxo específico para a biblioteca"""
    
    with app.app_context():
        try:
            # Buscar o fluxo
            fluxo = Fluxo.query.get(fluxo_id)
            if not fluxo:
                print(f"❌ Fluxo {fluxo_id} não encontrado")
                return False
            
            print(f"🔄 Sincronizando componentes do fluxo: {fluxo.nome}")
            
            # Parse dos agentes do fluxo
            agentes = fluxo.agentes if isinstance(fluxo.agentes, list) else json.loads(fluxo.agentes or '[]')
            
            componentes_criados = []
            
            for agente in agentes:
                nome_componente = agente.get('config', {}).get('titulo', f"Componente {agente.get('id', 'sem_id')}")
                
                # Verificar se já existe
                existe = ComponenteEditor.query.filter_by(nome=nome_componente).first()
                if existe:
                    print(f"⚠️  Componente '{nome_componente}' já existe - pulando")
                    continue
                
                # Mapear tipo para categoria
                tipo = agente.get('tipo', 'processamento')
                categoria_map = {
                    'entrada': 'Extração',
                    'extrator': 'Extração', 
                    'classificador': 'Classificação',
                    'analisador': 'Análise',
                    'especialista': 'Especialização',
                    'transformador': 'Transformação',
                    'gerador': 'Geração',
                    'agregador': 'Agregação',
                    'conector': 'Conexão',
                    'saida': 'Geração'
                }
                
                categoria = categoria_map.get(tipo, 'Processamento')
                
                # Mapear cor por tipo
                cor_map = {
                    'entrada': '#47b6b5',
                    'extrator': '#20597f',
                    'classificador': '#fec208', 
                    'analisador': '#17a2b7',
                    'especialista': '#c4414f',
                    'transformador': '#e98132',
                    'gerador': '#36bf9c',
                    'agregador': '#1175e5',
                    'conector': '#6d47b3',
                    'saida': '#47b6b5'
                }
                
                cor = cor_map.get(tipo, '#47b6b5')
                
                # Criar componente
                novo_componente = ComponenteEditor(
                    nome=nome_componente,
                    categoria=categoria,
                    tipo=tipo,
                    descricao=agente.get('config', {}).get('descricao', f'Componente {tipo} do fluxo'),
                    descricao_detalhada=f"Componente originado do fluxo '{fluxo.nome}' - {agente.get('config', {}).get('descricao', 'Sem descrição adicional')}",
                    icone=f'fas fa-{tipo}' if tipo in ['entrada', 'saida'] else f'fas fa-cog',
                    cor=cor,
                    ativo=True,
                    configuracao={
                        'origem': 'fluxo',
                        'fluxo_id': fluxo_id,
                        'agente_id': agente.get('id'),
                        'sincronizado_em': datetime.now().isoformat()
                    },
                    prompt_sistema=f'Você é um componente {tipo} especializado importado do fluxo {fluxo.nome}',
                    prompt_usuario=f'Execute a função de {tipo} conforme configurado no fluxo',
                    capacidades=[tipo, 'fluxo_integrado', categoria.lower()],
                    parametros=agente.get('config', {}),
                    base_conhecimento='direito_brasileiro',
                    temperatura=0.3,
                    max_tokens=4000,
                    top_k=4,
                    chunk_size=1000,
                    chunk_overlap=200
                )
                
                db.session.add(novo_componente)
                componentes_criados.append(nome_componente)
                print(f"✅ Criado: {nome_componente} ({categoria}/{tipo})")
            
            # Commit das mudanças
            if componentes_criados:
                db.session.commit()
                print(f"🎉 Sincronização concluída! {len(componentes_criados)} componentes criados:")
                for comp in componentes_criados:
                    print(f"   - {comp}")
            else:
                print("ℹ️  Nenhum componente novo foi criado")
                
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro na sincronização: {str(e)}")
            return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fluxo_id = int(sys.argv[1])
        sincronizar_componentes_fluxo(fluxo_id)
    else:
        print("Uso: python sync_fluxo_components.py <fluxo_id>")
        print("Exemplo: python sync_fluxo_components.py 2")