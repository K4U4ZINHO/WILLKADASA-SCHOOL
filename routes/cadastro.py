import sqlite3
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash

cadastro_bp = Blueprint("cadastro", __name__)

def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

@cadastro_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        tipo = request.form.get("tipo")

        # 1. Validação básica
        if not nome or not email or not senha or not tipo:
            flash("Preencha todos os campos.", "warning")
            return render_template("cadastro.html")

        # 2. Verificar se o email já existe
        conn = sqlite3.connect("willkadasa.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM email WHERE email_principal = ?", (email,))
        existente = cursor.fetchone()

        if existente:
            conn.close()
            flash("Este email já está cadastrado.", "danger")
            return render_template("cadastro.html")

        # 3. Criar hash da senha
        senha_hash = criar_hash_senha(senha)

        # 4. Inserir no banco
        cursor.execute("""
            INSERT INTO email (nome, email_principal, email_recuperacao, senha_hash)
            VALUES (?, ?, ?, ?)
        """, (nome, email, email, senha_hash))

        conn.commit()
        conn.close()

        flash("Conta criada com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("login.login"))

    return render_template("cadastro.html")


@cadastro_bp.route("/recuperar")
def recuperar():
    return render_template("recuperar_senha.html")