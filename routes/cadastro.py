import sqlite3
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")

SENHA_SECRETA_PROFESSOR = "2026professor"

def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def gerar_proximo_usuario():
    """Gera o próximo ID (SKWD) formatado como 0001, 0002... usando SQL puro."""
    with sqlite3.connect("willkadasa.db", timeout=5) as conn:
        cursor = conn.cursor()
        # Busca o maior valor numérico de email_principal onde o tipo é aluno
        cursor.execute("""
            SELECT MAX(CAST(email_principal AS INTEGER)) 
            FROM email 
            WHERE tipo = 'aluno' AND email_principal GLOB '[0-9]*'
        """)
        resultado = cursor.fetchone()[0]
        
    if resultado is None:
        return "0001"
    
    proximo = int(resultado) + 1
    return f"{proximo:04d}"

@cadastro_bp.route("/", methods=["GET", "POST"])
def cadastro():
    # Carrega o ID inicial para exibir no formulário (GET)
    proximo_usuario_exibicao = gerar_proximo_usuario()

    if request.method == "POST":
        tipo = request.form.get("tipo")
        nome = ""
        email = ""
        senha = ""

        # 1. Coleta e Validação Específica
        if tipo == "professor":
            nome = request.form.get("nome_prof", "").strip()
            email = request.form.get("email_prof", "").strip().lower()
            senha = request.form.get("senha_prof")
            senha_secreta = request.form.get("senha_secreta_prof")

            if senha_secreta != SENHA_SECRETA_PROFESSOR:
                flash("Senha secreta do professor incorreta!", "danger")
                return render_template("cadastro.html", proximo_usuario=proximo_usuario_exibicao)

        elif tipo == "aluno":
            nome = request.form.get("nome_aluno", "").strip()
            senha = request.form.get("senha_aluno")
            # Geramos o email (SKWD) no momento exato da inserção para evitar duplicatas
            email = gerar_proximo_usuario() 

        # 2. Validação Geral
        if not nome or not senha:
            flash("Por favor, preencha todos os campos!", "warning")
            return render_template("cadastro.html", proximo_usuario=proximo_usuario_exibicao)

        senha_hash = criar_hash_senha(senha)

        try:
            with sqlite3.connect("willkadasa.db", timeout=5) as conn:
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()

                # A. Inserção na Tabela Geral (email)
                cursor.execute("""
                    INSERT INTO email (nome, email_principal, senha_hash, tipo)
                    VALUES (?, ?, ?, ?)
                """, (nome, email, senha_hash, tipo))
                
                email_id_gerado = cursor.lastrowid

                # B. Inserção nas Tabelas Relacionadas
                if tipo == "professor":
                    cursor.execute("""
                        INSERT INTO professores (nome, email_id)
                        VALUES (?, ?)
                    """, (nome, email_id_gerado))
                
                elif tipo == "aluno":
                    cursor.execute("""
                        INSERT INTO alunos (skwd_aluno, nome, email_id)
                        VALUES (?, ?, ?)
                    """, (email, nome, email_id_gerado))

                conn.commit()
                
                msg_sucesso = f"Conta de {tipo} criada! Seu código de acesso é: {email}" if tipo == "aluno" else "Conta de professor criada!"
                flash(msg_sucesso, "success")

        except sqlite3.IntegrityError:
            flash("Erro: Este e-mail ou código já existe no sistema.", "danger")
            return render_template("cadastro.html", proximo_usuario=gerar_proximo_usuario())

        # 3. Redirecionamento
        return redirect(url_for(f"login.login_{tipo}"))

    return render_template("cadastro.html", proximo_usuario=proximo_usuario_exibicao)