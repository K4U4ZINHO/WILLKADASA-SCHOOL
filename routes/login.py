from flask import Blueprint, render_template,session
from willkadasa_db import login
@login.route("/")
def login():
    return render_template("login.html")