from flask import Blueprint, render_template, session

aluno_bp = Blueprint("aluno", __name__, url_prefix="/aluno")

@aluno_bp.route("/dashboard")
def dashboard_aluno():
    return render_template("home_aluno.html")