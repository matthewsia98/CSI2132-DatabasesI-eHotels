from flask import Blueprint, render_template, request

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
    return render_template("chains.html", chains=chains)


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
                    hotels.city,
                    hotels.num_rooms,
                    hotels.stars,
                    rooms.room_number,
                    rooms.capacity,
                    view_types.description,
                    rooms.price
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
            + (" AND rooms.capacity = %s" if request.form["capacity"] != "" else "")
            + (" AND hotels.city = %s" if request.form["city"] != "" else "")
            + (" AND chains.chain_name = %s" if request.form["chain"] != "" else "")
            + (" AND hotels.stars >= %s" if request.form["stars"] != "" else "")
            + (" AND hotels.num_rooms >= %s" if request.form["num-rooms"] != "" else "")
            + (" AND rooms.price <= %s" if request.form["price"] != "" else ""),
            tuple(request.form[key] for key in request.form if request.form[key] != ""),
        )
        rooms = cursor.fetchall()
        return render_template(
            "rooms.html",
            form=request.form,
            rooms=rooms,
            capacities=capacities,
            cities=cities,
            chains=chains,
            stars=stars,
            num_rooms=num_rooms,
            max_num_rooms=max_num_rooms,
        )
    elif request.method == "GET":
        cursor.execute(query)
        rooms = cursor.fetchall()
        return render_template(
            "rooms.html",
            form=None,
            rooms=rooms,
            capacities=capacities,
            cities=cities,
            chains=chains,
            stars=stars,
            num_rooms=num_rooms,
            max_num_rooms=max_num_rooms,
        )

    cursor.close()
