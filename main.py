from flask import Flask
import os
from extensions import socketio
# import  willkadasa_db
from routes.login import login_bp
from routes.cadastro import cadastro_bp
    
def create_app():

    app = Flask(__name__)
    app.secret_key = app.secret_key = os.urandom(24)
    

    #inicializar base de dados 
    # willkadasa_db.init_app(app)

    # registra blueprints
    app.register_blueprint(login_bp)
    app.register_blueprint(cadastro_bp)

    # inicializa socketio
    socketio.init_app(app)

    return app

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=500, debug=True)