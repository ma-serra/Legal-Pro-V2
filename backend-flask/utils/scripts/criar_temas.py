"""
Script para criar automaticamente temas para todas as páginas principais do sistema.
"""
import os
import sys
import json
from datetime import datetime

# Evitando importação circular
sys.path.insert(0, '.')

# Estamos conectando diretamente ao banco de dados em vez de usar imports para evitar importação circular
import psycopg2
from psycopg2.extras import RealDictCursor

# Obter a conexão do banco de dados do ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')

# Lista das principais rotas e suas descrições
PAGINAS = [
    ('/', 'Página Inicial'),
    ('/analisar', 'Página de Análise'),
    ('/historico', 'Histórico de Análises'),
    ('/extrair-texto', 'Extração de Texto'),
    ('/modulos-avancados', 'Módulos Avançados'),
    ('/juridico/segunda-opiniao', 'Segunda Opinião Jurídica'),
    ('/juridico/especialistas', 'Especialistas Jurídicos'),
    ('/perfil', 'Perfil do Usuário'),
    ('/admin/usuarios', 'Administração - Usuários'),
    ('/admin/roles', 'Administração - Papéis'),
    ('/admin/permissoes', 'Administração - Permissões'),
    ('/admin/apis', 'Administração - APIs'),
    ('/admin/logs', 'Administração - Logs'),
    ('/admin/config', 'Administração - Configurações'),
    ('/admin/monitor', 'Administração - Monitoramento'),
    ('/admin/fluxos', 'Administração - Fluxos'),
    ('/admin/temas', 'Administração - Temas'),
    ('/admin/agentes', 'Administração - Agentes'),
    ('/admin/taskade', 'Administração - Taskade'),
    ('/transcription/', 'Transcrição - Página Inicial'),
    ('/transcription/result', 'Transcrição - Resultados'),
    ('/transcription/progress', 'Transcrição - Progresso'),
    ('/listar-agentes', 'Listar Agentes'),
    ('/criar-agente', 'Criar Agente'),
    ('/listar-templates', 'Listar Templates'),
    ('/criar-template', 'Criar Template'),
    ('/listar-fluxos', 'Listar Fluxos'),
    ('/criar-fluxo', 'Criar Fluxo'),
    ('/editor-fluxos', 'Editor de Fluxos'),
]

def criar_tema(conn, rota, descricao):
    """
    Cria um tema para uma rota específica.
    
    Args:
        conn: Conexão com o banco de dados
        rota: Rota da página
        descricao: Descrição amigável da página
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Verificar se o tema já existe
    cursor.execute("SELECT id FROM tema_pagina WHERE rota = %s", (rota,))
    tema_existente = cursor.fetchone()
    
    if tema_existente:
        print(f"Tema para {rota} já existe. ID: {tema_existente['id']}")
        return
    
    # Definir cores padrão para algumas páginas específicas
    cores_default = {}
    
    # Página inicial - texto branco
    if rota == '/':
        cores_default = {
            "body": {
                "color": "#FFFFFF"
            }
        }
    
    # Página de análise - texto preto com fundo cinza escuro
    elif rota == '/analisar':
        cores_default = {
            "body": {
                "color": "#000000",
                "background-color": "#333333"
            }
        }
    
    # Segunda opinião - texto branco
    elif rota == '/juridico/segunda-opiniao':
        cores_default = {
            "body": {
                "color": "#FFFFFF"
            },
            "pre": {
                "color": "#FFFFFF",
                "background-color": "#2c2c2c"
            }
        }
        
    # Páginas de transcrição - fundo cinza claro com texto preto
    elif rota.startswith('/transcription'):
        cores_default = {
            "body": {
                "color": "#000000",
                "background-color": "#f8f9fa"
            },
            ".container": {
                "background-color": "#f8f9fa"
            },
            ".card": {
                "background-color": "#FFFFFF",
                "color": "#000000",
                "border-color": "#dee2e6"
            },
            ".card-header": {
                "background-color": "#e9ecef",
                "color": "#000000"
            },
            ".transcript-segment": {
                "background-color": "#FFFFFF",
                "color": "#000000",
                "border-color": "#dee2e6"
            },
            ".btn-copy": {
                "background-color": "#212529",
                "color": "#FFFFFF"
            },
            ".btn-copy:hover": {
                "background-color": "#000000",
                "color": "#FFFFFF"
            }
        }
    
    # Adicionar cores padrão para elementos pré-formatados em todas as páginas
    if 'pre' not in cores_default:
        cores_default['pre'] = {
            "color": "#FFFFFF",
            "background-color": "#2c2c2c"
        }
    
    # Cores padrão para botões primários
    if '.btn-primary' not in cores_default:
        cores_default['.btn-primary'] = {
            "background-color": "#0d6efd",
            "color": "#FFFFFF"
        }
    
    # Cores padrão para botões secundários
    if '.btn-secondary' not in cores_default:
        cores_default['.btn-secondary'] = {
            "background-color": "#6c757d",
            "color": "#FFFFFF"
        }
    
    # Cores padrão para cartões
    if '.card' not in cores_default:
        cores_default['.card'] = {
            "background-color": "#343a40",
            "color": "#FFFFFF"
        }
    
    # Cores padrão para cabeçalhos de cartões
    if '.card-header' not in cores_default:
        cores_default['.card-header'] = {
            "background-color": "#212529",
            "color": "#FFFFFF"
        }
    
    # Salvar o tema
    try:
        cursor.execute(
            "INSERT INTO tema_pagina (rota, descricao, cores, ativo, modificado_em) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (rota, descricao, json.dumps(cores_default), True, datetime.now())
        )
        
        tema_id = cursor.fetchone()['id']
        conn.commit()
        print(f"Tema para {rota} criado com sucesso. ID: {tema_id}")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar tema para {rota}: {str(e)}")

def main():
    """
    Função principal para criar temas para todas as páginas.
    """
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        
        print("Criando temas para as páginas principais...")
        
        for rota, descricao in PAGINAS:
            criar_tema(conn, rota, descricao)
        
        print("Finalizado!")
        
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()