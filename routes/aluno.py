from flask import Blueprint, render_template, session

aluno_bp = Blueprint("aluno", __name__, url_prefix="/aluno")

@aluno_bp.route("/dashboard")
def dashboard_aluno():
    return render_template("home_aluno.html")

@aluno_bp.route("/config_conta_aluno")
def config_conta_aluno():
    return render_template("config_conta_aluno.html")


@aluno_bp.route("/ver_turma_aluno")
def ver_turma_aluno():
    return render_template("ver_turma_aluno.html")


@aluno_bp.route("/ver_notas_aluno")
def ver_notas_aluno():
    return render_template("ver_notas_aluno.html")


@aluno_bp.route("/testes_pendentes_aluno")
def testes_pendentes_aluno():
    return render_template("testes_pendentes_aluno.html")


@aluno_bp.route("/realizar_teste")
def realizar_teste():
    return render_template("realizar_teste.html")



