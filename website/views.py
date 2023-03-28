from flask import Blueprint, render_template

from . import db
from .models import Chain

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/chains")
def chains():
    chains = Chain.query
    return render_template("chains.html", chains=chains)
