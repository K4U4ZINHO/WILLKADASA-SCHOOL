from flask import Blueprint, render_template, session
# Importamos o db_query caso você queira exibir algo do banco na home futuramente
from willkadasa_db import db_query

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    # Exemplo: se você quiser mostrar o nome do usuário logado na home
    email = session.get("email")
    usuario = None
    
    if email:
        usuario = db_query("SELECT nome FROM email WHERE LOWER(email_principal) = LOWER(?)", (email,), one=True)

    return render_template("home.html", usuario=usuario)