from datetime import date

from flask import (Blueprint, redirect, render_template, request, session,
                   url_for)

from . import db

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/chains/")
@views.route("/chains/<int:chain_id>")
def chains(chain_id=None):
    query = r"""SELECT chains.chain_id,
                    chains.chain_name,
                    chains.num_hotels
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
    return render_template("chains.html", session=session, chains=chains)


@views.route("/hotels/")
@views.route("/hotels/<int:hotel_id>")
def hotels(hotel_id=None):
    query = r"""SELECT hotels.hotel_id,
                    hotels.street_number,
                    hotels.street_name,
                    hotels.city,
                    hotels.province_or_state,
                    hotels.country,
                    hotels.zip,
                    hotels.stars,
                    hotels.num_rooms,
                    hotels.chain_id
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
    return render_template("hotels.html", session=session, hotels=hotels)


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
    return render_template("employees.html", session=session, employees=employees)


@views.route("/rooms/", methods=["GET", "POST"])
def rooms():
    cursor = db.cursor()

    capacities_query = r"""SELECT DISTINCT capacity
                            FROM rooms
                            ORDER BY capacity
                        """
    cursor.execute(capacities_query)
    capacities = cursor.fetchall()
    capacities = [capacity[0] for capacity in capacities]

    cities_query = r"""SELECT DISTINCT city
                        FROM hotels
                        ORDER BY city
                    """
    cursor.execute(cities_query)
    cities = cursor.fetchall()
    cities = [city[0] for city in cities]

    chains_query = r"""SELECT DISTINCT chain_name
                        FROM chains
                        ORDER BY chain_name
                    """
    cursor.execute(chains_query)
    chains = cursor.fetchall()
    chains = [chain[0] for chain in chains]

    countries_query = r"""SELECT DISTINCT country
                            FROM hotels
                            ORDER BY country
                        """
    cursor.execute(countries_query)
    countries = cursor.fetchall()
    countries = [country[0] for country in countries]

    provinces_or_states_query = r"""SELECT DISTINCT province_or_state
                                    FROM hotels
                                    ORDER BY province_or_state
                                """
    cursor.execute(provinces_or_states_query)
    provinces_or_states = cursor.fetchall()
    provinces_or_states = [
        province_or_state[0] for province_or_state in provinces_or_states
    ]

    stars_query = r"""SELECT DISTINCT stars
                        FROM hotels
                        ORDER BY stars
                    """
    cursor.execute(stars_query)
    stars = cursor.fetchall()
    stars = [star[0] for star in stars]

    num_rooms_query = r"""SELECT DISTINCT num_rooms
                            FROM hotels
                            ORDER BY num_rooms
                        """
    cursor.execute(num_rooms_query)
    num_rooms = cursor.fetchall()
    num_rooms = [num_room[0] for num_room in num_rooms]
    max_num_rooms = max(num_rooms)

    query = r"""SELECT chains.chain_name,
                    hotels.stars,
                    hotels.num_rooms,
                    hotels.country,
                    hotels.province_or_state,
                    hotels.city,
                    CONCAT(hotels.street_number, ' ', hotels.street_name, ', ', hotels.zip) AS address,
                    rooms.room_number,
                    rooms.capacity,
                    view_types.description,
                    rooms.price,
                    hotels.hotel_id
                FROM rooms
                JOIN hotels
                ON rooms.hotel_id = hotels.hotel_id
                JOIN chains
                ON hotels.chain_id = chains.chain_id
                JOIN view_types
                ON rooms.view_type = view_types.id
            """
    if request.method == "POST":
        cursor.execute(
            query
            + "WHERE 1=1"
            + (" AND chains.chain_name = %s" if request.form.get("chain") != "" else "")
            + (" AND hotels.stars >= %s" if request.form.get("stars") != "" else "")
            + (
                " AND hotels.num_rooms >= %s"
                if request.form.get("num-rooms") != ""
                else ""
            )
            + (" AND hotels.country = %s" if request.form.get("country") != "" else "")
            + (
                " AND hotels.province_or_state = %s"
                if request.form.get("province-or-state") != ""
                else ""
            )
            + (" AND hotels.city = %s" if request.form.get("city") != "" else "")
            + (" AND rooms.capacity = %s" if request.form.get("capacity") != "" else "")
            + (" AND rooms.price <= %s" if request.form.get("price") != "" else ""),
            tuple(
                request.form.get(key)
                for key in request.form
                if request.form.get(key) != ""
            ),
        )
        rooms = cursor.fetchall()
        return render_template(
            "rooms.html",
            session=session,
            form=request.form,
            rooms=rooms,
            capacities=capacities,
            countries=countries,
            cities=cities,
            chains=chains,
            provinces_or_states=provinces_or_states,
            stars=stars,
            num_rooms=num_rooms,
            max_num_rooms=max_num_rooms,
        )
    elif request.method == "GET":
        cursor.execute(query)
        rooms = cursor.fetchall()
        return render_template(
            "rooms.html",
            session=session,
            form=None,
            rooms=rooms,
            capacities=capacities,
            countries=countries,
            cities=cities,
            chains=chains,
            provinces_or_states=provinces_or_states,
            stars=stars,
            num_rooms=num_rooms,
            max_num_rooms=max_num_rooms,
        )

    cursor.close()


