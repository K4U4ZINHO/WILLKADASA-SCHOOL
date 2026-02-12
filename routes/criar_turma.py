from flask import Blueprint, render_template, request, session, redirect, url_for, flash
# Importamos as funções do seu banco de dados híbrido
from willkadasa_db import db_query, db_execute

criar_turma_bp = Blueprint("criar_turma", __name__, url_prefix="/professor")

@criar_turma_bp.route("/criar_turma", methods=["GET", "POST"])
def criar_turma():
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_professor"))

    if request.method == "POST":
        nome_turma = request.form.get("nome_turma")
        alunos_selecionados = request.form.getlist("alunos")

        # 1. Criar turma com valores neutros
        db_execute("""
            INSERT INTO turmas (nome, ano, curso)
            VALUES (?, ?, ?)
        """, (nome_turma, 0, ""))

        # 2. Pegar o ID da turma criada (Compatível com SQLite e Postgres)
        res_turma = db_query("SELECT id FROM turmas WHERE nome = ? ORDER BY id DESC", (nome_turma,), one=True)
        turma_id = res_turma['id'] if res_turma else None

        if turma_id:
            # 3. Associar alunos selecionados
            for aluno_id in alunos_selecionados:
                db_execute("""
                    UPDATE alunos
                    SET turma_id = ?
                    WHERE id = ?
                """, (turma_id, aluno_id))

            flash(f"Turma '{nome_turma}' criada com sucesso!", "success")
        
        return redirect(url_for("professor.dashboard_professor"))

    # GET → Carregar apenas alunos que ainda não possuem turma
    alunos = db_query("SELECT id, nome FROM alunos WHERE turma_id IS NULL")

    return render_template("criar_turma.html", alunos=alunos)