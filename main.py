import flask as flask
import os
from extensions import socketio
import willkadasa_db
    
def create_app():
    app = flask(__name__)

    #inicializar base de dados 
    willkadasa_db.init_app(app)

    # registra blueprints
    app.register_blueprint(login_route)
    # inicializa socketio
    socketio.init_app(app)

    return app

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    

@app.route("/")
def index():
    return flask.render_template("login.html")

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))