@views.route("/book-room/<int:hotel_id>/<string:room_number>", methods=["GET", "POST"])
def book_room(hotel_id=None, room_number=None):
    booking = None
    cursor = db.cursor()

    query = r"""SELECT chains.chain_name,
                    hotels.country,
                    hotels.province_or_state,
                    hotels.city,
                    CONCAT(hotels.street_number, ' ', hotels.street_name) AS address,
                    hotels.zip,
                    rooms.room_number,
                    rooms.capacity,
                    view_types.description,
                    rooms.extensible,
                    rooms.tv,
                    rooms.air_condition,
                    rooms.fridge,
                    rooms.price
                FROM rooms
                JOIN hotels
                ON rooms.hotel_id = hotels.hotel_id
                JOIN chains
                ON hotels.chain_id = chains.chain_id
                JOIN view_types
                ON rooms.view_type = view_types.id
                WHERE rooms.hotel_id = %s AND rooms.room_number = %s
                """
    cursor.execute(query, (hotel_id, room_number))
    room = cursor.fetchone()

    if request.method == "POST":
        if request.form.get("start-date") != "" and request.form.get("end-date") != "":
            booking_query = r"""INSERT INTO
                                bookings (customer_id, hotel_id, room_number, start_date, end_date)
                                VALUES (%s, %s, %s, %s, %s)
                                RETURNING booking_id, start_date, end_date;
                            """
            cursor.execute(
                booking_query,
                (
                    session.get("user").get("id"),
                    hotel_id,
                    room_number,
                    date.fromisoformat(request.form.get("start-date")),
                    date.fromisoformat(request.form.get("end-date")),
                ),
            )
            booking = cursor.fetchone()
            db.commit()

    cursor.close()
    return render_template(
        "book_room.html", session=session, hotel_id=hotel_id, room=room, booking=booking
    )


@views.route("/delete-room/<int:hotel_id>/<string:room_number>", methods=["POST"])
def delete_room(hotel_id=None, room_number=None):
    query = r"""DELETE FROM rooms
                    WHERE hotel_id = %s AND room_number = %s
                    RETURNING hotel_id, room_number
            """
    cursor = db.cursor()
    cursor.execute(query, (hotel_id, room_number))
    deleted_room = cursor.fetchone()
    db.commit()
    cursor.close()
    return redirect(url_for("views.rooms"))


@views.route("/edit-user/", methods=["GET", "POST"])
def edit_user():
    update_success = False
    cursor = db.cursor()
    if session.get("user").get("type") == "customer":
        customer_query = r"""SELECT customers.ssn,
                                    customers.first_name,
                                    customers.middle_initial,
                                    customers.last_name,
                                    customers.street_number,
                                    customers.street_name,
                                    customers.apt_number,
                                    customers.city,
                                    customers.province_or_state,
                                    customers.country,
                                    customers.zip
                                FROM customers
                                WHERE customer_id = %s
                        """
        cursor.execute(customer_query, (session.get("user").get("id"),))
        user = cursor.fetchone()
    elif session.get("user").get("type") == "employee":
        employee_query = r"""SELECT employees.ssn,
                                    employees.first_name,
                                    employees.middle_initial,
                                    employees.last_name,
                                    employees.street_number,
                                    employees.street_name,
                                    employees.apt_number,
                                    employees.city,
                                    employees.province_or_state,
                                    employees.country,
                                    employees.zip
                                FROM employees
                                WHERE employee_id = %s
                        """
        cursor.execute(employee_query, (session.get("user").get("id"),))
        user = cursor.fetchone()

    if request.method == "POST":
        query = (
            (
                "UPDATE employees SET"
                if session.get("user").get("type") == "employee"
                else "UPDATE customers SET"
            )
            + (" ssn = %s," if request.form.get("ssn") != "" else "")
            + (" first_name = %s," if request.form.get("first-name") != "" else "")
            + (
                " middle_initial = %s,"
                if request.form.get("middle-initial") != ""
                else ""
            )
            + (" last_name = %s," if request.form.get("last-name") != "" else "")
            + (
                " street_number = %s,"
                if request.form.get("street-number") != ""
                else ""
            )
            + (" street_name = %s," if request.form.get("street-name") != "" else "")
            + (" apt_number = %s," if request.form.get("apt-number") != "" else "")
            + (" city = %s," if request.form.get("city") != "" else "")
            + (
                " province_or_state = %s,"
                if request.form.get("province-or-state") != ""
                else ""
            )
            + (" country = %s," if request.form.get("country") != "" else "")
            + (" zip = %s," if request.form.get("zip") != "" else "")
        )
        query = query.strip(",")
        cursor.execute(
            query
            + (
                " WHERE customer_id = %s"
                if session.get("user").get("type") == "customer"
                else " WHERE employee_id = %s"
            )
            + " RETURNING *;",
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
                session.get("user").get("id"),
            ),
        )
        result = cursor.fetchone()
        if result is not None:
            update_success = True
        db.commit()

    cursor.close()
    return render_template(
        "edit_user.html", session=session, user=user, update_success=update_success
    )


