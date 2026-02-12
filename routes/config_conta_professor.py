from flask import Blueprint, render_template, request, session, redirect, url_for, flash
# Importamos as funções do seu banco de dados híbrido
from willkadasa_db import db_query, db_execute

config_conta_professor_bp = Blueprint(
    "config_conta_professor",
    __name__,
    url_prefix="/professor/config"
)

@config_conta_professor_bp.route("/conta", methods=["GET", "POST"])
def config_conta():
    email = session.get("email")

    if not email:
        return "Professor não autenticado", 401

    if request.method == "POST":
        data_nasc = request.form.get("data_nascimento")
        telefone = request.form.get("telefone")
        email_sec = request.form.get("email_secundario")
        disciplinas = request.form.get("disciplinas")

        # Usamos db_execute para o UPDATE
        db_execute("""
            UPDATE professores
            SET data_nascimento = ?, telefone = ?, email_secundario = ?, disciplinas = ?
            WHERE email_id = (SELECT id FROM email WHERE LOWER(email_principal) = LOWER(?))
        """, (data_nasc, telefone, email_sec, disciplinas, email))

        flash("Alterações salvas com sucesso!", "success")
        return redirect(url_for("config_conta_professor.config_conta"))

    # Lógica para o GET
    dados = db_query("""
        SELECT p.nome, e.email_principal, e.senha_hash,
               p.data_nascimento, p.telefone,
               p.email_secundario, p.disciplinas
        FROM professores p
        JOIN email e ON p.email_id = e.id
        WHERE LOWER(e.email_principal) = LOWER(?)
    """, (email,), one=True)

    if not dados:
        flash("Dados do professor não encontrados.", "danger")
        return redirect(url_for("home_professor")) # Ou sua rota de dashboard

    return render_template(
        "config_conta_professor.html",
        nome_professor=dados["nome"],
        email_professor=dados["email_principal"],
        senha_professor=dados["senha_hash"],
        data_nascimento=dados["data_nascimento"],
        telefone=dados["telefone"],
        email_secundario=dados["email_secundario"],
        disciplinas=dados["disciplinas"]
    )