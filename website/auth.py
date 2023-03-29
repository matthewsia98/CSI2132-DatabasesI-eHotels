from flask import Blueprint, render_template, request

from . import db

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html", logged_in=False)


@auth.route("/logout")
def logout():
    return "<p>Logout</p>"


@auth.route("/sign-up/", methods=["GET", "POST"])
def sign_up():
    cursor = db.cursor()

    if request.method == "GET":
        positions_query = r"""SELECT positions.position_id,
                        positions.position_name
                    FROM positions
                """
        cursor.execute(positions_query)
        positions = cursor.fetchall()

        hotels_query = r"""SELECT
                            hotels.hotel_id,
                            chains.chain_name,
                            CONCAT(hotels.street_number, ' ', hotels.street_name, ', ', hotels.zip) as address
                            FROM hotels
                            JOIN chains ON hotels.chain_id = chains.chain_id
                        """
        cursor.execute(hotels_query)
        hotels = cursor.fetchall()
        return render_template(
            "sign_up.html", positions=positions, hotels=hotels, inserted_id=None
        )
    elif request.method == "POST":
        customer_query = r"""INSERT INTO customers
                            (ssn, first_name, middle_initial, last_name,
                             street_number, street_name, apt_number,
                             city, province_or_state, country, zip)
                            VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING customer_id;
                        """
        employee_query = r"""INSERT INTO employees
                            (ssn, first_name, middle_initial, last_name,
                             street_number, street_name, apt_number,
                             city, province_or_state, country, zip,
                             position_id, hotel_id)
                            VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING employee_id;
                        """

        if request.form.get("customer-or-employee-radio") == "customer":
            cursor.execute(
                customer_query,
                (
                    request.form.get("ssn"),
                    request.form.get("first-name"),
                    request.form.get("middle-initial"),
                    request.form.get("last-name"),
                    request.form.get("street-number"),
                    request.form.get("street-name"),
                    request.form.get("apt-number"),
                    request.form.get("city"),
                    request.form.get("province-or-state"),
                    request.form.get("country"),
                    request.form.get("zip"),
                ),
            )
        elif request.form.get("customer-or-employee-radio") == "employee":
            cursor.execute(
                employee_query,
                (
                    request.form.get("ssn"),
                    request.form.get("first-name"),
                    request.form.get("middle-initial"),
                    request.form.get("last-name"),
                    request.form.get("street-number"),
                    request.form.get("street-name"),
                    request.form.get("apt-number"),
                    request.form.get("city"),
                    request.form.get("province-or-state"),
                    request.form.get("country"),
                    request.form.get("zip"),
                    request.form.get("position"),
                    request.form.get("hotel"),
                ),
            )
        inserted_id = cursor.fetchone()
        if inserted_id is not None:
            inserted_id = inserted_id[0]
            db.commit()
        cursor.close()
        return render_template("sign_up.html", inserted_id=inserted_id)
