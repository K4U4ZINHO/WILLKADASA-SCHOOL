from flask import Flask
import os
from extensions import socketio
# import  willkadasa_db
from routes.home import home_bp
from routes.login import login_bp          # CORRETO
from routes.cadastro import cadastro_bp
from routes.aluno import aluno_bp          # IMPORTAR AQUI
from routes.professor import professor_bp
from routes.config_conta_professor import config_conta_professor_bp
from routes.criar_teste import criar_teste_bp
from routes.criar_turma import criar_turma_bp
from routes.ver_turma import ver_turma_bp    
from routes.turma_professor import turma_professor_bp
from routes.notas_gerais import notas_gerais_bp
from routes.config_conta_aluno import config_conta_aluno_bp
from routes.ver_turma_aluno import ver_turma_aluno_bp
from routes.testes_pendentes_aluno import testes_pendentes_aluno_bp

def create_app():

    app = Flask(__name__)
    # app.secret_key = app.secret_key = os.urandom(24)
    app.secret_key = "WILLKADASA_SUPER_SECRET_KEY_123"
    #inicializar base de dados 
    
    # willkadasa_db.init_app(app) 

    # registra blueprints
        
    app.register_blueprint(home_bp)
    app.register_blueprint(cadastro_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(aluno_bp)
    app.register_blueprint(professor_bp)
    app.register_blueprint(config_conta_professor_bp)
    app.register_blueprint(criar_teste_bp)
    app.register_blueprint(criar_turma_bp)
    app.register_blueprint(ver_turma_bp)
    app.register_blueprint(turma_professor_bp)
    app.register_blueprint(notas_gerais_bp)
    app.register_blueprint(config_conta_aluno_bp)
    app.register_blueprint(ver_turma_aluno_bp)
    app.register_blueprint(testes_pendentes_aluno_bp)


    # inicializa socketio
    socketio.init_app(app)

    return app

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)


    # para matar o processo da base de dados
    # taskkill /IM python.exe /F