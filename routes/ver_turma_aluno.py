from flask import Blueprint, render_template, session, redirect, url_for, flash
import sqlite3

ver_turma_aluno_bp = Blueprint("ver_turma_aluno_sessao", __name__, url_prefix="/aluno")

def get_db_connection():
    conn = sqlite3.connect("willkadasa.db")
    conn.row_factory = sqlite3.Row
    return conn

@ver_turma_aluno_bp.route("/ver_turma_aluno")
def ver_turma_aluno():
    email = session.get("email")

    if not email:
        return redirect(url_for("login.login_aluno"))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Buscamos a turma do aluno seguindo o padrão do config_conta
        cursor.execute("""
            SELECT a.turma_id, t.nome AS nome_turma
            FROM alunos a
            JOIN email e ON a.email_id = e.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE e.email_principal = ?
        """, (email,))
        
        dados_vinculo = cursor.fetchone()

        alunos_da_turma = []
        turma_info = None

        # Se encontrou o aluno e ele tem uma turma vinculada
        if dados_vinculo and dados_vinculo["turma_id"]:
            turma_info = {"nome": dados_vinculo["nome_turma"]}
            
            # 2. Buscamos todos os colegas que possuem o mesmo turma_id
            cursor.execute("""
                SELECT nome FROM alunos 
                WHERE turma_id = ? 
                ORDER BY nome ASC
            """, (dados_vinculo["turma_id"],))
            
            alunos_da_turma = cursor.fetchall()

    # Se o aluno nem sequer existir no banco, redireciona
    if not dados_vinculo:
        flash("Perfil de aluno não encontrado.", "danger")
        return redirect(url_for("aluno.dashboard_aluno"))

    return render_template(
        "ver_turma_aluno.html", 
        turma=turma_info, 
        alunos=alunos_da_turma
    )