from flask import Blueprint, render_template, request, redirect, url_for, flash
import hashlib
# Importamos a conexão híbrida
from willkadasa_db import db_query, db_execute

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")

SENHA_SECRETA_PROFESSOR = "2026professor"

def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def gerar_proximo_usuario():
    """Gera o próximo ID (SKWD) formatado como 0001, 0002... adaptado para SQLite e Postgres."""
    # Usamos uma query que funciona em ambos os bancos para extrair números
    sql = """
        SELECT email_principal 
        FROM email 
        WHERE tipo = 'aluno' 
        ORDER BY id DESC LIMIT 1
    """
    resultado = db_query(sql, one=True)
    
    if not resultado or not str(resultado['email_principal']).isdigit():
        return "0001"
    
    proximo = int(resultado['email_principal']) + 1
    return f"{proximo:04d}"

@cadastro_bp.route("/", methods=["GET", "POST"])
def cadastro():
    proximo_usuario_exibicao = gerar_proximo_usuario()

    if request.method == "POST":
        tipo = request.form.get("tipo")
        nome = ""
        email = ""
        senha = ""

        # 1. Coleta e Validação
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
            email = gerar_proximo_usuario() 

        if not nome or not senha:
            flash("Por favor, preencha todos os campos!", "warning")
            return render_template("cadastro.html", proximo_usuario=proximo_usuario_exibicao)

        senha_hash = criar_hash_senha(senha)

        try:
            # A. Inserção na Tabela Geral (email)
            db_execute("""
                INSERT INTO email (nome, email_principal, senha_hash, tipo)
                VALUES (?, ?, ?, ?)
            """, (nome, email, senha_hash, tipo))
            
            # Buscamos o ID gerado (compatível com ambos os bancos)
            res_id = db_query("SELECT id FROM email WHERE email_principal = ?", (email,), one=True)
            email_id_gerado = res_id['id']

            # B. Inserção nas Tabelas Relacionadas
            if tipo == "professor":
                db_execute("""
                    INSERT INTO professores (nome, email_id)
                    VALUES (?, ?)
                """, (nome, email_id_gerado))
            
            elif tipo == "aluno":
                db_execute("""
                    INSERT INTO alunos (skwd_aluno, nome, email_id)
                    VALUES (?, ?, ?)
                """, (email, nome, email_id_gerado))

            msg_sucesso = f"Conta de {tipo} criada! Seu código de acesso é: {email}" if tipo == "aluno" else "Conta de professor criada!"
            flash(msg_sucesso, "success")
            return redirect(url_for(f"login.login_{tipo}"))

        except Exception as e:
            print(f"Erro no cadastro: {e}")
            flash("Erro: Este e-mail ou código já existe no sistema.", "danger")
            return render_template("cadastro.html", proximo_usuario=gerar_proximo_usuario())

    return render_template("cadastro.html", proximo_usuario=proximo_usuario_exibicao)