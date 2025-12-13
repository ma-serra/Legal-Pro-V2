"""
Script para criar a tabela de permissões de áreas jurídicas.
"""
import sys
import os
from sqlalchemy.exc import SQLAlchemyError
from main import db
from models import PermissaoAreaJuridica

def criar_tabela_permissoes_areas():
    """Cria a tabela permissao_area_juridica no banco de dados."""
    try:
        # Verifica se a tabela já existe
        db.session.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'permissao_area_juridica'")
        print("A tabela permissao_area_juridica já existe no banco de dados.")
        return
    except:
        # Cria a tabela
        print("Criando tabela permissao_area_juridica...")
        db.create_all()
        db.session.commit()
        print("Tabela permissao_area_juridica criada com sucesso!")

if __name__ == "__main__":
    try:
        criar_tabela_permissoes_areas()
    except SQLAlchemyError as e:
        print(f"Erro ao criar tabela: {str(e)}")
        sys.exit(1)