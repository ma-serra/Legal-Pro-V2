from main import app, db
import models

with app.app_context():
    # Cria as tabelas no banco de dados
    db.create_all()
    print("Tabelas criadas com sucesso!")