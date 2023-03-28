from flask import Blueprint, render_template

from . import db

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/chains/")
@views.route("/chains/<int:chain_id>")
def chains(chain_id=None):
    query = r"""SELECT *
                FROM chains
            """
    cursor = db.cursor()
    if chain_id:
        cursor.execute(
            query + "WHERE chain_id = %s",
            (chain_id,),
        )
    else:
        cursor.execute(query)
    chains = cursor.fetchall()
    cursor.close()
    return render_template("chains.html", chains=chains)


@views.route("/hotels/")
@views.route("/hotels/<int:hotel_id>")
def hotels(hotel_id=None):
    query = r"""SELECT *
                FROM hotels
            """
    cursor = db.cursor()
    if hotel_id:
        cursor.execute(
            query + "WHERE hotel_id = %s",
            (hotel_id,),
        )
    else:
        cursor.execute(query)
    hotels = cursor.fetchall()
    cursor.close()
    return render_template("hotels.html", hotels=hotels)


@views.route("/employees/")
@views.route("/employees/<int:employee_id>")
def employees(employee_id=None):
    query = r"""SELECT employees.employee_id,
                    employees.first_name,
                    COALESCE(employees.middle_initial, ''),
                    employees.last_name,
                    employees.street_number,
                    employees.street_name,
                    employees.apt_number,
                    employees.city,
                    employees.province_or_state,
                    employees.country,
                    employees.zip,
                    positions.position_name,
                    employees.hotel_id
                FROM employees
                JOIN positions
                ON employees.position_id = positions.position_id
            """
    cursor = db.cursor()
    if employee_id:
        cursor.execute(
            query + "WHERE employee_id = %s",
            (employee_id,),
        )
    else:
        cursor.execute(query)
    employees = cursor.fetchall()
    cursor.close()
    return render_template("employees.html", employees=employees)
