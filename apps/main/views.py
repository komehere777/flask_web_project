from flask import Blueprint, render_template, redirect, url_for

main = Blueprint("main", __name__, template_folder="templates", static_folder="static")

@main.route("/")
def index():
    return render_template("main/index.html")
