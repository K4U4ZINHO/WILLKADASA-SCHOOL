from flask import Blueprint, render_template

professor_bp = Blueprint("professor", __name__, url_prefix="/professor")

@professor_bp.route("/dashboard")
def dashboard_professor():
    return render_template("home_professor.html")

@professor_bp.route("/criar_teste")
def criar_teste():
    return render_template("criar_teste.html")

