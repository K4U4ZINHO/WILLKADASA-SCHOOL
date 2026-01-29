import sqlite3
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

login_bp = Blueprint("login", __name__, url_prefix="/login")


# -----------------------------
# Funções auxiliares
# -----------------------------
def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def buscar_usuario(email):
    conn = sqlite3.connect("willkadasa.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email_principal, senha_hash, tipo
        FROM email
        WHERE email_principal = ?
    """, (email,))

    usuario = cursor.fetchone()
    conn.close()
    return usuario


# -----------------------------
# LOGIN DO PROFESSOR
# -----------------------------
@login_bp.route("/professor", methods=["GET", "POST"])
def login_professor():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = buscar_usuario(email)

        if not usuario or criar_hash_senha(senha) != usuario[3] or usuario[4] != "professor":
            flash("Email ou senha incorretos.", "danger")
            return redirect(url_for("login.login_professor"))

        session["usuario_id"] = usuario[0]
        session["usuario_nome"] = usuario[1]

        return redirect(url_for("professor.dashboard_professor"))

    return render_template("login_professor.html")


# -----------------------------
# LOGIN DO ALUNO
# -----------------------------
@login_bp.route("/aluno", methods=["GET", "POST"])
def login_aluno():
    if request.method == "POST":
        skwd = request.form.get("skwd")
        senha = request.form.get("senha")

        usuario = buscar_usuario(skwd)

        if not usuario or criar_hash_senha(senha) != usuario[3] or usuario[4] != "aluno":
            flash("SKWD ou senha incorretos.", "danger")
            return redirect(url_for("login.login_aluno"))

        session["usuario_id"] = usuario[0]
        session["usuario_nome"] = usuario[1]

        return redirect(url_for("aluno.dashboard_aluno"))

    return render_template("login_aluno.html")
