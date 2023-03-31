-- Create chains table
CREATE TABLE IF NOT EXISTS chains (
    chain_id SERIAL PRIMARY KEY,
    chain_name TEXT NOT NULL,
    num_hotels INTEGER DEFAULT 0
);


-- Create chain_offices table
CREATE TABLE IF NOT EXISTS chain_offices (
    id SERIAL PRIMARY KEY,
    street_number TEXT NOT NULL,
    street_name TEXT NOT NULL,
    apt_number TEXT,
    city TEXT NOT NULL,
    province_or_state TEXT,
    country TEXT NOT NULL,
    zip TEXT NOT NULL,
    chain_id INTEGER NOT NULL,
    FOREIGN KEY (chain_id) REFERENCES chains(chain_id) ON DELETE CASCADE
);


-- Create chain_phone_numbers table
CREATE TABLE IF NOT EXISTS chain_phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    description TEXT,
    chain_id INTEGER NOT NULL,
    FOREIGN KEY(chain_id) REFERENCES chains(chain_id) ON DELETE CASCADE
);


-- Create chain_email_addresses table
CREATE TABLE IF NOT EXISTS chain_email_addresses (
    id SERIAL PRIMARY KEY,
    email_address TEXT NOT NULL,
    description TEXT,
    chain_id INTEGER NOT NULL,
    FOREIGN KEY(chain_id) REFERENCES chains(chain_id) ON DELETE CASCADE
);


-- Create hotels table
CREATE TABLE IF NOT EXISTS hotels (
    hotel_id SERIAL PRIMARY KEY,
    street_number TEXT NOT NULL,
    street_name TEXT NOT NULL,
    city TEXT NOT NULL,
    province_or_state TEXT,
    country TEXT NOT NULL,
    zip TEXT NOT NULL,
    stars INTEGER,
    num_rooms INTEGER,
    chain_id INTEGER,
    CHECK (stars BETWEEN 1 AND 5),
    FOREIGN KEY (chain_id) REFERENCES chains(chain_id) ON DELETE CASCADE
);


-- Create hotel_phone_numbers table
CREATE TABLE IF NOT EXISTS hotel_phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    description TEXT,
    hotel_id INTEGER NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE
);


-- Create hotel_email_addresses table
CREATE TABLE IF NOT EXISTS hotel_email_addresses (
    id SERIAL PRIMARY KEY,
    email_address TEXT NOT NULL,
    description TEXT,
    hotel_id INTEGER NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE
);


-- Create view_types table
CREATE TABLE IF NOT EXISTS view_types (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL
);


-- Create rooms table
CREATE TABLE IF NOT EXISTS rooms (
    hotel_id INTEGER,
    room_number TEXT,
    capacity INTEGER NOT NULL,
    price NUMERIC(8, 2) NOT NULL,
    view_type INTEGER,
    extensible BOOLEAN,
    tv BOOLEAN,
    air_condition BOOLEAN,
    fridge BOOLEAN,
    CHECK (capacity > 0),
    CHECK (price > 0),
    PRIMARY KEY (hotel_id, room_number),
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE,
    FOREIGN KEY (view_type) REFERENCES view_types(id) ON DELETE SET NULL
);


-- Create room_damages table
CREATE TABLE IF NOT EXISTS room_damages (
    hotel_id INTEGER,
    room_number TEXT,
    description TEXT NOT NULL,
    PRIMARY KEY (hotel_id, room_number, description),
    FOREIGN KEY (hotel_id, room_number) REFERENCES rooms (hotel_id, room_number) ON DELETE CASCADE
);


-- Create positions table
CREATE TABLE IF NOT EXISTS positions (
    position_id SERIAL PRIMARY KEY,
    position_name TEXT NOT NULL
);


-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    employee_id SERIAL PRIMARY KEY,
    ssn VARCHAR(11) UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    middle_initial TEXT,
    last_name TEXT NOT NULL,
    street_number TEXT NOT NULL,
    street_name TEXT NOT NULL,
    apt_number TEXT,
    city TEXT NOT NULL,
    province_or_state TEXT,
    country TEXT NOT NULL,
    zip TEXT NOT NULL,
    position_id INTEGER,
    hotel_id INTEGER,
    FOREIGN KEY (position_id) REFERENCES positions(position_id) ON DELETE SET NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE SET NULL
);


-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    ssn VARCHAR(11) UNIQUE NOT NULL,
    registration_date DATE DEFAULT now(),
    first_name TEXT NOT NULL,
    middle_initial TEXT,
    last_name TEXT NOT NULL,
    street_number TEXT NOT NULL,
    street_name TEXT NOT NULL,
    apt_number TEXT,
    city TEXT NOT NULL,
    province_or_state TEXT,
    country TEXT NOT NULL,
    zip TEXT NOT NULL
);


