from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3

testes_pendentes_aluno_bp = Blueprint("testes_pendentes_aluno_sessao", __name__, url_prefix="/aluno")

def get_db_connection():
    conn = sqlite3.connect("willkadasa.db")
    conn.row_factory = sqlite3.Row
    # Tenta adicionar a coluna. Se já existir, o erro é ignorado silenciosamente.
    try:
        conn.execute("ALTER TABLE exames ADD COLUMN turma_id INTEGER REFERENCES turmas(id);")
        conn.commit()
        print("Coluna turma_id verificada/adicionada.")
    except sqlite3.OperationalError:
        pass
    return conn

@testes_pendentes_aluno_bp.route("/testes_pendentes")
def testes_pendentes_aluno():
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_aluno"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Pegamos o ID do aluno E o ID da turma atual dele
    cursor.execute("""
        SELECT a.id AS aluno_id, a.turma_id 
        FROM alunos a 
        JOIN email e ON a.email_id = e.id 
        WHERE e.email_principal = ?
    """, (email,))
    aluno = cursor.fetchone()

    exames_pendentes = []

    if aluno and aluno["turma_id"]:
        # 2. Buscamos exames que pertencem à turma do aluno e não foram feitos
        cursor.execute("""
            SELECT e.id, e.titulo, e.duracao_minutos
            FROM exames e
            WHERE e.turma_id = ? 
            AND NOT EXISTS (
                SELECT 1 FROM submissoes_exame s 
                WHERE s.exame_id = e.id AND s.aluno_id = ?
            )
        """, (aluno["turma_id"], aluno["aluno_id"]))
        exames_pendentes = cursor.fetchall()

    conn.close()
    return render_template("testes_pendentes_aluno.html", testes=exames_pendentes)