from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import hashlib
# Importamos as funções do seu banco de dados híbrido
from willkadasa_db import db_query

login_bp = Blueprint("login", __name__, url_prefix="/login")

# -----------------------------
# Funções auxiliares
# -----------------------------
def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def buscar_usuario(identificador):
    """Busca o usuário pelo email_principal (que pode ser o e-mail ou o SKWD)."""
    return db_query("""
        SELECT id, nome, email_principal, senha_hash, tipo 
        FROM email 
        WHERE LOWER(email_principal) = LOWER(?)
    """, (identificador,), one=True)

# -----------------------------
# LOGIN DO PROFESSOR
# -----------------------------
@login_bp.route("/professor", methods=["GET", "POST"])
def login_professor():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        senha = request.form.get("senha")

        # Usamos a função auxiliar que já utiliza o db_query
        usuario = buscar_usuario(email)

        if not usuario or usuario["tipo"] != "professor":
            flash("Email não encontrado ou conta não é de professor.", "danger")
            return render_template("login_professor.html")

        if criar_hash_senha(senha) != usuario["senha_hash"]:
            flash("Senha incorreta.", "danger")
            return render_template("login_professor.html")

        # Define as variáveis de sessão
        session.clear()
        session["usuario_id"] = usuario["id"]
        session["usuario_nome"] = usuario["nome"]
        session["email"] = usuario["email_principal"]
        session["tipo"] = "professor"

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

        # 1. Busca o usuário
        usuario = buscar_usuario(skwd)

        # 2. Validação utilizando os nomes das colunas (mais seguro)
        if usuario:
            if criar_hash_senha(senha) == usuario["senha_hash"] and usuario["tipo"] == "aluno":
                session.clear()

                # Define as variáveis de sessão
                session["usuario_id"] = usuario["id"]
                session["usuario_nome"] = usuario["nome"]
                session["email"] = usuario["email_principal"] # SKWD
                session["tipo"] = "aluno"

                flash(f"Bem-vindo, {usuario['nome']}!", "success")
                return redirect(url_for("aluno.dashboard_aluno"))
            else:
                flash("Senha incorreta para este código SKWD.", "danger")
        else:
            flash("Código SKWD não encontrado.", "danger")

        return redirect(url_for("login.login_aluno"))

    return render_template("login_aluno.html")