import traceback
from datetime import date

from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
from psycopg2.errors import IntegrityError, RaiseException

from . import db

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/chains/")
def chains():
    query = r"""SELECT chains.chain_id,
                    chains.chain_name,
                    chains.num_hotels
                FROM chains
            """
    cursor = db.cursor()
    cursor.execute(query)
    chains = cursor.fetchall()
    cursor.close()
    return render_template("chains.html", session=session, chains=chains)


@views.route("/hotels/<int:chain_id>", methods=["GET"])
@views.route("/hotels/", methods=["GET"])
def hotels(chain_id=None):
    query = r"""SELECT chains.chain_name,
                    hotels.hotel_id,
                    hotels.street_number,
                    hotels.street_name,
                    hotels.city,
                    hotels.province_or_state,
                    hotels.country,
                    hotels.zip,
                    hotels.stars,
                    hotels.num_rooms
                FROM hotels
                JOIN chains
                ON hotels.chain_id = chains.chain_id
            """
    cursor = db.cursor()
    if chain_id:
        cursor.execute(
            query + "WHERE chains.chain_id = %s" + " ORDER BY hotels.hotel_id",
            (chain_id,),
        )
    else:
        cursor.execute(query + " ORDER BY chains.chain_name, hotels.hotel_id")
    hotels = cursor.fetchall()
    cursor.close()
    return render_template(
        "hotels.html", session=session, hotels=hotels, chain_id=chain_id
    )


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
@views.route("/rooms/<int:chain_id>/<int:hotel_id>", methods=["GET", "POST"])
def rooms(chain_id=None, hotel_id=None):
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
        if request.form.get("start-date") != "" and request.form.get("end-date") != "":
            cursor.execute(
                "SELECT * FROM get_available_rooms(%s, %s)",
                (request.form.get("start-date"), request.form.get("end-date")),
            )
        else:
            cursor.execute(
                query
                + "WHERE 1=1"
                + (
                    " AND chains.chain_name = %s"
                    if request.form.get("chain") != ""
                    else ""
                )
                + (" AND hotels.stars >= %s" if request.form.get("stars") != "" else "")
                + (
                    " AND hotels.num_rooms >= %s"
                    if request.form.get("num-rooms") != ""
                    else ""
                )
                + (
                    " AND hotels.country = %s"
                    if request.form.get("country") != ""
                    else ""
                )
                + (
                    " AND hotels.province_or_state = %s"
                    if request.form.get("province-or-state") != ""
                    else ""
                )
                + (" AND hotels.city = %s" if request.form.get("city") != "" else "")
                + (
                    " AND rooms.capacity = %s"
                    if request.form.get("capacity") != ""
                    else ""
                )
                + (" AND rooms.price <= %s" if request.form.get("price") != "" else "")
                + " ORDER BY hotels.chain_id, rooms.hotel_id, rooms.room_number",
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
            chain_id=chain_id,
            hotel_id=hotel_id,
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
        if hotel_id:
            cursor.execute(
                query
                + "WHERE rooms.hotel_id = %s ORDER BY hotels.chain_id, rooms.hotel_id, rooms.room_number",
                (hotel_id,),
            )
        else:
            cursor.execute(
                query + " ORDER BY hotels.chain_id, rooms.hotel_id, rooms.room_number"
            )
        rooms = cursor.fetchall()
        return render_template(
            "rooms.html",
            session=session,
            form=None,
            chain_id=chain_id,
            hotel_id=hotel_id,
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
        try:
            if (
                request.form.get("start-date") != ""
                and request.form.get("end-date") != ""
            ):
                if request.form.get("end-date") < request.form.get("start-date"):
                    flash("End Date must follow Start Date", "danger")
                else:
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
        except RaiseException:
            flash("Room is already booked. Try different dates", "danger")
            db.rollback()

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
    if deleted_room is not None:
        flash("Successfully deleted room", "success")
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
    try:
        query = r"""DELETE FROM chains
                        WHERE chain_id = %s
                        RETURNING chain_id
                """
        cursor = db.cursor()
        cursor.execute(query, (chain_id,))
        deleted_chain = cursor.fetchone()
        if deleted_chain is not None:
            flash("Successfully deleted chain", "success")

        db.commit()
        cursor.close()
    except IntegrityError:
        db.rollback()
        flash("Cannot delete chain", "danger")

    return redirect(url_for("views.chains"))


@views.route("/edit-chain/<int:chain_id>", methods=["GET", "POST"])
def edit_chain(chain_id=None):
    cursor = db.cursor()

    if request.method == "POST" and request.form.get("chain-name") != "":
        try:
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
                flash("Successfully updated chain name", "success")
            db.commit()
        except IntegrityError:
            db.rollback()
            flash("Unable to update chain", "danger")

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
                        FROM chain_offices
                        WHERE chain_offices.chain_id = %s
                    """
    phones_query = r"""SELECT chain_phone_numbers.phone_number,
                            chain_phone_numbers.description,
                            chain_phone_numbers.id AS phone_id
                        FROM chain_phone_numbers
                        WHERE chain_phone_numbers.chain_id = %s
                    """
    emails_query = r"""SELECT chain_email_addresses.email_address,
                            chain_email_addresses.description,
                            chain_email_addresses.id AS email_id
                        FROM chain_email_addresses
                        WHERE chain_email_addresses.chain_id = %s
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
    )


@views.route("/delete-office/<int:chain_id>/<int:office_id>", methods=["POST"])
def delete_office(chain_id=None, office_id=None):
    query = r"""DELETE
                FROM chain_offices
                WHERE id = %s
            """
    cursor = db.cursor()
    cursor.execute(query, (office_id,))
    db.commit()
    cursor.close()
    return redirect(url_for("views.edit_chain", chain_id=chain_id))


@views.route("/edit-office/<int:chain_id>/<int:office_id>", methods=["GET", "POST"])
def edit_office(chain_id=None, office_id=None):
    cursor = db.cursor()
    if request.method == "GET":
        query = r"""SELECT chains.chain_name FROM chains WHERE chains.chain_id = %s"""
        cursor.execute(query, (chain_id,))
        chain_name = cursor.fetchone()
        if chain_name is not None:
            chain_name = chain_name[0]

        query = r"""SELECT chain_offices.street_number,
                            chain_offices.street_name,
                            chain_offices.apt_number,
                            chain_offices.city,
                            chain_offices.province_or_state,
                            chain_offices.country,
                            chain_offices.zip
                    FROM chain_offices
                    WHERE chain_offices.id = %s
                """
        cursor.execute(query, (office_id,))
        office = cursor.fetchone()
        cursor.close()
        return render_template(
            "edit_office.html",
            session=session,
            chain_id=chain_id,
            chain_name=chain_name,
            office_id=office_id,
            office=office,
        )
    elif request.method == "POST":
        try:
            query = (
                "UPDATE chain_offices SET"
                + (
                    " street_number = %s,"
                    if request.form.get("street-number") != ""
                    else ""
                )
                + (
                    " street_name = %s,"
                    if request.form.get("street-name") != ""
                    else ""
                )
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
            data = (
                request.form.get("street-number"),
                request.form.get("street-name"),
                request.form.get("apt-number"),
                request.form.get("city"),
                request.form.get("province-or-state"),
                request.form.get("country"),
                request.form.get("zip"),
            )
            data = tuple(filter(lambda x: x != "", data))
            cursor.execute(query + " WHERE id = %s RETURNING id", data + (office_id,))
            office_id = cursor.fetchone()
            db.commit()
            if office_id is not None:
                office_id = office_id[0]
                flash("Successfully updated chain office address", "success")
        except IntegrityError:
            db.rollback()
            flash("Unable to update chain office address", "danger")

        return redirect(url_for("views.edit_chain", chain_id=chain_id))


@views.route("/delete-phone/<int:chain_id>/<int:phone_id>", methods=["POST"])
def delete_phone(chain_id=None, phone_id=None):
    try:
        query = r"""DELETE
                    FROM chain_phone_numbers
                    WHERE id = %s
                """
        cursor = db.cursor()
        cursor.execute(query, (phone_id,))
        db.commit()
        cursor.close()
    except IntegrityError:
        db.rollback()
        flash("Unable to delete chain phone number", "danger")
    return redirect(url_for("views.edit_chain", chain_id=chain_id))


@views.route("/edit-phone/<int:chain_id>/<int:phone_id>", methods=["GET", "POST"])
def edit_phone(chain_id=None, phone_id=None):
    cursor = db.cursor()
    if request.method == "GET":
        query = r"""SELECT chains.chain_name FROM chains WHERE chains.chain_id = %s"""
        cursor.execute(query, (chain_id,))
        chain_name = cursor.fetchone()
        if chain_name is not None:
            chain_name = chain_name[0]

        query = r"""SELECT chain_phone_numbers.phone_number,
                            chain_phone_numbers.description
                    FROM chain_phone_numbers
                    WHERE chain_phone_numbers.id = %s
                """
        cursor.execute(query, (phone_id,))
        phone = cursor.fetchone()
        db.commit()

        cursor.close()
        return render_template(
            "edit_phone.html",
            session=session,
            chain_id=chain_id,
            chain_name=chain_name,
            phone_id=phone_id,
            phone=phone,
        )
    elif request.method == "POST":
        try:
            query = (
                "UPDATE chain_phone_numbers SET"
                + (
                    " phone_number = %s,"
                    if request.form.get("phone-number") != ""
                    else ""
                )
                + (
                    " description = %s,"
                    if request.form.get("phone-description") != ""
                    else ""
                )
            )
            query = query.strip(",")
            data = (
                request.form.get("phone-number"),
                request.form.get("phone-description"),
            )
            data = tuple(filter(lambda x: x != "", data))
            cursor.execute(
                query + " WHERE id = %s RETURNING id",
                data + (phone_id,),
            )
            phone_id = cursor.fetchone()
            db.commit()
            if phone_id is not None:
                phone_id = phone_id[0]
                flash("Successfully updated chain phone number", "success")
        except IntegrityError:
            db.rollback()
            flash("Unable to update chain phone number", "danger")

        return redirect(url_for("views.edit_chain", chain_id=chain_id))


@views.route("/delete-email/<int:chain_id>/<int:email_id>", methods=["POST"])
def delete_email(chain_id=None, email_id=None):
    try:
        query = r"""DELETE
                    FROM chain_email_addresses
                    WHERE id = %s
                """
        cursor = db.cursor()
        cursor.execute(query, (email_id,))
        db.commit()
        cursor.close()
    except IntegrityError:
        db.rollback()
        flash("Unable to delete chain email address", "danger")

    return redirect(url_for("views.edit_chain", chain_id=chain_id))


@views.route("/edit-email/<int:chain_id>/<int:email_id>", methods=["GET", "POST"])
def edit_email(chain_id=None, email_id=None):
    cursor = db.cursor()
    if request.method == "GET":
        query = r"""SELECT chains.chain_name FROM chains WHERE chains.chain_id = %s"""
        cursor.execute(query, (chain_id,))
        chain_name = cursor.fetchone()
        if chain_name is not None:
            chain_name = chain_name[0]

        query = r"""SELECT chain_email_addresses.email_address,
                            chain_email_addresses.description
                    FROM chain_email_addresses
                    WHERE chain_email_addresses.id = %s
                """
        cursor.execute(query, (email_id,))
        email = cursor.fetchone()

        cursor.close()
        return render_template(
            "edit_email.html",
            session=session,
            chain_id=chain_id,
            chain_name=chain_name,
            email_id=email_id,
            email=email,
        )
    elif request.method == "POST":
        try:
            query = (
                "UPDATE chain_email_addresses SET"
                + (
                    " email_address = %s,"
                    if request.form.get("email-address") != ""
                    else ""
                )
                + (
                    " description = %s,"
                    if request.form.get("email-description") != ""
                    else ""
                )
            )
            query = query.strip(",")
            data = (
                request.form.get("email-address"),
                request.form.get("email-description"),
            )
            data = tuple(filter(lambda x: x != "", data))
            cursor.execute(
                query + " WHERE id = %s RETURNING id",
                data + (email_id,),
            )
            email_id = cursor.fetchone()
            db.commit()
            if email_id is not None:
                email_id = email_id[0]
                flash("Successfully updated chain email address", "success")
        except IntegrityError:
            db.rollback()
            flash("Unable to update chain email address", "danger")

        return redirect(url_for("views.edit_chain", chain_id=chain_id))


@views.route("/edit-room/<int:hotel_id>/<string:room_number>", methods=["GET", "POST"])
def edit_room(hotel_id=None, room_number=None):
    cursor = db.cursor()
    if request.method == "GET":
        query = r"""SELECT rooms.room_number,
                        rooms.capacity,
                        rooms.price,
                        rooms.extensible,
                        rooms.tv,
                        rooms.air_condition,
                        rooms.fridge,
                        view_types.description
                    FROM rooms
                    JOIN view_types
                    ON rooms.view_type = view_types.id
                    WHERE rooms.hotel_id = %s AND rooms.room_number = %s
                """
        cursor.execute(query, (hotel_id, room_number))
        room = cursor.fetchone()

        damages_query = r"""SELECT description FROM room_damages WHERE hotel_id = %s AND room_number = %s"""
        cursor.execute(damages_query, (hotel_id, room_number))
        damages = cursor.fetchall()
        if damages is not None:
            damages = [damage[0] for damage in damages]

        return render_template(
            "edit_room.html",
            session=session,
            hotel_id=hotel_id,
            room=room,
            damages=damages,
        )


@views.route(
    "/edit-room-details/<int:hotel_id>/<string:room_number>", methods=["GET", "POST"]
)
def edit_room_details(hotel_id=None, room_number=None):
    cursor = db.cursor()
    if request.method == "GET":
        query = r"""SELECT rooms.room_number,
                        rooms.capacity,
                        rooms.price,
                        rooms.extensible,
                        rooms.tv,
                        rooms.air_condition,
                        rooms.fridge,
                        view_types.description
                    FROM rooms
                    JOIN view_types
                    ON rooms.view_type = view_types.id
                    WHERE rooms.hotel_id = %s AND rooms.room_number = %s
                """
        cursor.execute(query, (hotel_id, room_number))
        room = cursor.fetchone()

        views_query = r"""SELECT id, description FROM view_types"""
        cursor.execute(views_query)
        views = cursor.fetchall()

        return render_template(
            "edit_room_details.html",
            session=session,
            hotel_id=hotel_id,
            room_number=room_number,
            room=room,
            views=views,
        )
    elif request.method == "POST":
        try:
            query = (
                "UPDATE rooms SET"
                + (" capacity = %s," if request.form.get("capacity") != "" else "")
                + (" price = %s," if request.form.get("price") != "" else "")
                + (" extensible = %s," if request.form.get("extensible") != "" else "")
                + (" tv = %s," if request.form.get("tv") != "" else "")
                + (
                    " air_condition = %s,"
                    if request.form.get("air-condition") != ""
                    else ""
                )
                + (" fridge = %s," if request.form.get("fridge") != "" else "")
                + (" view_type = %s," if request.form.get("view") != "" else "")
            )
            query = query.strip(",")
            data = (
                request.form.get("capacity"),
                request.form.get("price"),
                request.form.get("extensible"),
                request.form.get("tv"),
                request.form.get("air-condition"),
                request.form.get("fridge"),
                request.form.get("view"),
            )
            data = tuple(filter(lambda x: x != "", data))
            cursor.execute(
                query
                + " WHERE hotel_id = %s AND room_number = %s RETURNING hotel_id, room_number",
                data + (hotel_id, room_number),
            )
            room = cursor.fetchone()
            db.commit()
            if room is not None:
                flash("Successfully updated room details", "success")
        except IntegrityError:
            db.rollback()
            flash("Unable to update room details", "danger")

        return redirect(
            url_for("views.edit_room", hotel_id=hotel_id, room_number=room_number)
        )


@views.route("/edit-hotel/<int:hotel_id>", methods=["GET", "POST"])
def edit_hotel(hotel_id=None):
    cursor = db.cursor()
    if request.method == "GET":
        query = r"""SELECT chains.chain_name,
                            hotels.street_number,
                            hotels.street_name,
                            hotels.city,
                            hotels.province_or_state,
                            hotels.country,
                            hotels.zip,
                            hotels.stars
                    FROM hotels
                    JOIN chains
                    ON hotels.chain_id = chains.chain_id
                    WHERE hotels.hotel_id = %s
                """
        cursor.execute(query, (hotel_id,))
        hotel = cursor.fetchone()

        phones_query = r"""SELECT hotel_phone_numbers.phone_number,
                                    hotel_phone_numbers.description,
                                    hotel_phone_numbers.id AS phone_id
                            FROM hotel_phone_numbers
                            WHERE hotel_phone_numbers.hotel_id = %s
                        """
        cursor.execute(phones_query, (hotel_id,))
        phones = cursor.fetchall()

        emails_query = r"""SELECT hotel_email_addresses.email_address,
                                    hotel_email_addresses.description,
                                    hotel_email_addresses.id AS email_id
                            FROM hotel_email_addresses
                            WHERE hotel_email_addresses.hotel_id = %s
                        """
        cursor.execute(emails_query, (hotel_id,))
        emails = cursor.fetchall()

        cursor.close()
        return render_template(
            "edit_hotel.html",
            session=session,
            hotel_id=hotel_id,
            hotel=hotel,
            phones=phones,
            emails=emails,
        )
    elif request.method == "POST":
        return redirect(url_for("views.hotels", hotel_id=hotel_id))


@views.route("/edit-hotel-address/<int:hotel_id>", methods=["GET", "POST"])
def edit_hotel_address(hotel_id=None):
    cursor = db.cursor()
    if request.method == "GET":
        query = r"""SELECT chains.chain_name,
                            hotels.street_number,
                            hotels.street_name,
                            hotels.city,
                            hotels.province_or_state,
                            hotels.country,
                            hotels.zip,
                            hotels.stars
                    FROM hotels
                    JOIN chains
                    ON hotels.chain_id = chains.chain_id
                    WHERE hotels.hotel_id = %s
                """
        cursor.execute(query, (hotel_id,))
        hotel = cursor.fetchone()

        cursor.close()
        return render_template(
            "edit_hotel_address.html", session=session, hotel_id=hotel_id, hotel=hotel
        )
    elif request.method == "POST":
        try:
            query = (
                "UPDATE hotels SET"
                + (
                    " street_number = %s,"
                    if request.form.get("street-number") != ""
                    else ""
                )
                + (
                    " street_name = %s,"
                    if request.form.get("street-name") != ""
                    else ""
                )
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
            data = (
                request.form.get("street-number"),
                request.form.get("street-name"),
                request.form.get("city"),
                request.form.get("province-or-state"),
                request.form.get("country"),
                request.form.get("zip"),
            )
            data = tuple(filter(lambda x: x != "", data))
            cursor.execute(
                query + " WHERE hotel_id = %s RETURNING hotel_id",
                data + (hotel_id,),
            )
            hotel_id = cursor.fetchone()
            db.commit()
            if hotel_id is not None:
                hotel_id = hotel_id[0]
                flash("Successfully updated hotel address", "success")
        except IntegrityError:
            db.rollback()
            flash("Unable to update hotel address", "danger")

        return redirect(url_for("views.edit_hotel", hotel_id=hotel_id))


@views.route("/delete-hotel/<int:hotel_id>", methods=["POST"])
def delete_hotel(hotel_id=None):
    try:
        cursor = db.cursor()
        cursor.execute(
            r"""DELETE FROM hotels WHERE hotel_id = %s RETURNING hotel_id""",
            (hotel_id,),
        )
        hotel_id = cursor.fetchone()
        if hotel_id is not None:
            hotel_id = hotel_id[0]
            flash("Successfully deleted hotel", "success")
        db.commit()
        cursor.close()
    except IntegrityError:
        traceback.print_exc()
        db.rollback()
        flash("Unable to delete hotel", "danger")

    return redirect(url_for("views.hotels"))


@views.route("/edit-hotel-phone/<int:hotel_id>/<int:phone_id>", methods=["GET", "POST"])
def edit_hotel_phone(hotel_id=None, phone_id=None):
    if request.method == "GET":
        return render_template("edit_hotel_phone.html", session=session)


@views.route("/delete-hotel-phone/<int:hotel_id>/<int:phone_id>", methods=["POST"])
def delete_hotel_phone(hotel_id=None, phone_id=None):
    try:
        cursor = db.cursor()
        cursor.execute(
            r"""DELETE FROM hotel_phone_numbers WHERE id = %s""", (phone_id,)
        )
        db.commit()
        cursor.close()
    except IntegrityError:
        traceback.print_exc()
        db.rollback()
        flash("Unable to delete hotel phone number", "danger")

    return redirect(url_for("views.edit_hotel", hotel_id=hotel_id))


@views.route("/edit-hotel-email/<int:hotel_id>/<int:email_id>", methods=["GET", "POST"])
def edit_hotel_email(hotel_id=None, email_id=None):
    pass


@views.route("/delete-hotel-email/<int:hotel_id>/<int:email_id>", methods=["POST"])
def delete_hotel_email(hotel_id=None, email_id=None):
    try:
        cursor = db.cursor()
        cursor.execute(
            r"""DELETE FROM hotel_email_addresses WHERE id = %s""", (email_id,)
        )
        db.commit()
        cursor.close()
    except IntegrityError:
        traceback.print_exc()
        db.rollback()
        flash("Unable to delete hotel email address", "danger")

    return redirect(url_for("views.edit_hotel", hotel_id=hotel_id))


@views.route("/edit-hotel-stars/<int:hotel_id>", methods=["POST"])
def edit_hotel_stars(hotel_id=None):
    cursor = db.cursor()
    try:
        cursor.execute(
            r"""UPDATE hotels SET stars = %s WHERE hotel_id = %s""",
            (request.form.get("stars"), hotel_id),
        )
        db.commit()
        cursor.close()
        flash("Successfully updated hotel stars", "success")
    except IntegrityError:
        traceback.print_exc()
        db.rollback()
        flash("Unable to update hotel stars", "danger")

    return redirect(url_for("views.edit_hotel", hotel_id=hotel_id))


@views.route("/bookings/", methods=["GET", "POST"])
def bookings():
    form = None
    cursor = db.cursor()
    query = r"""SELECT chains.chain_name,
                        bookings.hotel_id,
                        bookings.room_number,
                        bookings.start_date,
                        bookings.end_date,
                        customers.first_name,
                        customers.last_name,
                        bookings.booking_id
                FROM bookings
                JOIN customers
                ON bookings.customer_id = customers.customer_id
                JOIN hotels
                ON bookings.hotel_id = hotels.hotel_id
                JOIN chains
                ON hotels.chain_id = chains.chain_id
            """

    if request.method == "GET":
        cursor.execute(query)
        bookings = cursor.fetchall()
    elif request.method == "POST":
        form = request.form
        data = (
            request.form.get("first-name"),
            request.form.get("last-name"),
        )
        data = tuple(filter(lambda x: x != "", data))
        data = tuple((f"%{x}%",) for x in data)

        cursor.execute(
            query
            + " WHERE 1=1"
            + (
                " AND customers.first_name ILIKE %s"
                if request.form.get("first-name") != ""
                else ""
            )
            + (
                " AND customers.last_name ILIKE %s"
                if request.form.get("last-name") != ""
                else ""
            ),
            data,
        )
        bookings = cursor.fetchall()

    cursor.close()
    return render_template(
        "bookings.html", session=session, form=form, bookings=bookings
    )


@views.route("/rent/")
@views.route("/rent/<string:booking_id>", methods=["GET", "POST"])
@views.route(
    "/rent/<string:customer_ssn>/<int:hotel_id>/<string:room_number>/<float:price>/<string:start_date>/<string:end_date>",
    methods=["GET", "POST"],
)
def rent(
    booking_id=None,
    customer_ssn=None,
    hotel_id=None,
    room_number=None,
    price=None,
    start_date=None,
    end_date=None,
):
    cursor = db.cursor()
    if booking_id is not None:
        query = r"""SELECT bookings.hotel_id,
                            bookings.room_number,
                            bookings.start_date,
                            bookings.end_date,
                            rooms.price
                    FROM bookings
                    JOIN rooms
                    ON bookings.hotel_id = rooms.hotel_id
                        AND bookings.room_number = rooms.room_number
                    WHERE bookings.booking_id = %s
                """
        cursor.execute(query, (booking_id,))
        booking = cursor.fetchone()

        customer_query = r"""SELECT customers.customer_id,
                                    customers.ssn,
                                    customers.registration_date,
                                    customers.first_name,
                                    customers.last_name
                                FROM bookings
                                JOIN customers
                                ON bookings.customer_id = customers.customer_id
                                WHERE bookings.booking_id = %s
                            """
        cursor.execute(customer_query, (booking_id,))
        customer = cursor.fetchone()

        paid_query = r"""SELECT rentals.paid_amount
                            FROM rentals
                            WHERE rentals.booking_id = %s
                    """
        cursor.execute(paid_query, (booking_id,))
        paid = cursor.fetchone()
        if paid is not None:
            paid = paid[0]

    if request.method == "GET":
        if booking_id is not None:
            return render_template(
                "rent.html",
                session=session,
                booking_id=booking_id,
                booking=booking,
                customer=customer,
                paid=paid,
            )
        else:
            return render_template(
                "rent.html",
                session=session,
                booking_id=None,
                customer_ssn=customer_ssn,
                hotel_id=hotel_id,
                room_number=room_number,
                price=price,
                start_date=start_date,
                end_date=end_date,
            )
    elif request.method == "POST":
        if booking_id is not None:
            try:
                rent_query = r"""INSERT INTO rentals
                                (customer_id, booking_id, hotel_id, room_number, start_date, end_date, paid_amount)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                RETURNING rental_id
                            """
                cursor.execute(
                    rent_query,
                    (
                        customer[0],
                        booking_id,
                        booking[0],
                        booking[1],
                        booking[2],
                        booking[3],
                        request.form.get("paid-amount"),
                    ),
                )
                rental_id = cursor.fetchone()[0]
                if rental_id is not None:
                    flash("Successfully rented room", "success")
                db.commit()
                cursor.close()
            except IntegrityError:
                traceback.print_exc()
                db.rollback()
                flash("Unable to rent room", "danger")

            return redirect(url_for("views.rent", booking_id=booking_id))
        else:
            new_rent_query = r"""INSERT INTO rentals
                                (customer_id, hotel_id, room_number, start_date, end_date, paid_amount)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                RETURNING rental_id
                            """

            customer_query = r"""SELECT customer_id FROM customers WHERE ssn = %s"""
            cursor.execute(customer_query, (customer_ssn,))
            customer_id = cursor.fetchone()[0]

            cursor.execute(
                new_rent_query,
                (
                    customer_id,
                    hotel_id,
                    room_number,
                    start_date,
                    end_date,
                    request.form.get("paid-amount"),
                ),
            )
            rental_id = cursor.fetchone()
            if rental_id is not None:
                flash("Successfully rented room", "success")
            cursor.close()
            db.commit()

            return redirect(url_for("views.rent"))


@views.route("/get-available-rooms/", methods=["GET"])
def get_available_rooms():
    cursor = db.cursor()

    hotel_query = r"""SELECT hotel_id FROM employees WHERE employee_id = %s"""
    cursor.execute(hotel_query, (session.get("user").get("id"),))
    hotel_id = cursor.fetchone()
    if hotel_id is not None:
        hotel_id = hotel_id[0]

    query = r"""SELECT chain_name,
                        stars,
                        num_rooms,
                        country,
                        province_or_state,
                        city,
                        address,
                        room_number,
                        capacity,
                        description,
                        price,
                        hotel_id
                FROM get_available_rooms(%s, %s)
                WHERE hotel_id = %s
            """
    cursor.execute(
        query,
        (
            date.fromisoformat(request.args.get("start-date")),
            date.fromisoformat(request.args.get("end-date")),
            hotel_id,
        ),
    )
    rooms = cursor.fetchall()

    return render_template(
        "available_rooms.html",
        session=session,
        customer_ssn=request.args.get("customer-ssn"),
        rooms=rooms,
        hotel_id=hotel_id,
        start_date=request.args.get("start-date"),
        end_date=request.args.get("end-date"),
    )


@views.route("/rentals/")
@views.route("/rentals/<int:rental_id>")
def rentals(rental_id=None):
    query = r"""SELECT rentals.rental_id,
                        rentals.customer_id,
                        rentals.booking_id,
                        rentals.hotel_id,
                        rentals.room_number,
                        rentals.start_date,
                        rentals.end_date,
                        rentals.paid_amount
                FROM rentals
            """
    cursor = db.cursor()
    cursor.execute(query)
    rentals = cursor.fetchall()

    cursor.close()
    return render_template(
        "rentals.html", session=session, rental_id=rental_id, rentals=rentals
    )


@views.route("/view-one")
def view_one():
    query = r"""SELECT country,
                        province_or_state,
                        city,
                        num_available_rooms
                FROM available_rooms_per_area
            """
    cursor = db.cursor()
    cursor.execute(query)
    rooms = cursor.fetchall()
    cursor.close()

    return render_template("view_one.html", rooms=rooms)


@views.route("/view-two/", methods=["GET", "POST"])
def view_two(hotel_id=None):
    query = r"""SELECT chain_name,
                        hotel_id,
                        country,
                        province_or_state,
                        city,
                        room_number,
                        capacity
                FROM room_capacities
            """
    cursor = db.cursor()
    if request.method == "GET":
        cursor.execute(query)
        capacities = cursor.fetchall()
    elif request.method == "POST":
        cursor.execute(query + " WHERE hotel_id = %s", (request.form.get("hotel-id"),))
        capacities = cursor.fetchall()

    cursor.close()
    return render_template("view_two.html", capacities=capacities)
