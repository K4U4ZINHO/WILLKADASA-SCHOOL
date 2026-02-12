# No arquivo routes/config_conta_aluno.py

from flask import Blueprint, render_template, session, redirect, url_for, flash
# Importamos as funções do seu banco de dados híbrido
from willkadasa_db import db_query

config_conta_aluno_bp = Blueprint("config_conta_aluno", __name__, url_prefix="/aluno")

@config_conta_aluno_bp.route("/config_conta_aluno")
def config_conta_aluno():
    email = session.get("email") # O email do aluno (SKWD)

    if not email:
        return redirect(url_for("login.login_aluno"))

    # Usamos db_query com one=True para pegar os dados do aluno
    # A função já trata a troca de ? para %s no Postgres automaticamente
    dados_aluno = db_query("""
        SELECT a.nome, a.skwd_aluno, t.nome AS nome_turma
        FROM alunos a
        JOIN email e ON a.email_id = e.id
        LEFT JOIN turmas t ON a.turma_id = t.id
        WHERE e.email_principal = ?
    """, (email,), one=True)

    if not dados_aluno:
        flash("Dados não encontrados.", "danger")
        return redirect(url_for("aluno.dashboard_aluno"))

    return render_template(
        "config_conta_aluno.html",
        nome=dados_aluno["nome"],
        skwd=dados_aluno["skwd_aluno"],
        turma=dados_aluno["nome_turma"] if dados_aluno["nome_turma"] else "Sem Turma"
    )