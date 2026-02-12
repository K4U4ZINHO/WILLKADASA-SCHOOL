from flask import Blueprint, render_template, session, redirect, url_for
# Importamos a função de consulta híbrida
from willkadasa_db import db_query

testes_pendentes_aluno_bp = Blueprint("testes_pendentes_aluno_sessao", __name__, url_prefix="/aluno")

@testes_pendentes_aluno_bp.route("/testes_pendentes")
def testes_pendentes_aluno():
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_aluno"))

    # 1. Pegamos o ID do aluno E o ID da turma atual dele
    aluno = db_query("""
        SELECT a.id AS aluno_id, a.turma_id 
        FROM alunos a 
        JOIN email e ON a.email_id = e.id 
        WHERE LOWER(e.email_principal) = LOWER(?)
    """, (email,), one=True)

    exames_pendentes = []

    if aluno and aluno["turma_id"]:
        # 2. Buscamos exames que pertencem à turma do aluno e ainda NÃO foram feitos
        # Usamos NOT EXISTS para filtrar apenas o que falta realizar
        exames_pendentes = db_query("""
            SELECT e.id, e.titulo, e.duracao_minutos
            FROM exames e
            WHERE e.turma_id = ? 
            AND NOT EXISTS (
                SELECT 1 FROM submissoes_exame s 
                WHERE s.exame_id = e.id AND s.aluno_id = ?
            )
        """, (aluno["turma_id"], aluno["aluno_id"]))

    return render_template("testes_pendentes_aluno.html", testes=exames_pendentes)