@views.route("/delete-chain/<int:chain_id>", methods=["POST"])
def delete_chain(chain_id=None):
    query = r"""DELETE FROM chains
                    WHERE chain_id = %s
                    RETURNING chain_id
            """
    cursor = db.cursor()
    cursor.execute(query, (chain_id,))
    deleted_chain = cursor.fetchone()
    db.commit()
    cursor.close()
    return redirect(url_for("views.chains"))


@views.route("/edit-chain/<int:chain_id>", methods=["GET", "POST"])
def edit_chain(chain_id=None):
    update_success = False
    cursor = db.cursor()

    if request.method == "POST" and request.form.get("chain-name") != "":
        cursor.execute(
            r"""UPDATE chains
                    SET chain_name = %s
                    WHERE chain_id = %s
                RETURNING chain_id
            """,
            (request.form.get("chain-name"), chain_id),
        )
        changed_name = cursor.fetchone()
        if changed_name is not None:
            update_success = True
        db.commit()

    chain_query = r"""SELECT chains.chain_id,
                            chains.chain_name
                        FROM chains
                        WHERE chains.chain_id = %s
                    """

    offices_query = r"""SELECT chain_offices.street_number,
                            chain_offices.street_name,
                            chain_offices.apt_number,
                            chain_offices.city,
                            chain_offices.province_or_state,
                            chain_offices.country,
                            chain_offices.zip,
                            chain_offices.id AS office_id
                        FROM chains
                        JOIN chain_offices
                        ON chains.chain_id = chain_offices.chain_id
                        WHERE chains.chain_id = %s
                    """
    phones_query = r"""SELECT chain_phone_numbers.phone_number,
                            chain_phone_numbers.description,
                            chain_phone_numbers.id AS phone_id
                        FROM chains
                        JOIN chain_phone_numbers
                        ON chains.chain_id = chain_phone_numbers.chain_id
                        WHERE chains.chain_id = %s
                    """
    emails_query = r"""SELECT chain_email_addresses.email_address,
                            chain_email_addresses.description,
                            chain_email_addresses.id AS email_id
                        FROM chains
                        JOIN chain_email_addresses
                        ON chains.chain_id = chain_email_addresses.chain_id
                        WHERE chains.chain_id = %s
                    """
    cursor.execute(chain_query, (chain_id,))
    chain = cursor.fetchone()

    cursor.execute(offices_query, (chain_id,))
    offices = cursor.fetchall()

    cursor.execute(phones_query, (chain_id,))
    phones = cursor.fetchall()

    cursor.execute(emails_query, (chain_id,))
    emails = cursor.fetchall()

    cursor.close()
    return render_template(
        "edit_chain.html",
        session=session,
        chain=chain,
        offices=offices,
        phones=phones,
        emails=emails,
        update_success=update_success,
    )


@views.route("/delete-office/<int:office_id>", methods=["POST"])
def delete_office(office_id=None):
    query = r"""DELETE
                FROM chain_offices
                WHERE id = %s
            """
    cursor = db.cursor()
    cursor.execute(query, (office_id,))
    db.commit()
    cursor.close()
    return redirect(url_for("views.edit_chain"))


@views.route("/edit-office/<int:office_id>", methods=["GET", "POST"])
def edit_office(office_id=None):
    pass


@views.route("/delete-phone/<int:phone_id>", methods=["POST"])
def delete_phone(phone_id=None):
    query = r"""DELETE
                FROM chain_phone_numbers
                WHERE id = %s
            """
    cursor = db.cursor()
    cursor.execute(query, (phone_id,))
    db.commit()
    cursor.close()
    return redirect(url_for("views.edit_chain"))


@views.route("/edit-phone/<int:phone_id>", methods=["GET", "POST"])
def edit_phone(phone_id=None):
    pass


@views.route("/delete-email/<int:email_id>", methods=["POST"])
def delete_email(email_id=None):
    query = r"""DELETE
                FROM chain_email_addresses
                WHERE id = %s
            """
    cursor = db.cursor()
    cursor.execute(query, (email_id,))
    db.commit()
    cursor.close()
    return redirect(url_for("views.edit_chain"))


@views.route("/edit-email/<int:email_id>", methods=["GET", "POST"])
def edit_email(email_id=None):
    pass


@views.route("/edit-room/<int:hotel_id>/<string:room_number>", methods=["GET", "POST"])
def edit_room(hotel_id=None, room_number=None):
    pass


@views.route("/edit-hotel/<int:hotel_id>", methods=["GET", "POST"])
def edit_hotel(hotel_id=None):
    pass


@views.route("/delete-hotel/<int:hotel_id>", methods=["POST"])
def delete_hotel(hotel_id=None):
    cursor = db.cursor()
    cursor.execute(r"""DELETE FROM hotels WHERE hotel_id = %s""", (hotel_id,))
    db.commit()
    cursor.close()
    return redirect(url_for("views.hotels"))
