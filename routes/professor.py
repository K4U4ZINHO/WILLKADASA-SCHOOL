from flask import Blueprint, render_template, session, redirect, url_for
# Importamos a função de consulta híbrida
from willkadasa_db import db_query

professor_bp = Blueprint("professor", __name__, url_prefix="/professor")

@professor_bp.route("/dashboard")
def dashboard_professor():
    email_logado = session.get("email")
    if not email_logado:
        return redirect(url_for("login.login_professor"))

    # 1. Busca os dados do professor para personalizar as saudações
    professor = db_query("""
        SELECT p.id, p.nome 
        FROM professores p
        JOIN email e ON p.email_id = e.id
        WHERE LOWER(e.email_principal) = LOWER(?)
    """, (email_logado,), one=True)

    # 2. Busca as turmas (se o seu sistema permitir que o professor veja todas ou apenas as dele)
    # Aqui estou buscando todas as turmas cadastradas para o dashboard
    turmas = db_query("SELECT id, nome, ano, curso FROM turmas ORDER BY nome ASC")

    return render_template("home_professor.html", 
        professor=professor, 
        turmas=turmas)

@professor_bp.route("/notas_individuais")
def notas_individuais():
    # Esta rota geralmente é acessada via turma_professor, 
    # mas mantemos o template se houver uma visão geral.
    return render_template("notas_individuais.html")

@professor_bp.route("/recuperar_senha")
def recuperar_senha():
    return render_template("recuperar_senha.html")

@professor_bp.route("/trocar_senha")
def trocar_senha():
    return render_template("trocar_senha.html")