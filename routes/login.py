from flask import Blueprint, render_template
# from willkadasa_db import login
login_bp = Blueprint("login", __name__)

@login_bp.route("/")    

def login():
    return render_template("login.html")
