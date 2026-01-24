import sqlite3
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

login_bp = Blueprint("login", __name__)

def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def buscar_usuario(email):
    conn = sqlite3.connect("willkadasa.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email_principal, senha_hash
        FROM email
        WHERE email_principal = ?
    """, (email,))

    usuario = cursor.fetchone()
    conn.close()
    return usuario


@login_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = buscar_usuario(email)

        
        if not usuario or criar_hash_senha(senha) != usuario[3]:
            flash("Email ou senha incorretos.", "danger")
            return redirect(url_for("login.login"))

        
        id_user, nome, email_principal, senha_hash = usuario

        
        session["usuario_id"] = id_user
        session["usuario_nome"] = nome

        return redirect(url_for("dashboard.index"))

    return render_template("login.html")