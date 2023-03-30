from flask import Blueprint, render_template, request, session

from . import db

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    print("SESSION:", session)
    if request.method == "GET":
        return render_template(
            "login.html",
            session=session,
            failed_login=False,
        )
    elif request.method == "POST":
        customer_query = r"""SELECT customers.customer_id,
                                    customers.first_name,
                                    customers.last_name
                                FROM customers
                                WHERE customers.ssn = %s
                        """

        employee_query = r"""SELECT employees.employee_id,
                                    employees.first_name,
                                    employees.last_name
                                FROM employees
                                WHERE employees.ssn = %s
                        """

        cursor = db.cursor()
        if request.form.get("customer-or-employee-radio") == "customer":
            cursor.execute(customer_query, (request.form.get("ssn"),))
        elif request.form.get("customer-or-employee-radio") == "employee":
            cursor.execute(employee_query, (request.form.get("ssn"),))

        user = cursor.fetchone()
        if user is None:
            return render_template(
                "login.html",
                session=session,
                failed_login=True,
            )
        else:
            session["user"] = {
                "type": request.form.get("customer-or-employee-radio"),
                "id": user[0],
                "first_name": user[1],
                "last_name": user[2],
            }
            return render_template(
                "login.html",
                session=session,
            )


@auth.route("/logout")
def logout():
    session["user"] = None
    return render_template("login.html", session=session)


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
