from flask import Blueprint, render_template
import sqlite3


professor_bp = Blueprint("professor", __name__, url_prefix="/professor")

@professor_bp.route("/dashboard")
def dashboard_professor():
    return render_template("home_professor.html")

# @professor_bp.route("/criar_teste")
# def criar_teste():
    
#     with sqlite3.connect("willkadasa.db", timeout=5) as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT MAX(id) FROM email WHERE tipo = 'professor'")
#         nome_professor = cursor.fetchone()[0]

#    return render_template("criar_teste.html", nome_professor=nome_professor)


# @professor_bp.route("/criar_turma")

# def criar_turma():
#     return render_template("criar_turma.html")

# @professor_bp.route("/config_conta")
# def config_conta():
#     return render_template("config_conta_professor.html")

# @professor_bp.route("/ver_turma")
# def ver_turma():
#     return render_template("ver_turma.html")

# @professor_bp.route("/turma_professor")
# def turma_professor():
#     return render_template("turma_professor.html")

# @professor_bp.route("/notas_gerais")
# def notas_gerais():
#     return render_template("notas_gerais.html")

@professor_bp.route("/notas_individuais")
def notas_individuais():
    return render_template("notas_individuais.html")


@professor_bp.route("/recuperar_senha")
def recuperar_senha():
    return render_template("recuperar_senha.html")


@professor_bp.route("/trocar_senha")
def trocar_senha():
    return render_template("trocar_senha.html")



