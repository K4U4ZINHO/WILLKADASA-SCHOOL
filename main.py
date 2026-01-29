from flask import Flask
import os
from extensions import socketio
# import  willkadasa_db
from routes.home import home_bp
from routes.login import login_bp          # CORRETO
from routes.cadastro import cadastro_bp
from routes.aluno import aluno_bp          # IMPORTAR AQUI
from routes.professor import professor_bp


    
def create_app():

    app = Flask(__name__)
    app.secret_key = app.secret_key = os.urandom(24)
    #inicializar base de dados 
    
    # willkadasa_db.init_app(app) 

    # registra blueprints
    
    app.register_blueprint(home_bp)
    app.register_blueprint(cadastro_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(aluno_bp)
    app.register_blueprint(professor_bp)

    # inicializa socketio
    socketio.init_app(app)

    return app

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)


    # para matar o processo da base de dados
    # taskkill /IM python.exe /F