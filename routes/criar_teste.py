from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3
from datetime import datetime

criar_teste_bp = Blueprint("criar_teste", __name__, url_prefix="/professor")

@criar_teste_bp.route("/criar_teste", methods=["GET"])
def criar_teste():

    email = session.get("email")
    if not email:
        return redirect(url_for("login.professor_login"))

    with sqlite3.connect("willkadasa.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.nome, p.disciplinas
            FROM professores p
            JOIN email e ON p.email_id = e.id
            WHERE e.email_principal = ?
        """, (email,))

        resultado = cursor.fetchone()

    if not resultado:
        nome_professor = "Professor"
        disciplinas = ""
    else:
        nome_professor, disciplinas = resultado

    lista_disciplinas = []
    if disciplinas:
        lista_disciplinas = [d.strip() for d in disciplinas.split(",")]

    mes = datetime.now().month
    if mes <= 3:
        trimestre = "1º Trimestre"
    elif mes <= 6:
        trimestre = "2º Trimestre"
    elif mes <= 9:
        trimestre = "3º Trimestre"
    else:
        trimestre = "4º Trimestre"

    # ... (código anterior igual)
    titulo_sugerido = f"Avaliação {trimestre}"

    return render_template(
        "criar_teste.html",
        nome_professor=nome_professor,
        disciplinas=lista_disciplinas,
        titulo_sugerido=titulo_sugerido
    )