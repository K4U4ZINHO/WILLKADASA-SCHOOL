from flask import Blueprint, render_template, session, redirect, url_for, flash
# Importamos a função de consulta híbrida
from willkadasa_db import db_query

ver_turma_aluno_bp = Blueprint("ver_turma_aluno_sessao", __name__, url_prefix="/aluno")

@ver_turma_aluno_bp.route("/ver_turma_aluno")
def ver_turma_aluno():
    email = session.get("email")

    if not email:
        return redirect(url_for("login.login_aluno"))

    # 1. Buscamos a turma do aluno usando db_query
    # O pattern LOWER ajuda a evitar erros de caixa alta/baixa no login
    dados_vinculo = db_query("""
        SELECT a.turma_id, t.nome AS nome_turma
        FROM alunos a
        JOIN email e ON a.email_id = e.id
        LEFT JOIN turmas t ON a.turma_id = t.id
        WHERE LOWER(e.email_principal) = LOWER(?)
    """, (email,), one=True)

    # Se o aluno nem sequer existir no banco
    if not dados_vinculo:
        flash("Perfil de aluno não encontrado.", "danger")
        return redirect(url_for("aluno.dashboard_aluno"))

    alunos_da_turma = []
    turma_info = None

    # Se encontrou o aluno e ele tem uma turma vinculada
    if dados_vinculo["turma_id"]:
        turma_info = {"nome": dados_vinculo["nome_turma"]}
        
        # 2. Buscamos todos os colegas da mesma turma
        alunos_da_turma = db_query("""
            SELECT nome FROM alunos 
            WHERE turma_id = ? 
            ORDER BY nome ASC
        """, (dados_vinculo["turma_id"],))

    return render_template(
        "ver_turma_aluno.html", 
        turma=turma_info, 
        alunos=alunos_da_turma
    )