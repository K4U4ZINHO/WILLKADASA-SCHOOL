from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import sqlite3

criar_turma_bp = Blueprint("criar_turma", __name__, url_prefix="/professor")

@criar_turma_bp.route("/criar_turma", methods=["GET", "POST"])
def criar_turma():

    email = session.get("email")
    if not email:
        return redirect(url_for("login.professor_login"))

    if request.method == "POST":
        nome_turma = request.form.get("nome_turma")
        alunos_selecionados = request.form.getlist("alunos")

        with sqlite3.connect("willkadasa.db") as conn:
            cursor = conn.cursor()

            # Criar turma com valores neutros
            cursor.execute("""
                INSERT INTO turmas (nome, ano, curso)
                VALUES (?, ?, ?)
            """, (nome_turma, 0, ""))

            turma_id = cursor.lastrowid

            # Associar alunos
            for aluno_id in alunos_selecionados:
                cursor.execute("""
                    UPDATE alunos
                    SET turma_id = ?
                    WHERE id = ?
                """, (turma_id, aluno_id))

            conn.commit()

        flash("Turma criada com sucesso!", "success")
        return redirect(url_for("professor.dashboard_professor"))

    # GET → carregar alunos sem turma
    with sqlite3.connect("willkadasa.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM alunos WHERE turma_id IS NULL")
        alunos = cursor.fetchall()

    return render_template("criar_turma.html", alunos=alunos)