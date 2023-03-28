from flask import Blueprint, render_template

from . import db

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/chains/")
@views.route("/chains/<chain_id>")
def chains(chain_id=None):
    cursor = db.cursor()
    if chain_id:
        cursor.execute(
            r"""SELECT *
            FROM chains
            WHERE chain_id = %s
            """,
            (chain_id),
        )
    else:
        cursor.execute(
            r"""SELECT *
            FROM chains
            """
        )
    chains = cursor.fetchall()
    cursor.close()
    return render_template("chains.html", chains=chains)


@views.route("/hotels/")
@views.route("/hotels/<hotel_id>")
def hotels(hotel_id=None):
    cursor = db.cursor()
    if hotel_id:
        cursor.execute(
            r"""SELECT *
                FROM hotels
                WHERE hotel_id = %s
                """,
            (hotel_id),
        )
    else:
        cursor.execute(
            r"""SELECT *
                FROM hotels
                """
        )
    hotels = cursor.fetchall()
    cursor.close()
    return render_template("hotels.html", hotels=hotels)
