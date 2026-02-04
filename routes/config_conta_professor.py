from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import sqlite3

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

        with sqlite3.connect("willkadasa.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE professores
                SET data_nascimento = ?, telefone = ?, email_secundario = ?, disciplinas = ?
                WHERE email_id = (SELECT id FROM email WHERE email_principal = ?)
            """, (data_nasc, telefone, email_sec, disciplinas, email))
            conn.commit()

        flash("Alterações salvas com sucesso!", "success")
        return redirect(url_for("config_conta_professor.config_conta"))

    # GET
    with sqlite3.connect("willkadasa.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.nome, e.email_principal, e.senha_hash,
            p.data_nascimento, p.telefone,
            p.email_secundario, p.disciplinas
            FROM professores p
            JOIN email e ON p.email_id = e.id
            WHERE LOWER(e.email_principal) = LOWER(?)
        """, (email,))
        dados = cursor.fetchone()

    nome, email_principal, senha_hash, data_nasc, telefone, email_sec, disciplinas = dados

    return render_template(
        "config_conta_professor.html",
        nome_professor=nome,
        email_professor=email_principal,
        senha_professor=senha_hash,
        data_nascimento=data_nasc,
        telefone=telefone,
        email_secundario=email_sec,
        disciplinas=disciplinas
    )