-- Install uuid module
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- Create bookings table
CREATE TABLE IF NOT EXISTS bookings (
    booking_id UUID DEFAULT uuid_generate_v4(),
    customer_id INTEGER,
    hotel_id INTEGER,
    room_number TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    PRIMARY KEY (booking_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE,
    FOREIGN KEY (hotel_id, room_number) REFERENCES rooms (hotel_id, room_number) ON DELETE CASCADE
);


-- Create rentals table
CREATE TABLE IF NOT EXISTS rentals (
    rental_id UUID DEFAULT uuid_generate_v4(),
    customer_id INTEGER,
    booking_id UUID,
    hotel_id INTEGER,
    room_number TEXT,
    start_date DATE,
    end_date DATE,
    paid_amount NUMERIC(8, 2),
    PRIMARY KEY (rental_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings (booking_id) ON DELETE SET NULL,
    FOREIGN KEY (hotel_id, room_number) REFERENCES rooms (hotel_id, room_number) ON DELETE CASCADE
);


-- View for number of available rooms per area
CREATE OR REPLACE VIEW available_rooms_per_area AS
    SELECT hotels.country,
        hotels.province_or_state,
        hotels.city,
        COUNT(*) AS num_available_rooms
    FROM rooms
    JOIN hotels
    ON rooms.hotel_id = hotels.hotel_id
    JOIN chains
    ON hotels.chain_id = chains.chain_id
    WHERE (rooms.hotel_id, rooms.room_number) NOT IN (
        SELECT hotel_id, room_number from bookings
        WHERE current_date < start_date or current_date >= end_date
    )
    GROUP BY hotels.country, hotels.province_or_state, hotels.city
    ORDER BY hotels.country, hotels.province_or_state, hotels.city


-- View for capacity of all rooms of a specific hotel
CREATE OR REPLACE VIEW room_capacities AS
    SELECT chains.chain_name,
        hotels.hotel_id,
        hotels.country,
        hotels.province_or_state,
        hotels.city,
        rooms.room_number,
        rooms.capacity
    FROM hotels
    JOIN chains
    ON hotels.chain_id = chains.chain_id
    JOIN rooms
    ON hotels.hotel_id = rooms.hotel_id
    ORDER BY chains.chain_name, hotels.hotel_id, rooms.room_number


-- num_hotels trigger
CREATE OR REPLACE FUNCTION num_hotels() RETURNS TRIGGER AS $num_hotels$
    BEGIN
        UPDATE chains
        SET num_hotels = sub.num_hotels
        FROM (
            SELECT chain_id, COUNT(*) AS num_hotels
            FROM hotels
            GROUP BY chain_id
        ) AS sub
        WHERE chains.chain_id = sub.chain_id;
        RETURN NEW;
    END;
$num_hotels$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trig_num_hotels
    AFTER INSERT OR DELETE ON hotels
    FOR EACH ROW
    EXECUTE PROCEDURE num_hotels();


-- num_rooms trigger
CREATE OR REPLACE FUNCTION num_rooms() RETURNS TRIGGER AS $num_rooms$
    BEGIN
        UPDATE hotels
        SET num_rooms = sub.num_rooms
        FROM (
            SELECT hotel_id, COUNT(*) AS num_rooms
            FROM rooms
            GROUP BY hotel_id
        ) AS sub
        WHERE hotels.hotel_id = sub.hotel_id;
        RETURN NEW;
    END;
$num_rooms$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trig_num_rooms
    AFTER INSERT OR DELETE ON rooms
    FOR EACH ROW
    EXECUTE PROCEDURE num_rooms();


-- check_delete_manager trigger
CREATE OR REPLACE FUNCTION check_delete_manager() RETURNS TRIGGER as $check_delete_manager$
    DECLARE
        manager_position_id int;
        num_managers int;
    BEGIN
        SELECT position_id INTO manager_position_id
        FROM positions
        WHERE position_name = 'manager';

        IF OLD.position_id != manager_position_id THEN
            RETURN NULL;
        ELSE
            SELECT COUNT(*) INTO num_managers
            FROM employees
            WHERE employees.hotel_id = OLD.hotel_id
                AND employees.position_id = manager_position_id;

            IF num_managers > 1 THEN
                RETURN OLD;
            ELSE
                RAISE EXCEPTION 'Cannot delete last manager for hotel';
            END IF;
        END IF;
    END;
$check_delete_manager$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trig_check_delete_manager
    BEFORE DELETE ON employees
    FOR EACH ROW
    EXECUTE PROCEDURE check_delete_manager();
