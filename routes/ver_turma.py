from flask import Blueprint, render_template, session, redirect, url_for, flash
import sqlite3

ver_turma_bp = Blueprint("ver_turma", __name__, url_prefix="/professor")

# --- ROTA 1: EXIBIR A LISTA DE TURMAS (O GET) ---
@ver_turma_bp.route("/ver_turma")
def ver_turma():
    email = session.get("email")
    if not email:
        return redirect(url_for("login.professor_login"))

    with sqlite3.connect("willkadasa.db") as conn:
        conn.row_factory = sqlite3.Row  # ESSENCIAL para usar turma.id no HTML
        cursor = conn.cursor()
        
        # Seleciona turmas e conta alunos (COUNT)
        cursor.execute("""
            SELECT t.id, t.nome, COUNT(a.id) as total
            FROM turmas t
            LEFT JOIN alunos a ON t.id = a.turma_id
            GROUP BY t.id
        """)
        turmas = cursor.fetchall()

    return render_template("ver_turma.html", turmas=turmas)

# --- ROTA 2: EXCLUIR A TURMA (O POST) ---
@ver_turma_bp.route("/excluir_turma/<int:id_turma>", methods=["POST"])
def excluir_turma(id_turma):
    try:
        with sqlite3.connect("willkadasa.db") as conn:
            cursor = conn.cursor()

            # 1. Libera os alunos (define turma_id como NULL)
            cursor.execute("UPDATE alunos SET turma_id = NULL WHERE turma_id = ?", (id_turma,))

            # 2. Deleta a turma
            cursor.execute("DELETE FROM turmas WHERE id = ?", (id_turma,))
            
            conn.commit()
            
    except Exception as e:
        print(f"Erro ao excluir: {e}")
        

    # Agora o redirecionamento vai funcionar porque a rota acima existe!
    return redirect(url_for("ver_turma.ver_turma"))

# --- ROTA 3: DETALHES (Para o botão "Entrar" não dar erro) ---
@ver_turma_bp.route("/detalhes_turma/<int:id_turma>")
def detalhes_turma(id_turma):
    # Aqui você criaria a lógica para ver os alunos daquela turma específica
        return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))