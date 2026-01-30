from flask import Blueprint, render_template   

criar_teste_bp = Blueprint("criar_teste", __name__, url_prefix="/criar_teste")

@criar_teste_bp.route("/criar_teste")
def criar_teste():
    return render_template("criar_teste.html")