#!/usr/bin/env python3
"""
Script para configurar permissões padrão do módulo jurídico
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, PermissaoAreaJuridica, CategoriaJuridica, AgenteJuridico

def setup_permissoes_juridicas():
    """
    Configura permissões padrão para o módulo jurídico
    """
    with app.app_context():
        try:
            print("🔧 Configurando permissões do módulo jurídico...")
            
            # Busca todos os usuários ativos
            usuarios = User.query.filter_by(active=True).all()
            print(f"📋 Encontrados {len(usuarios)} usuários ativos")
            
            # Criar categorias padrão se não existirem
            categorias_padrao = [
                {
                    'nome': 'Direito Penal',
                    'descricao': 'Especialistas em direito criminal e processual penal',
                    'icone': 'fas fa-gavel',
                    'cor': '#dc3545'
                },
                {
                    'nome': 'Direito Civil',
                    'descricao': 'Especialistas em direito civil e processual civil',
                    'icone': 'fas fa-balance-scale',
                    'cor': '#007bff'
                },
                {
                    'nome': 'Direito Empresarial',
                    'descricao': 'Especialistas em direito empresarial e societário',
                    'icone': 'fas fa-building',
                    'cor': '#1f5981'
                },
                {
                    'nome': 'Direito Trabalhista',
                    'descricao': 'Especialistas em direito do trabalho',
                    'icone': 'fas fa-users',
                    'cor': '#ffc107'
                },
                {
                    'nome': 'Direito Bancário',
                    'descricao': 'Especialistas em direito bancário e financeiro',
                    'icone': 'fas fa-university',
                    'cor': '#17a2b8'
                },
                {
                    'nome': 'Recuperação de Crédito',
                    'descricao': 'Especialistas em cobrança e execução',
                    'icone': 'fas fa-coins',
                    'cor': '#fd7e14'
                }
            ]
            
            for cat_data in categorias_padrao:
                categoria = CategoriaJuridica.query.filter_by(nome=cat_data['nome']).first()
                if not categoria:
                    categoria = CategoriaJuridica(
                        nome=cat_data['nome'],
                        descricao=cat_data['descricao'],
                        icone=cat_data['icone'],
                        cor=cat_data['cor'],
                        ativa=True
                    )
                    db.session.add(categoria)
                    print(f"✅ Categoria criada: {cat_data['nome']}")
            
            db.session.commit()
            print("📋 Categorias jurídicas configuradas")
            
            # Configurar permissões para todos os usuários
            for usuario in usuarios:
                # Verificar se já tem permissão para "Todas as Áreas"
                permissao_existente = PermissaoAreaJuridica.query.filter_by(
                    user_id=usuario.id,
                    area_juridica='Todas as Áreas'
                ).first()
                
                if not permissao_existente:
                    # Criar permissão para todas as áreas
                    nova_permissao = PermissaoAreaJuridica(
                        user_id=usuario.id,
                        area_juridica='Todas as Áreas',
                        pode_visualizar=True
                    )
                    db.session.add(nova_permissao)
                    print(f"✅ Permissão criada para {usuario.username}: Todas as Áreas")
                else:
                    print(f"ℹ️  {usuario.username} já possui acesso a todas as áreas")
            
            # Criar agentes padrão se não existirem
            agentes_padrao = [
                {
                    'nome': 'Especialista em Defesa Criminal',
                    'classe': 'AssistenteDireitoPenal',
                    'descricao': 'Especialista em defesa criminal e elaboração de peças processuais penais',
                    'categoria': 'Direito Penal',
                    'detalhes_tecnicos': '{"capacidades": ["Elaboração de defesas", "Análise processual", "Recursos criminais"], "limitacoes": ["Não substitui advogado"], "icone": "user-tie"}'
                },
                {
                    'nome': 'Consultor Empresarial',
                    'classe': 'AssistenteDireitoEmpresarial',
                    'descricao': 'Especialista em direito empresarial e societário',
                    'categoria': 'Direito Empresarial',
                    'detalhes_tecnicos': '{"capacidades": ["Contratos societários", "Compliance", "Due diligence"], "limitacoes": ["Consulta apenas"], "icone": "building"}'
                },
                {
                    'nome': 'Especialista em Cobrança',
                    'classe': 'AssistenteRecuperacaoCredito',
                    'descricao': 'Especialista em recuperação de crédito e execução',
                    'categoria': 'Recuperação de Crédito',
                    'detalhes_tecnicos': '{"capacidades": ["Ações de cobrança", "Execução de títulos", "Negociação"], "limitacoes": ["Orientação processual"], "icone": "coins"}'
                }
            ]
            
            for agente_data in agentes_padrao:
                categoria = CategoriaJuridica.query.filter_by(nome=agente_data['categoria']).first()
                if categoria:
                    agente_existente = AgenteJuridico.query.filter_by(nome=agente_data['nome']).first()
                    if not agente_existente:
                        novo_agente = AgenteJuridico(
                            nome=agente_data['nome'],
                            classe=agente_data['classe'],
                            descricao=agente_data['descricao'],
                            categoria_id=categoria.id,
                            detalhes_tecnicos=agente_data['detalhes_tecnicos'],
                            ativo=True,
                            nivel_especializacao=4
                        )
                        db.session.add(novo_agente)
                        print(f"✅ Agente criado: {agente_data['nome']}")
            
            db.session.commit()
            print("🎯 Configuração concluída com sucesso!")
            
            # Exibir estatísticas
            total_permissoes = PermissaoAreaJuridica.query.count()
            total_categorias = CategoriaJuridica.query.filter_by(ativa=True).count()
            total_agentes = AgenteJuridico.query.filter_by(ativo=True).count()
            
            print(f"""
📊 Estatísticas do Sistema Jurídico:
   - Permissões configuradas: {total_permissoes}
   - Categorias ativas: {total_categorias}
   - Agentes disponíveis: {total_agentes}
   - Usuários com acesso: {len(usuarios)}
            """)
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro na configuração: {e}")
            raise

if __name__ == "__main__":
    setup_permissoes_juridicas()