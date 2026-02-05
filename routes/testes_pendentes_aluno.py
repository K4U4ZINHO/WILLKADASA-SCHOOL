from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3

testes_pendentes_aluno_bp = Blueprint("testes_pendentes_aluno_sessao", __name__, url_prefix="/aluno")

def get_db_connection():
    conn = sqlite3.connect("willkadasa.db")
    conn.row_factory = sqlite3.Row
    return conn

@testes_pendentes_aluno_bp.route("/testes_pendentes")
def testes_pendentes_aluno():
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_aluno"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Pegamos o ID do aluno
    cursor.execute("""
        SELECT a.id AS aluno_id 
        FROM alunos a 
        JOIN email e ON a.email_id = e.id 
        WHERE e.email_principal = ?
    """, (email,))
    aluno = cursor.fetchone()

    exames_pendentes = []

    if aluno:
        # 2. Buscamos exames que NÃO foram submetidos por este aluno
        # Note que removi o e.turma_id para evitar o erro de coluna inexistente
        cursor.execute("""
            SELECT e.id, e.titulo, e.duracao_minutos
            FROM exames e
            WHERE NOT EXISTS (
                SELECT 1 FROM submissoes_exame s 
                WHERE s.exame_id = e.id AND s.aluno_id = ?
            )
        """, (aluno["aluno_id"],))
        exames_pendentes = cursor.fetchall()

    conn.close()
    return render_template("testes_pendentes_aluno.html", testes=exames_pendentes)