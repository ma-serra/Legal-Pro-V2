"""
Script para atualizar as cores dos ícones de Direito de Família
Mantém os ícones FontAwesome existentes, apenas muda a cor para #ba9851 com fundo branco
"""

import os
import psycopg2
from urllib.parse import urlparse

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL não encontrada")
        
        url = urlparse(database_url)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar com o banco: {e}")
        return None

def atualizar_cores_familia():
    """Atualiza as classes CSS dos ícones para usar cores customizadas"""
    
    conn = conectar_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Buscar todos os agentes de Direito de Família
        cursor.execute("SELECT id, nome, icone FROM agente_juridico WHERE categoria_id = 15")
        agentes = cursor.fetchall()
        
        contador = 0
        for agente_id, nome, icone_atual in agentes:
            # Adicionar classe CSS personalizada para Direito de Família
            icone_atualizado = f"{icone_atual} familia-icon"
            
            cursor.execute(
                "UPDATE agente_juridico SET icone = %s WHERE id = %s",
                (icone_atualizado, agente_id)
            )
            
            contador += 1
            print(f"✅ Ícone atualizado para: {nome}")
            print(f"   Antes: {icone_atual}")
            print(f"   Depois: {icone_atualizado}")
        
        conn.commit()
        print(f"\n✅ Total de ícones atualizados: {contador}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar ícones: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def criar_css_personalizado():
    """Cria CSS personalizado para os ícones de Direito de Família"""
    
    css_content = """
/* Estilos personalizados para ícones de Direito de Família */
.familia-icon {
    color: #ba9851 !important;
    background-color: white !important;
    padding: 8px !important;
    border-radius: 50% !important;
    border: 2px solid #ba9851 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 40px !important;
    height: 40px !important;
    box-shadow: 0 2px 4px rgba(186, 152, 81, 0.2) !important;
}

.familia-icon:hover {
    background-color: #ba9851 !important;
    color: white !important;
    transform: scale(1.05) !important;
    transition: all 0.3s ease !important;
}

/* Estilos específicos para cards de agentes da família */
.agent-card .familia-icon {
    margin-bottom: 10px !important;
    font-size: 18px !important;
}

/* Estilos para listagem de especialistas */
.specialist-list .familia-icon {
    margin-right: 15px !important;
    font-size: 16px !important;
}
"""
    
    # Salvar o CSS personalizado
    css_filepath = os.path.join("static", "css", "familia-icons.css")
    os.makedirs(os.path.dirname(css_filepath), exist_ok=True)
    
    with open(css_filepath, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"✅ CSS personalizado criado em: {css_filepath}")
    return css_filepath

def main():
    """Função principal"""
    print("🎨 Atualizando cores dos ícones de Direito de Família...")
    print("Cor: #ba9851 | Fundo: Branco")
    
    # Criar CSS personalizado
    css_path = criar_css_personalizado()
    
    # Atualizar ícones no banco
    if atualizar_cores_familia():
        print("\n✅ Ícones atualizados com sucesso!")
        print(f"📄 CSS personalizado salvo em: {css_path}")
        print("\n📝 Próximos passos:")
        print("1. Incluir o CSS no template base da aplicação")
        print("2. Verificar se as classes estão sendo aplicadas corretamente")
    else:
        print("\n❌ Erro ao atualizar os ícones.")

if __name__ == "__main__":
    main()