from flask import Blueprint, render_template
# from willkadasa_db import login
cadastro_bp = Blueprint("cadastro", __name__)

@cadastro_bp.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@cadastro_bp.route("/recupar")
def recuperar():
    return render_template("recuperar_senha.html")