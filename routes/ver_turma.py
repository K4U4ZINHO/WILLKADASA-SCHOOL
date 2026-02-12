from flask import Blueprint, render_template, session, redirect, url_for, flash
# Importamos as funções do seu banco de dados híbrido
from willkadasa_db import db_query, db_execute

ver_turma_bp = Blueprint("ver_turma", __name__, url_prefix="/professor")

# --- ROTA 1: EXIBIR A LISTA DE TURMAS ---
@ver_turma_bp.route("/ver_turma")
def ver_turma():
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_professor"))

    # Seleciona turmas e conta alunos (COUNT)
    # Ajustado o GROUP BY para total compatibilidade com PostgreSQL
    turmas = db_query("""
        SELECT t.id, t.nome, COUNT(a.id) as total
        FROM turmas t
        LEFT JOIN alunos a ON t.id = a.turma_id
        GROUP BY t.id, t.nome
        ORDER BY t.nome ASC
    """)

    return render_template("ver_turma.html", turmas=turmas)

# --- ROTA 2: EXCLUIR A TURMA ---
@ver_turma_bp.route("/excluir_turma/<int:id_turma>", methods=["POST"])
def excluir_turma(id_turma):
    try:
        # 1. Libera os alunos (define turma_id como NULL para não deletar os alunos junto)
        db_execute("UPDATE alunos SET turma_id = NULL WHERE turma_id = ?", (id_turma,))

        # 2. Deleta a turma
        db_execute("DELETE FROM turmas WHERE id = ?", (id_turma,))
        
        flash("Turma excluída com sucesso!", "success")
            
    except Exception as e:
        print(f"Erro ao excluir: {e}")
        flash("Erro ao tentar excluir a turma.", "danger")

    return redirect(url_for("ver_turma.ver_turma"))

# --- ROTA 3: DETALHES ---
@ver_turma_bp.route("/detalhes_turma/<int:id_turma>")
def detalhes_turma(id_turma):
    # Redireciona para o controlador que gerencia a sala de aula específica
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))