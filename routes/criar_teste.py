from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime
# Importamos apenas o db_query, já que esta rota é apenas GET
from willkadasa_db import db_query

criar_teste_bp = Blueprint("criar_teste", __name__, url_prefix="/professor")

@criar_teste_bp.route("/criar_teste", methods=["GET"])
def criar_teste():
    email = session.get("email")
    if not email:
        # Certifique-se de que o nome da rota de login do professor é este mesmo
        return redirect(url_for("login.login_professor"))

    # Busca os dados do professor usando a função híbrida
    resultado = db_query("""
        SELECT e.nome, p.disciplinas
        FROM professores p
        JOIN email e ON p.email_id = e.id
        WHERE LOWER(e.email_principal) = LOWER(?)
    """, (email,), one=True)

    if not resultado:
        nome_professor = "Professor"
        disciplinas = ""
    else:
        nome_professor = resultado["nome"]
        disciplinas = resultado["disciplinas"]

    # Tratamento das disciplinas
    lista_disciplinas = []
    if disciplinas:
        lista_disciplinas = [d.strip() for d in disciplinas.split(",")]

    # Lógica do Trimestre (mantida igual)
    mes = datetime.now().month
    if mes <= 3:
        trimestre = "1º Trimestre"
    elif mes <= 6:
        trimestre = "2º Trimestre"
    elif mes <= 9:
        trimestre = "3º Trimestre"
    else:
        trimestre = "4º Trimestre"

    titulo_sugerido = f"Avaliação {trimestre}"

    return render_template(
        "criar_teste.html",
        nome_professor=nome_professor,
        disciplinas=lista_disciplinas,
        titulo_sugerido=titulo_sugerido
    )