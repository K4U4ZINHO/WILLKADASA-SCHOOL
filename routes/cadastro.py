import sqlite3
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")

# SENHA SECRETA DO PROFESSOR (alterar aqui)
SENHA_SECRETA_PROFESSOR = "1234"

def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def gerar_proximo_usuario():
    with sqlite3.connect("willkadasa.db", timeout=5) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(CAST(email_principal AS INTEGER)) FROM email WHERE tipo = 'aluno'")
        ultimo = cursor.fetchone()[0]

    if ultimo is None:
        return "0001"
    return f"{int(ultimo) + 1:04d}"

@cadastro_bp.route("/", methods=["GET", "POST"])
def cadastro():
    proximo_usuario = gerar_proximo_usuario()

    if request.method == "POST":
        tipo = request.form.get("tipo")

        # -----------------------------
        # CADASTRO DO PROFESSOR
        # -----------------------------
        if tipo == "professor":
            nome = request.form.get("nome_prof")
            email = request.form.get("email_prof").strip().lower()
            senha = request.form.get("senha_prof")
            senha_secreta = request.form.get("senha_secreta_prof")

            # validação da senha secreta
            if senha_secreta != SENHA_SECRETA_PROFESSOR:
                flash("Senha secreta incorreta.", "danger")
                return render_template("cadastro.html", proximo_usuario=proximo_usuario)

        # -----------------------------
        # CADASTRO DO ALUNO
        # -----------------------------
        elif tipo == "aluno":
            nome = request.form.get("nome_aluno")
            senha = request.form.get("senha_aluno")
            email = gerar_proximo_usuario()

        else:
            flash("Selecione um tipo de conta.", "warning")
            return render_template("cadastro.html", proximo_usuario=proximo_usuario)

        # validação geral
        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "warning")
            return render_template("cadastro.html", proximo_usuario=proximo_usuario)

        senha_hash = criar_hash_senha(senha)

        try:
            with sqlite3.connect("willkadasa.db", timeout=5) as conn:
                cursor = conn.cursor()

                # Inserir na tabela email
                cursor.execute("""
                    INSERT INTO email (nome, email_principal, senha_hash, tipo)
                    VALUES (?, ?, ?, ?)
                """, (nome, email, senha_hash, tipo))

                # Inserir na tabela professores
                if tipo == "professor":
                    cursor.execute("""
                        INSERT INTO professores (nome, email_id)
                        VALUES (?, (SELECT id FROM email WHERE email_principal = ?))
                    """, (nome, email))

                conn.commit()

        except sqlite3.IntegrityError:
            flash("Erro: este usuário já existe.", "danger")
            return render_template("cadastro.html", proximo_usuario=proximo_usuario)

        flash("Conta criada com sucesso!", "success")

        if tipo == "aluno":
            return redirect(url_for("login.login_aluno"))
        if tipo == "professor":
            return redirect(url_for("login.login_professor"))

    return render_template("cadastro.html", proximo_usuario=proximo_usuario)