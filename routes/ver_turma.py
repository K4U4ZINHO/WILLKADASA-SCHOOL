from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3

ver_turma_bp = Blueprint("ver_turma", __name__, url_prefix="/aluno")

@ver_turma_bp.route("/ver_turma")
def ver_turma():

    with sqlite3.connect("willkadasa.db") as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome FROM turmas")
        turmas = cursor.fetchall()

        lista = []
        for turma_id, nome in turmas:
            cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id = ?", (turma_id,))
            total = cursor.fetchone()[0]

            lista.append({
                "id": turma_id,
                "nome": nome,
                "total": total
            })

    return render_template("ver_turma.html", turmas=lista)