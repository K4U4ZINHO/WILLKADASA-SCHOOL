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
    with sqlite3.connect("willkadasa.db") as conn:
        cursor = conn.cursor()
        # A ordem aqui define os índices usuario[0], usuario[1], etc.
        cursor.execute("""
            SELECT id, nome, email_principal, senha_hash, tipo 
            FROM email 
            WHERE email_principal = ?
        """, (email,))
        return cursor.fetchone()


# -----------------------------
# LOGIN DO PROFESSOR
# -----------------------------
@login_bp.route("/professor", methods=["GET", "POST"])
def login_professor():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        session["email"] = email
        senha = request.form.get("senha")

        with sqlite3.connect("willkadasa.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT senha_hash FROM email WHERE email_principal = ? AND tipo = 'professor'", (email,))
            dados = cursor.fetchone()

        if not dados:
            flash("Email não encontrado.", "danger")
            return render_template("login_professor.html")

        senha_hash = dados[0]

        if criar_hash_senha(senha) != senha_hash:
            flash("Senha incorreta.", "danger")
            return render_template("login_professor.html")

        
        session["email"] = email

        return redirect(url_for("professor.dashboard_professor"))

    return render_template("login_professor.html")

# -----------------------------
# LOGIN DO ALUNO
# -----------------------------
@login_bp.route("/aluno", methods=["GET", "POST"])
def login_aluno():
    if request.method == "POST":
        # Pegamos o SKWD (ex: 0001)
        skwd = request.form.get("skwd", "").strip()
        senha = request.form.get("senha")

        # 1. Busca o usuário na tabela 'email' onde o email_principal é o SKWD
        usuario = buscar_usuario(skwd)

        # 2. Validação
        # usuario[0]=id, usuario[1]=nome, usuario[2]=email_principal, usuario[3]=senha_hash, usuario[4]=tipo
        if usuario:
            if criar_hash_senha(senha) == usuario[3] and usuario[4] == "aluno":
                session.clear()

                # Define as variáveis de sessão
                session["usuario_id"] = usuario[0]
                session["usuario_nome"] = usuario[1]
                session["email"] = usuario[2]  # Aqui fica o SKWD (ex: 0001)
                session["tipo"] = "aluno"

                flash(f"Bem-vindo, {usuario[1]}!", "success")
                return redirect(url_for("aluno.dashboard_aluno"))
            else:
                flash("Senha incorreta para este código SKWD.", "danger")
        else:
            flash("Código SKWD não encontrado.", "danger")

        return redirect(url_for("login.login_aluno"))

    return render_template("login_aluno.html")