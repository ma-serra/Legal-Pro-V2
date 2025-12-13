"""
API para sincronizar componentes de fluxos para a biblioteca
"""

from flask import request, jsonify
from flask_login import login_required
import json
from datetime import datetime

def register_sync_fluxo_api(app, db):
    """Registra a API de sincronização de fluxos para biblioteca"""
    
    # Importar aqui para evitar importação circular
    from models import ComponenteEditor, Fluxo
    
    @app.route('/api/fluxos/sync-to-library/<int:fluxo_id>', methods=['POST'])
    @login_required 
    def sync_fluxo_to_library(fluxo_id):
        """Sincroniza componentes de um fluxo para a biblioteca de componentes"""
        try:
            # Buscar o fluxo
            fluxo = Fluxo.query.get_or_404(fluxo_id)
            
            # Parse dos agentes do fluxo
            agentes = fluxo.agentes if isinstance(fluxo.agentes, list) else json.loads(fluxo.agentes or '[]')
            
            componentes_criados = []
            componentes_existentes = []
            
            for agente in agentes:
                nome_componente = agente.get('config', {}).get('titulo', f"Componente {agente.get('id', 'sem_id')}")
                
                # Verificar se já existe
                existe = ComponenteEditor.query.filter_by(nome=nome_componente).first()
                if existe:
                    componentes_existentes.append(nome_componente)
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
                
                # Mapear ícone por tipo
                icone_map = {
                    'entrada': 'fas fa-sign-in-alt',
                    'extrator': 'fas fa-file-text',
                    'classificador': 'fas fa-tags',
                    'analisador': 'fas fa-search',
                    'especialista': 'fas fa-user-tie',
                    'transformador': 'fas fa-exchange-alt',
                    'gerador': 'fas fa-file-plus',
                    'agregador': 'fas fa-layer-group',
                    'conector': 'fas fa-plug',
                    'saida': 'fas fa-file-export'
                }
                
                icone = icone_map.get(tipo, 'fas fa-cog')
                
                # Criar componente
                novo_componente = ComponenteEditor(
                    nome=nome_componente,
                    categoria=categoria,
                    tipo=tipo,
                    descricao=agente.get('config', {}).get('descricao', f'Componente {tipo} do fluxo'),
                    descricao_detalhada=f"Componente originado do fluxo '{fluxo.nome}' - {agente.get('config', {}).get('descricao', 'Processamento especializado')}",
                    icone=icone,
                    cor=cor,
                    ativo=True,
                    configuracao={
                        'origem': 'fluxo',
                        'fluxo_id': fluxo_id,
                        'agente_id': agente.get('id'),
                        'sincronizado_em': datetime.now().isoformat(),
                        'posicao_original': agente.get('posicao', {})
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
                componentes_criados.append({
                    'nome': nome_componente,
                    'categoria': categoria,
                    'tipo': tipo,
                    'cor': cor
                })
            
            # Commit das mudanças
            if componentes_criados:
                db.session.commit()
                
            return jsonify({
                'success': True,
                'message': f'Sincronização concluída! {len(componentes_criados)} componentes criados.',
                'fluxo': {
                    'id': fluxo.id,
                    'nome': fluxo.nome,
                    'descricao': fluxo.descricao
                },
                'componentes_criados': componentes_criados,
                'componentes_existentes': componentes_existentes,
                'total_agentes_fluxo': len(agentes)
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro na sincronização fluxo->biblioteca: {str(e)}")
            return jsonify({
                'success': False, 
                'error': str(e),
                'message': 'Erro ao sincronizar componentes do fluxo'
            }), 500
    
    @app.route('/api/fluxos/sync-status/<int:fluxo_id>')
    @login_required
    def check_sync_status(fluxo_id):
        """Verifica status de sincronização de um fluxo"""
        try:
            fluxo = Fluxo.query.get_or_404(fluxo_id)
            agentes = fluxo.agentes if isinstance(fluxo.agentes, list) else json.loads(fluxo.agentes or '[]')
            
            status_componentes = []
            for agente in agentes:
                nome_componente = agente.get('config', {}).get('titulo', f"Componente {agente.get('id', 'sem_id')}")
                existe = ComponenteEditor.query.filter_by(nome=nome_componente).first()
                
                status_componentes.append({
                    'nome': nome_componente,
                    'tipo': agente.get('tipo'),
                    'sincronizado': bool(existe),
                    'id_biblioteca': existe.id if existe else None
                })
            
            total_sincronizados = sum(1 for comp in status_componentes if comp['sincronizado'])
            
            return jsonify({
                'success': True,
                'fluxo': {
                    'id': fluxo.id,
                    'nome': fluxo.nome
                },
                'total_componentes': len(status_componentes),
                'total_sincronizados': total_sincronizados,
                'componentes': status_componentes,
                'percentual_sincronizado': round((total_sincronizados / len(status_componentes)) * 100) if status_componentes else 0
            })
            
        except Exception as e:
            app.logger.error(f"Erro ao verificar status de sincronização: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500