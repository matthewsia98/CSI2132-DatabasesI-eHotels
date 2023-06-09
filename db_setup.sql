-- Drop all tables
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO msia;


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
    num_rooms INTEGER DEFAULT 0,
    chain_id INTEGER NOT NULL,
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
    ORDER BY hotels.country, hotels.province_or_state, hotels.city;


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
    ORDER BY chains.chain_name, hotels.hotel_id, rooms.room_number;


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


-- check_insert_booking trigger
CREATE OR REPLACE FUNCTION check_insert_booking() RETURNS TRIGGER as $check_insert_booking$
    DECLARE
        is_booking_valid boolean;
    BEGIN
        -- There are no bookings for the room
        SELECT (
            NEW.hotel_id NOT IN (SELECT bookings.hotel_id FROM bookings)
            AND NEW.room_number NOT IN (SELECT bookings.room_number FROM bookings)
        )
        OR
        -- New booking has start_date >= any booking end_date
        (
            NEW.start_date >= ALL(
                SELECT bookings.end_date
                FROM bookings
                WHERE bookings.hotel_id = NEW.hotel_id
                    AND bookings.room_number = NEW.room_number
            )
        )
        OR
        -- New booking has end_date <= any booking start_date
        (
            NEW.end_date <= ALL(
                SELECT bookings.start_date
                FROM bookings
                WHERE bookings.hotel_id = NEW.hotel_id
                    AND bookings.room_number = NEW.room_number
            )
        )
        INTO is_booking_valid;

        IF is_booking_valid THEN
            RETURN NEW;
        ELSE
            RAISE EXCEPTION 'Room is already booked';
        END IF;
    END;
$check_insert_booking$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trig_check_insert_booking
    BEFORE INSERT ON bookings
    FOR EACH ROW 
    EXECUTE PROCEDURE check_insert_booking();


-- get_available_rooms function
CREATE OR REPLACE FUNCTION get_available_rooms(start_date date, end_date date) RETURNS TABLE (
    chain_name text,
    stars int,
    num_rooms int,
    country text,
    province_or_state text,
    city text,
    address text,
    room_number text,
    capacity int,
    description text,
    price numeric,
    hotel_id int
) AS $get_available_rooms$
    BEGIN
        RETURN QUERY
        WITH all_rooms AS (
            SELECT chains.chain_name,
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
        )
        SELECT *
        FROM all_rooms
        WHERE (
                all_rooms.hotel_id NOT IN (SELECT bookings.hotel_id FROM bookings)
                AND all_rooms.room_number NOT IN (SELECT bookings.room_number FROM bookings)
            )
            OR
            -- New booking has start_date >= any booking end_date
            (
                start_date >= ALL(
                    SELECT bookings.end_date
                    FROM bookings
                    WHERE bookings.hotel_id = all_rooms.hotel_id
                        AND bookings.room_number = all_rooms.room_number
                )
            )
            OR 
            -- New booking has end_date <= any booking start_date
            (
                end_date <= ALL(
                    SELECT bookings.start_date
                    FROM bookings
                    WHERE bookings.hotel_id = all_rooms.hotel_id
                        AND bookings.room_number = all_rooms.room_number
                )
            )
        ORDER BY all_rooms.chain_name, all_rooms.hotel_id, all_rooms.room_number;
    END;
$get_available_rooms$ LANGUAGE plpgsql;


-- Create indexes
CREATE INDEX idx_bookings_start_date
ON bookings(start_date);

CREATE INDEX idx_bookings_end_date
ON bookings(end_date);

CREATE INDEX idx_room_price
ON rooms(price);


-- Insert into `chains` table
INSERT INTO chains(chain_name) VALUES
    ('Hotel Chain 1'),
    ('Hotel Chain 2'),
    ('Hotel Chain 3'),
    ('Hotel Chain 4'),
    ('Hotel Chain 5');

-- Insert into `chain_offices` table
INSERT INTO chain_offices (chain_id, street_number, street_name, apt_number, city, province_or_state, country, zip) VALUES
    (1, '1234', 'Angler Avenue', '2605', 'Ottawa', 'Ontario', 'Canada', 'K1R0C3'),
    (2, '2345', 'Barhaven Route', '813', 'Houston', 'Texas', 'United States', '77002'),
    (3, '3456', 'Christmas Lane', NULL, 'Toronto', 'Ontario', 'Canada', 'K1G5F3'),
    (4, '4567', 'Dunst Street', NULL, 'Miami', 'Florida', 'United States', '33102'),
    (5, '5678', 'Elgin Lane', '1205', 'Seattle', 'Washington', 'United States', '98102');

-- Insert into `chain_phone_numbers` table
INSERT INTO chain_phone_numbers (chain_id, phone_number) VALUES
    (1, '1234567890'),
    (2, '2345678901'),
    (3, '3456789012'),
    (4, '4567890123'),
    (5, '5678901234');

-- Insert into `chain_email_addresses` table
INSERT INTO chain_email_addresses (chain_id, email_address) VALUES
    (1, 'main_office@hotelchain1.com'),
    (2, 'main_office@hotelchain2.com'),
    (3, 'main_office@hotelchain3.com'),
    (4, 'main_office@hotelchain4.com'),
    (5, 'main_office@hotelchain5.com');

-- Insert into `hotels` table
INSERT INTO hotels (street_number, street_name, city, province_or_state, country, zip, stars, chain_id) VALUES
    ('1100', 'Brook Avenue',      'Ottawa',          'Ontario',          'Canada',        'K1R0C2', 1, 1),
    ('1200', 'Lawn Way',          'Toronto',         'Ontario',          'Canada',        'K1G5E9', 2, 1),
    ('1300', 'Feathers Route',    'Houston',         'Texas',            'United States', '77001',  3, 1),
    ('1400', 'Gem Way',           'San Antonio',     'Texas',            'United States', '78015',  4, 1),
    ('1500', 'Princess Lane',     'Vancouver',       'British Columbia', 'Canada',        'V5K0E2', 5, 1),
    ('1600', 'Winter Avenue',     'Surrey',          'British Columbia', 'Canada',        'V1M3B5', 1, 1),
    ('1700', 'Market Way',        'Los Angeles',     'California',       'United States', '90001',  1, 1),
    ('1800', 'Olive Street',      'San Diego',       'California',       'United States', '91911',  1, 1),
    ('2100', 'Polygon Passage',   'Montreal',        'Quebec',           'Canada',        'H1N3B5', 1, 2),
    ('2200', 'Nightingale Lane',  'Quebec City',     'Quebec',           'Canada',        'G2Z9Z9', 2, 2),
    ('2300', 'Fox Street',        'Jacksonville',    'Florida',          'United States', '32034',  3, 2),
    ('2400', 'Middle Avenue',     'Miami',           'Florida',          'United States', '33101',  4, 2),
    ('2500', 'Maple Route',       'Calgary',         'Alberta',          'Canada',        'T1V2F6', 5, 2),
    ('2600', 'Knight Lane',       'Edmonton',        'Alberta',          'Canada',        'T6G5A1', 2, 2),
    ('2700', 'Pine Lane',         'Oklahoma City',   'Oklahoma',         'United States', '73008',  2, 2),
    ('2800', 'Station Avenue',    'Tulsa',           'Oklahoma',         'United States', '74008',  2, 2),
    ('3100', 'Marine Way',        'Mississauga',     'Ontario',          'Canada',        'L4T0A1', 1, 3),
    ('3200', 'Museum Avenue',     'Hamilton',        'Ontario',          'Canada',        'L0P1B0', 2, 3),
    ('3300', 'Ironwood Lane',     'Philadelphia',    'Pennsylvania',     'United States', '19019',  3, 3),
    ('3400', 'Globe Route',       'Pittsburgh',      'Pennsylvania',     'United States', '15106',  4, 3),
    ('3500', 'Rowan Lane',        'Richmond',        'British Columbia', 'Canada',        'V6V0A2', 5, 3),
    ('3600', 'Monument Passage',  'Burnaby',         'British Columbia', 'Canada',        'V3J0A5', 3, 3),
    ('3700', 'Meadow Route',      'Phoenix',         'Arizona',          'United States', '85001',  3, 3),
    ('3800', 'Paradise Street',   'Tuscon',          'Arizona',          'United States', '85641',  3, 3),
    ('4100', 'Medieval Avenue',   'San Jose',        'California',       'United States', '94088',  1, 4),
    ('4200', 'Lavender Street',   'San Francisco',   'California',       'United States', '94016',  2, 4),
    ('4300', 'Senna Street',      'Austin',          'Texas',            'United States', '73301',  3, 4),
    ('4400', 'Globe Boulevard',   'El Paso',         'Texas',            'United States', '79835',  4, 4),
    ('4500', 'Autumn Boulevard',  'Tampa',           'Florida',          'United States', '33592',  5, 4),
    ('4600', 'Hill Way',          'Fort Lauderdale', 'Florida',          'United States', '33301',  4, 4),
    ('4700', 'Lower Lane',        'Columbus',        'Ohio',             'United States', '43004',  4, 4),
    ('4800', 'Bay View Way',      'Cleveland',       'Ohio',             'United States', '44101',  4, 4),
    ('5100', 'Blossom Boulevard', 'New York City',   'New York',         'United States', '10001',  1, 5),
    ('5200', 'Petal Avenue',      'Brookhaven',      'New York',         'United States', '30319',  2, 5),
    ('5300', 'Hazelnut Avenue',   'Fresno',          'California',       'United States', '93650',  3, 5),
    ('5400', 'Greenfield Street', 'Sacramento',      'California',       'United States', '94203',  4, 5),
    ('5500', 'Chapel Way',        'Charlotte',       'North Carolina',   'United States', '28105',  5, 5),
    ('5600', 'Amber Row',         'Raleigh',         'North Carolina',   'United States', '27513',  5, 5),
    ('5700', 'Highland Avenue',   'Seattle',         'Washington',       'United States', '98101',  5, 5),
    ('5800', 'Bloomfield Lane',   'Spokane',         'Washington',       'United States', '99201',  5, 5);

-- Insert into `hotel_phone_numbers` table
INSERT INTO hotel_phone_numbers (hoteL_id, phone_number) VALUES
    (1, '1111111111'),
    (2, '2222222222'),
    (3, '3333333333'),
    (4, '4444444444'),
    (5, '5555555555'),
    (6, '6666666666'),
    (7, '7777777777'),
    (8, '8888888888'),
    (9, '9999999999'),
    (10, '1010101010'),
    (11, '1111111111'),
    (12, '1212121212'),
    (13, '1313131313'),
    (14, '1414141414'),
    (15, '1515151515'),
    (16, '1616161616'),
    (17, '1717171717'),
    (18, '1818181818'),
    (19, '1919191919'),
    (20, '2020202020'),
    (21, '2121212121'),
    (22, '2222222222'),
    (23, '2323232323'),
    (24, '2424242424'),
    (25, '2525252525'),
    (26, '2626262626'),
    (27, '2727272727'),
    (28, '2828282828'),
    (29, '2929292929'),
    (30, '3030303030'),
    (31, '3131313131'),
    (32, '3232323232'),
    (33, '3333333333'),
    (34, '3434343434'),
    (35, '3535353535'),
    (36, '3636363636'),
    (37, '3737373737'),
    (38, '3838383838'),
    (39, '3939393939'),
    (40, '4040404040');

-- Insert into `hotel_email_addresses` table
INSERT INTO hotel_email_addresses (hotel_id, email_address) VALUES
    (1, 'email@hotel1.com'),
    (2, 'email@hotel2.com'),
    (3, 'email@hotel3.com'),
    (4, 'email@hotel4.com'),
    (5, 'email@hotel5.com'),
    (6, 'email@hotel6.com'),
    (7, 'email@hotel7.com'),
    (8, 'email@hotel8.com'),
    (9, 'email@hotel9.com'),
    (10, 'email@hotel10.com'),
    (11, 'email@hotel11.com'),
    (12, 'email@hotel12.com'),
    (13, 'email@hotel13.com'),
    (14, 'email@hotel14.com'),
    (15, 'email@hotel15.com'),
    (16, 'email@hotel16.com'),
    (17, 'email@hotel17.com'),
    (18, 'email@hotel18.com'),
    (19, 'email@hotel19.com'),
    (20, 'email@hotel20.com'),
    (21, 'email@hotel21.com'),
    (22, 'email@hotel22.com'),
    (23, 'email@hotel23.com'),
    (24, 'email@hotel24.com'),
    (25, 'email@hotel25.com'),
    (26, 'email@hotel26.com'),
    (27, 'email@hotel27.com'),
    (28, 'email@hotel28.com'),
    (29, 'email@hotel29.com'),
    (30, 'email@hotel30.com'),
    (31, 'email@hotel31.com'),
    (32, 'email@hotel32.com'),
    (33, 'email@hotel33.com'),
    (34, 'email@hotel34.com'),
    (35, 'email@hotel35.com'),
    (36, 'email@hotel36.com'),
    (37, 'email@hotel37.com'),
    (38, 'email@hotel38.com'),
    (39, 'email@hotel39.com'),
    (40, 'email@hotel40.com');

-- Insert into `view_types` table
INSERT INTO view_types (description) VALUES
    ('Mountain'),
    ('Sea');

-- Insert into `rooms` table
INSERT INTO rooms (hotel_id, room_number, capacity, price, view_type, extensible, tv, air_condition, fridge) VALUES
    (1, '101', 1, 123.45, 1, false, true, true, true),
    (1, '102', 1, 234.56, 2, true, true, true, true),
    (1, '201', 2, 345.67, 1, false, true, true, true),
    (1, '202', 2, 456.78, 2, true, true, true, true),
    (1, '301', 3, 567.89, 1, false, true, true, true),
    (1, '302', 3, 678.90, 2, true, true, true, true),
    (1, '401', 4, 789.01, 1, false, true, true, true),
    (1, '402', 4, 890.12, 2, true, true, true, true),
    (1, '501', 5, 901.23, 1, false, true, true, true),
    (1, '502', 5, 1011.12, 2, true, true, true, true),
    (1, '601', 6, 1112.13, 1, false, true, true, true),
    (1, '602', 6, 1213.14, 2, true, true, true, true),
    (2, '101', 1, 123.45, 1, false, true, true, true),
    (2, '102', 1, 234.56, 2, true, true, true, true),
    (2, '201', 2, 345.67, 1, false, true, true, true),
    (2, '202', 2, 456.78, 2, true, true, true, true),
    (2, '301', 3, 567.89, 1, false, true, true, true),
    (2, '302', 3, 678.90, 2, true, true, true, true),
    (2, '401', 4, 789.01, 1, false, true, true, true),
    (2, '402', 4, 890.12, 2, true, true, true, true),
    (2, '501', 5, 901.23, 1, false, true, true, true),
    (2, '502', 5, 1011.12, 2, true, true, true, true),
    (2, '601', 6, 1112.13, 1, false, true, true, true),
    (2, '602', 6, 1213.14, 2, true, true, true, true),
    (3, '101', 1, 123.45, 1, false, true, true, true),
    (3, '102', 1, 234.56, 2, true, true, true, true),
    (3, '201', 2, 345.67, 1, false, true, true, true),
    (3, '202', 2, 456.78, 2, true, true, true, true),
    (3, '301', 3, 567.89, 1, false, true, true, true),
    (3, '302', 3, 678.90, 2, true, true, true, true),
    (3, '401', 4, 789.01, 1, false, true, true, true),
    (3, '402', 4, 890.12, 2, true, true, true, true),
    (3, '501', 5, 901.23, 1, false, true, true, true),
    (3, '502', 5, 1011.12, 2, true, true, true, true),
    (3, '601', 6, 1112.13, 1, false, true, true, true),
    (3, '602', 6, 1213.14, 2, true, true, true, true),
    (4, '101', 1, 123.45, 1, false, true, true, true),
    (4, '102', 1, 234.56, 2, true, true, true, true),
    (4, '201', 2, 345.67, 1, false, true, true, true),
    (4, '202', 2, 456.78, 2, true, true, true, true),
    (4, '301', 3, 567.89, 1, false, true, true, true),
    (4, '302', 3, 678.90, 2, true, true, true, true),
    (4, '401', 4, 789.01, 1, false, true, true, true),
    (4, '402', 4, 890.12, 2, true, true, true, true),
    (4, '501', 5, 901.23, 1, false, true, true, true),
    (4, '502', 5, 1011.12, 2, true, true, true, true),
    (4, '601', 6, 1112.13, 1, false, true, true, true),
    (4, '602', 6, 1213.14, 2, true, true, true, true),
    (5, '101', 1, 123.45, 1, false, true, true, true),
    (5, '102', 1, 234.56, 2, true, true, true, true),
    (5, '201', 2, 345.67, 1, false, true, true, true),
    (5, '202', 2, 456.78, 2, true, true, true, true),
    (5, '301', 3, 567.89, 1, false, true, true, true),
    (5, '302', 3, 678.90, 2, true, true, true, true),
    (5, '401', 4, 789.01, 1, false, true, true, true),
    (5, '402', 4, 890.12, 2, true, true, true, true),
    (5, '501', 5, 901.23, 1, false, true, true, true),
    (5, '502', 5, 1011.12, 2, true, true, true, true),
    (5, '601', 6, 1112.13, 1, false, true, true, true),
    (5, '602', 6, 1213.14, 2, true, true, true, true),
    (6, '101', 1, 123.45, 1, false, true, true, true),
    (6, '102', 1, 234.56, 2, true, true, true, true),
    (6, '201', 2, 345.67, 1, false, true, true, true),
    (6, '202', 2, 456.78, 2, true, true, true, true),
    (6, '301', 3, 567.89, 1, false, true, true, true),
    (6, '302', 3, 678.90, 2, true, true, true, true),
    (6, '401', 4, 789.01, 1, false, true, true, true),
    (6, '402', 4, 890.12, 2, true, true, true, true),
    (6, '501', 5, 901.23, 1, false, true, true, true),
    (6, '502', 5, 1011.12, 2, true, true, true, true),
    (6, '601', 6, 1112.13, 1, false, true, true, true),
    (6, '602', 6, 1213.14, 2, true, true, true, true),
    (7, '101', 1, 123.45, 1, false, true, true, true),
    (7, '102', 1, 234.56, 2, true, true, true, true),
    (7, '201', 2, 345.67, 1, false, true, true, true),
    (7, '202', 2, 456.78, 2, true, true, true, true),
    (7, '301', 3, 567.89, 1, false, true, true, true),
    (7, '302', 3, 678.90, 2, true, true, true, true),
    (7, '401', 4, 789.01, 1, false, true, true, true),
    (7, '402', 4, 890.12, 2, true, true, true, true),
    (7, '501', 5, 901.23, 1, false, true, true, true),
    (7, '502', 5, 1011.12, 2, true, true, true, true),
    (7, '601', 6, 1112.13, 1, false, true, true, true),
    (7, '602', 6, 1213.14, 2, true, true, true, true),
    (8, '101', 1, 123.45, 1, false, true, true, true),
    (8, '102', 1, 234.56, 2, true, true, true, true),
    (8, '201', 2, 345.67, 1, false, true, true, true),
    (8, '202', 2, 456.78, 2, true, true, true, true),
    (8, '301', 3, 567.89, 1, false, true, true, true),
    (8, '302', 3, 678.90, 2, true, true, true, true),
    (8, '401', 4, 789.01, 1, false, true, true, true),
    (8, '402', 4, 890.12, 2, true, true, true, true),
    (8, '501', 5, 901.23, 1, false, true, true, true),
    (8, '502', 5, 1011.12, 2, true, true, true, true),
    (8, '601', 6, 1112.13, 1, false, true, true, true),
    (8, '602', 6, 1213.14, 2, true, true, true, true),
    (9, '101', 1, 123.45, 1, false, true, true, true),
    (9, '102', 1, 234.56, 2, true, true, true, true),
    (9, '201', 2, 345.67, 1, false, true, true, true),
    (9, '202', 2, 456.78, 2, true, true, true, true),
    (9, '301', 3, 567.89, 1, false, true, true, true),
    (9, '302', 3, 678.90, 2, true, true, true, true),
    (9, '401', 4, 789.01, 1, false, true, true, true),
    (9, '402', 4, 890.12, 2, true, true, true, true),
    (9, '501', 5, 901.23, 1, false, true, true, true),
    (9, '502', 5, 1011.12, 2, true, true, true, true),
    (9, '601', 6, 1112.13, 1, false, true, true, true),
    (9, '602', 6, 1213.14, 2, true, true, true, true),
    (10, '101', 1, 123.45, 1, false, true, true, true),
    (10, '102', 1, 234.56, 2, true, true, true, true),
    (10, '201', 2, 345.67, 1, false, true, true, true),
    (10, '202', 2, 456.78, 2, true, true, true, true),
    (10, '301', 3, 567.89, 1, false, true, true, true),
    (10, '302', 3, 678.90, 2, true, true, true, true),
    (10, '401', 4, 789.01, 1, false, true, true, true),
    (10, '402', 4, 890.12, 2, true, true, true, true),
    (10, '501', 5, 901.23, 1, false, true, true, true),
    (10, '502', 5, 1011.12, 2, true, true, true, true),
    (10, '601', 6, 1112.13, 1, false, true, true, true),
    (10, '602', 6, 1213.14, 2, true, true, true, true),
    (11, '101', 1, 123.45, 1, false, true, true, true),
    (11, '102', 1, 234.56, 2, true, true, true, true),
    (11, '201', 2, 345.67, 1, false, true, true, true),
    (11, '202', 2, 456.78, 2, true, true, true, true),
    (11, '301', 3, 567.89, 1, false, true, true, true),
    (11, '302', 3, 678.90, 2, true, true, true, true),
    (11, '401', 4, 789.01, 1, false, true, true, true),
    (11, '402', 4, 890.12, 2, true, true, true, true),
    (11, '501', 5, 901.23, 1, false, true, true, true),
    (11, '502', 5, 1011.12, 2, true, true, true, true),
    (11, '601', 6, 1112.13, 1, false, true, true, true),
    (11, '602', 6, 1213.14, 2, true, true, true, true),
    (12, '101', 1, 123.45, 1, false, true, true, true),
    (12, '102', 1, 234.56, 2, true, true, true, true),
    (12, '201', 2, 345.67, 1, false, true, true, true),
    (12, '202', 2, 456.78, 2, true, true, true, true),
    (12, '301', 3, 567.89, 1, false, true, true, true),
    (12, '302', 3, 678.90, 2, true, true, true, true),
    (12, '401', 4, 789.01, 1, false, true, true, true),
    (12, '402', 4, 890.12, 2, true, true, true, true),
    (12, '501', 5, 901.23, 1, false, true, true, true),
    (12, '502', 5, 1011.12, 2, true, true, true, true),
    (12, '601', 6, 1112.13, 1, false, true, true, true),
    (12, '602', 6, 1213.14, 2, true, true, true, true),
    (13, '101', 1, 123.45, 1, false, true, true, true),
    (13, '102', 1, 234.56, 2, true, true, true, true),
    (13, '201', 2, 345.67, 1, false, true, true, true),
    (13, '202', 2, 456.78, 2, true, true, true, true),
    (13, '301', 3, 567.89, 1, false, true, true, true),
    (13, '302', 3, 678.90, 2, true, true, true, true),
    (13, '401', 4, 789.01, 1, false, true, true, true),
    (13, '402', 4, 890.12, 2, true, true, true, true),
    (13, '501', 5, 901.23, 1, false, true, true, true),
    (13, '502', 5, 1011.12, 2, true, true, true, true),
    (13, '601', 6, 1112.13, 1, false, true, true, true),
    (13, '602', 6, 1213.14, 2, true, true, true, true),
    (14, '101', 1, 123.45, 1, false, true, true, true),
    (14, '102', 1, 234.56, 2, true, true, true, true),
    (14, '201', 2, 345.67, 1, false, true, true, true),
    (14, '202', 2, 456.78, 2, true, true, true, true),
    (14, '301', 3, 567.89, 1, false, true, true, true),
    (14, '302', 3, 678.90, 2, true, true, true, true),
    (14, '401', 4, 789.01, 1, false, true, true, true),
    (14, '402', 4, 890.12, 2, true, true, true, true),
    (14, '501', 5, 901.23, 1, false, true, true, true),
    (14, '502', 5, 1011.12, 2, true, true, true, true),
    (14, '601', 6, 1112.13, 1, false, true, true, true),
    (14, '602', 6, 1213.14, 2, true, true, true, true),
    (15, '101', 1, 123.45, 1, false, true, true, true),
    (15, '102', 1, 234.56, 2, true, true, true, true),
    (15, '201', 2, 345.67, 1, false, true, true, true),
    (15, '202', 2, 456.78, 2, true, true, true, true),
    (15, '301', 3, 567.89, 1, false, true, true, true),
    (15, '302', 3, 678.90, 2, true, true, true, true),
    (15, '401', 4, 789.01, 1, false, true, true, true),
    (15, '402', 4, 890.12, 2, true, true, true, true),
    (15, '501', 5, 901.23, 1, false, true, true, true),
    (15, '502', 5, 1011.12, 2, true, true, true, true),
    (15, '601', 6, 1112.13, 1, false, true, true, true),
    (15, '602', 6, 1213.14, 2, true, true, true, true),
    (16, '101', 1, 123.45, 1, false, true, true, true),
    (16, '102', 1, 234.56, 2, true, true, true, true),
    (16, '201', 2, 345.67, 1, false, true, true, true),
    (16, '202', 2, 456.78, 2, true, true, true, true),
    (16, '301', 3, 567.89, 1, false, true, true, true),
    (16, '302', 3, 678.90, 2, true, true, true, true),
    (16, '401', 4, 789.01, 1, false, true, true, true),
    (16, '402', 4, 890.12, 2, true, true, true, true),
    (16, '501', 5, 901.23, 1, false, true, true, true),
    (16, '502', 5, 1011.12, 2, true, true, true, true),
    (16, '601', 6, 1112.13, 1, false, true, true, true),
    (16, '602', 6, 1213.14, 2, true, true, true, true),
    (17, '101', 1, 123.45, 1, false, true, true, true),
    (17, '102', 1, 234.56, 2, true, true, true, true),
    (17, '201', 2, 345.67, 1, false, true, true, true),
    (17, '202', 2, 456.78, 2, true, true, true, true),
    (17, '301', 3, 567.89, 1, false, true, true, true),
    (17, '302', 3, 678.90, 2, true, true, true, true),
    (17, '401', 4, 789.01, 1, false, true, true, true),
    (17, '402', 4, 890.12, 2, true, true, true, true),
    (17, '501', 5, 901.23, 1, false, true, true, true),
    (17, '502', 5, 1011.12, 2, true, true, true, true),
    (17, '601', 6, 1112.13, 1, false, true, true, true),
    (17, '602', 6, 1213.14, 2, true, true, true, true),
    (18, '101', 1, 123.45, 1, false, true, true, true),
    (18, '102', 1, 234.56, 2, true, true, true, true),
    (18, '201', 2, 345.67, 1, false, true, true, true),
    (18, '202', 2, 456.78, 2, true, true, true, true),
    (18, '301', 3, 567.89, 1, false, true, true, true),
    (18, '302', 3, 678.90, 2, true, true, true, true),
    (18, '401', 4, 789.01, 1, false, true, true, true),
    (18, '402', 4, 890.12, 2, true, true, true, true),
    (18, '501', 5, 901.23, 1, false, true, true, true),
    (18, '502', 5, 1011.12, 2, true, true, true, true),
    (18, '601', 6, 1112.13, 1, false, true, true, true),
    (18, '602', 6, 1213.14, 2, true, true, true, true),
    (19, '101', 1, 123.45, 1, false, true, true, true),
    (19, '102', 1, 234.56, 2, true, true, true, true),
    (19, '201', 2, 345.67, 1, false, true, true, true),
    (19, '202', 2, 456.78, 2, true, true, true, true),
    (19, '301', 3, 567.89, 1, false, true, true, true),
    (19, '302', 3, 678.90, 2, true, true, true, true),
    (19, '401', 4, 789.01, 1, false, true, true, true),
    (19, '402', 4, 890.12, 2, true, true, true, true),
    (19, '501', 5, 901.23, 1, false, true, true, true),
    (19, '502', 5, 1011.12, 2, true, true, true, true),
    (19, '601', 6, 1112.13, 1, false, true, true, true),
    (19, '602', 6, 1213.14, 2, true, true, true, true),
    (20, '101', 1, 123.45, 1, false, true, true, true),
    (20, '102', 1, 234.56, 2, true, true, true, true),
    (20, '201', 2, 345.67, 1, false, true, true, true),
    (20, '202', 2, 456.78, 2, true, true, true, true),
    (20, '301', 3, 567.89, 1, false, true, true, true),
    (20, '302', 3, 678.90, 2, true, true, true, true),
    (20, '401', 4, 789.01, 1, false, true, true, true),
    (20, '402', 4, 890.12, 2, true, true, true, true),
    (20, '501', 5, 901.23, 1, false, true, true, true),
    (20, '502', 5, 1011.12, 2, true, true, true, true),
    (20, '601', 6, 1112.13, 1, false, true, true, true),
    (20, '602', 6, 1213.14, 2, true, true, true, true),
    (21, '101', 1, 123.45, 1, false, true, true, true),
    (21, '102', 1, 234.56, 2, true, true, true, true),
    (21, '201', 2, 345.67, 1, false, true, true, true),
    (21, '202', 2, 456.78, 2, true, true, true, true),
    (21, '301', 3, 567.89, 1, false, true, true, true),
    (21, '302', 3, 678.90, 2, true, true, true, true),
    (21, '401', 4, 789.01, 1, false, true, true, true),
    (21, '402', 4, 890.12, 2, true, true, true, true),
    (21, '501', 5, 901.23, 1, false, true, true, true),
    (21, '502', 5, 1011.12, 2, true, true, true, true),
    (21, '601', 6, 1112.13, 1, false, true, true, true),
    (21, '602', 6, 1213.14, 2, true, true, true, true),
    (22, '101', 1, 123.45, 1, false, true, true, true),
    (22, '102', 1, 234.56, 2, true, true, true, true),
    (22, '201', 2, 345.67, 1, false, true, true, true),
    (22, '202', 2, 456.78, 2, true, true, true, true),
    (22, '301', 3, 567.89, 1, false, true, true, true),
    (22, '302', 3, 678.90, 2, true, true, true, true),
    (22, '401', 4, 789.01, 1, false, true, true, true),
    (22, '402', 4, 890.12, 2, true, true, true, true),
    (22, '501', 5, 901.23, 1, false, true, true, true),
    (22, '502', 5, 1011.12, 2, true, true, true, true),
    (22, '601', 6, 1112.13, 1, false, true, true, true),
    (22, '602', 6, 1213.14, 2, true, true, true, true),
    (23, '101', 1, 123.45, 1, false, true, true, true),
    (23, '102', 1, 234.56, 2, true, true, true, true),
    (23, '201', 2, 345.67, 1, false, true, true, true),
    (23, '202', 2, 456.78, 2, true, true, true, true),
    (23, '301', 3, 567.89, 1, false, true, true, true),
    (23, '302', 3, 678.90, 2, true, true, true, true),
    (23, '401', 4, 789.01, 1, false, true, true, true),
    (23, '402', 4, 890.12, 2, true, true, true, true),
    (23, '501', 5, 901.23, 1, false, true, true, true),
    (23, '502', 5, 1011.12, 2, true, true, true, true),
    (23, '601', 6, 1112.13, 1, false, true, true, true),
    (23, '602', 6, 1213.14, 2, true, true, true, true),
    (24, '101', 1, 123.45, 1, false, true, true, true),
    (24, '102', 1, 234.56, 2, true, true, true, true),
    (24, '201', 2, 345.67, 1, false, true, true, true),
    (24, '202', 2, 456.78, 2, true, true, true, true),
    (24, '301', 3, 567.89, 1, false, true, true, true),
    (24, '302', 3, 678.90, 2, true, true, true, true),
    (24, '401', 4, 789.01, 1, false, true, true, true),
    (24, '402', 4, 890.12, 2, true, true, true, true),
    (24, '501', 5, 901.23, 1, false, true, true, true),
    (24, '502', 5, 1011.12, 2, true, true, true, true),
    (24, '601', 6, 1112.13, 1, false, true, true, true),
    (24, '602', 6, 1213.14, 2, true, true, true, true),
    (25, '101', 1, 123.45, 1, false, true, true, true),
    (25, '102', 1, 234.56, 2, true, true, true, true),
    (25, '201', 2, 345.67, 1, false, true, true, true),
    (25, '202', 2, 456.78, 2, true, true, true, true),
    (25, '301', 3, 567.89, 1, false, true, true, true),
    (25, '302', 3, 678.90, 2, true, true, true, true),
    (25, '401', 4, 789.01, 1, false, true, true, true),
    (25, '402', 4, 890.12, 2, true, true, true, true),
    (25, '501', 5, 901.23, 1, false, true, true, true),
    (25, '502', 5, 1011.12, 2, true, true, true, true),
    (25, '601', 6, 1112.13, 1, false, true, true, true),
    (25, '602', 6, 1213.14, 2, true, true, true, true),
    (26, '101', 1, 123.45, 1, false, true, true, true),
    (26, '102', 1, 234.56, 2, true, true, true, true),
    (26, '201', 2, 345.67, 1, false, true, true, true),
    (26, '202', 2, 456.78, 2, true, true, true, true),
    (26, '301', 3, 567.89, 1, false, true, true, true),
    (26, '302', 3, 678.90, 2, true, true, true, true),
    (26, '401', 4, 789.01, 1, false, true, true, true),
    (26, '402', 4, 890.12, 2, true, true, true, true),
    (26, '501', 5, 901.23, 1, false, true, true, true),
    (26, '502', 5, 1011.12, 2, true, true, true, true),
    (26, '601', 6, 1112.13, 1, false, true, true, true),
    (26, '602', 6, 1213.14, 2, true, true, true, true),
    (27, '101', 1, 123.45, 1, false, true, true, true),
    (27, '102', 1, 234.56, 2, true, true, true, true),
    (27, '201', 2, 345.67, 1, false, true, true, true),
    (27, '202', 2, 456.78, 2, true, true, true, true),
    (27, '301', 3, 567.89, 1, false, true, true, true),
    (27, '302', 3, 678.90, 2, true, true, true, true),
    (27, '401', 4, 789.01, 1, false, true, true, true),
    (27, '402', 4, 890.12, 2, true, true, true, true),
    (27, '501', 5, 901.23, 1, false, true, true, true),
    (27, '502', 5, 1011.12, 2, true, true, true, true),
    (27, '601', 6, 1112.13, 1, false, true, true, true),
    (27, '602', 6, 1213.14, 2, true, true, true, true),
    (28, '101', 1, 123.45, 1, false, true, true, true),
    (28, '102', 1, 234.56, 2, true, true, true, true),
    (28, '201', 2, 345.67, 1, false, true, true, true),
    (28, '202', 2, 456.78, 2, true, true, true, true),
    (28, '301', 3, 567.89, 1, false, true, true, true),
    (28, '302', 3, 678.90, 2, true, true, true, true),
    (28, '401', 4, 789.01, 1, false, true, true, true),
    (28, '402', 4, 890.12, 2, true, true, true, true),
    (28, '501', 5, 901.23, 1, false, true, true, true),
    (28, '502', 5, 1011.12, 2, true, true, true, true),
    (28, '601', 6, 1112.13, 1, false, true, true, true),
    (28, '602', 6, 1213.14, 2, true, true, true, true),
    (29, '101', 1, 123.45, 1, false, true, true, true),
    (29, '102', 1, 234.56, 2, true, true, true, true),
    (29, '201', 2, 345.67, 1, false, true, true, true),
    (29, '202', 2, 456.78, 2, true, true, true, true),
    (29, '301', 3, 567.89, 1, false, true, true, true),
    (29, '302', 3, 678.90, 2, true, true, true, true),
    (29, '401', 4, 789.01, 1, false, true, true, true),
    (29, '402', 4, 890.12, 2, true, true, true, true),
    (29, '501', 5, 901.23, 1, false, true, true, true),
    (29, '502', 5, 1011.12, 2, true, true, true, true),
    (29, '601', 6, 1112.13, 1, false, true, true, true),
    (29, '602', 6, 1213.14, 2, true, true, true, true),
    (30, '101', 1, 123.45, 1, false, true, true, true),
    (30, '102', 1, 234.56, 2, true, true, true, true),
    (30, '201', 2, 345.67, 1, false, true, true, true),
    (30, '202', 2, 456.78, 2, true, true, true, true),
    (30, '301', 3, 567.89, 1, false, true, true, true),
    (30, '302', 3, 678.90, 2, true, true, true, true),
    (30, '401', 4, 789.01, 1, false, true, true, true),
    (30, '402', 4, 890.12, 2, true, true, true, true),
    (30, '501', 5, 901.23, 1, false, true, true, true),
    (30, '502', 5, 1011.12, 2, true, true, true, true),
    (30, '601', 6, 1112.13, 1, false, true, true, true),
    (30, '602', 6, 1213.14, 2, true, true, true, true),
    (31, '101', 1, 123.45, 1, false, true, true, true),
    (31, '102', 1, 234.56, 2, true, true, true, true),
    (31, '201', 2, 345.67, 1, false, true, true, true),
    (31, '202', 2, 456.78, 2, true, true, true, true),
    (31, '301', 3, 567.89, 1, false, true, true, true),
    (31, '302', 3, 678.90, 2, true, true, true, true),
    (31, '401', 4, 789.01, 1, false, true, true, true),
    (31, '402', 4, 890.12, 2, true, true, true, true),
    (31, '501', 5, 901.23, 1, false, true, true, true),
    (31, '502', 5, 1011.12, 2, true, true, true, true),
    (31, '601', 6, 1112.13, 1, false, true, true, true),
    (31, '602', 6, 1213.14, 2, true, true, true, true),
    (32, '101', 1, 123.45, 1, false, true, true, true),
    (32, '102', 1, 234.56, 2, true, true, true, true),
    (32, '201', 2, 345.67, 1, false, true, true, true),
    (32, '202', 2, 456.78, 2, true, true, true, true),
    (32, '301', 3, 567.89, 1, false, true, true, true),
    (32, '302', 3, 678.90, 2, true, true, true, true),
    (32, '401', 4, 789.01, 1, false, true, true, true),
    (32, '402', 4, 890.12, 2, true, true, true, true),
    (32, '501', 5, 901.23, 1, false, true, true, true),
    (32, '502', 5, 1011.12, 2, true, true, true, true),
    (32, '601', 6, 1112.13, 1, false, true, true, true),
    (32, '602', 6, 1213.14, 2, true, true, true, true),
    (33, '101', 1, 123.45, 1, false, true, true, true),
    (33, '102', 1, 234.56, 2, true, true, true, true),
    (33, '201', 2, 345.67, 1, false, true, true, true),
    (33, '202', 2, 456.78, 2, true, true, true, true),
    (33, '301', 3, 567.89, 1, false, true, true, true),
    (33, '302', 3, 678.90, 2, true, true, true, true),
    (33, '401', 4, 789.01, 1, false, true, true, true),
    (33, '402', 4, 890.12, 2, true, true, true, true),
    (33, '501', 5, 901.23, 1, false, true, true, true),
    (33, '502', 5, 1011.12, 2, true, true, true, true),
    (33, '601', 6, 1112.13, 1, false, true, true, true),
    (33, '602', 6, 1213.14, 2, true, true, true, true),
    (34, '101', 1, 123.45, 1, false, true, true, true),
    (34, '102', 1, 234.56, 2, true, true, true, true),
    (34, '201', 2, 345.67, 1, false, true, true, true),
    (34, '202', 2, 456.78, 2, true, true, true, true),
    (34, '301', 3, 567.89, 1, false, true, true, true),
    (34, '302', 3, 678.90, 2, true, true, true, true),
    (34, '401', 4, 789.01, 1, false, true, true, true),
    (34, '402', 4, 890.12, 2, true, true, true, true),
    (34, '501', 5, 901.23, 1, false, true, true, true),
    (34, '502', 5, 1011.12, 2, true, true, true, true),
    (34, '601', 6, 1112.13, 1, false, true, true, true),
    (34, '602', 6, 1213.14, 2, true, true, true, true),
    (35, '101', 1, 123.45, 1, false, true, true, true),
    (35, '102', 1, 234.56, 2, true, true, true, true),
    (35, '201', 2, 345.67, 1, false, true, true, true),
    (35, '202', 2, 456.78, 2, true, true, true, true),
    (35, '301', 3, 567.89, 1, false, true, true, true),
    (35, '302', 3, 678.90, 2, true, true, true, true),
    (35, '401', 4, 789.01, 1, false, true, true, true),
    (35, '402', 4, 890.12, 2, true, true, true, true),
    (35, '501', 5, 901.23, 1, false, true, true, true),
    (35, '502', 5, 1011.12, 2, true, true, true, true),
    (35, '601', 6, 1112.13, 1, false, true, true, true),
    (35, '602', 6, 1213.14, 2, true, true, true, true),
    (36, '101', 1, 123.45, 1, false, true, true, true),
    (36, '102', 1, 234.56, 2, true, true, true, true),
    (36, '201', 2, 345.67, 1, false, true, true, true),
    (36, '202', 2, 456.78, 2, true, true, true, true),
    (36, '301', 3, 567.89, 1, false, true, true, true),
    (36, '302', 3, 678.90, 2, true, true, true, true),
    (36, '401', 4, 789.01, 1, false, true, true, true),
    (36, '402', 4, 890.12, 2, true, true, true, true),
    (36, '501', 5, 901.23, 1, false, true, true, true),
    (36, '502', 5, 1011.12, 2, true, true, true, true),
    (36, '601', 6, 1112.13, 1, false, true, true, true),
    (36, '602', 6, 1213.14, 2, true, true, true, true),
    (37, '101', 1, 123.45, 1, false, true, true, true),
    (37, '102', 1, 234.56, 2, true, true, true, true),
    (37, '201', 2, 345.67, 1, false, true, true, true),
    (37, '202', 2, 456.78, 2, true, true, true, true),
    (37, '301', 3, 567.89, 1, false, true, true, true),
    (37, '302', 3, 678.90, 2, true, true, true, true),
    (37, '401', 4, 789.01, 1, false, true, true, true),
    (37, '402', 4, 890.12, 2, true, true, true, true),
    (37, '501', 5, 901.23, 1, false, true, true, true),
    (37, '502', 5, 1011.12, 2, true, true, true, true),
    (37, '601', 6, 1112.13, 1, false, true, true, true),
    (37, '602', 6, 1213.14, 2, true, true, true, true),
    (38, '101', 1, 123.45, 1, false, true, true, true),
    (38, '102', 1, 234.56, 2, true, true, true, true),
    (38, '201', 2, 345.67, 1, false, true, true, true),
    (38, '202', 2, 456.78, 2, true, true, true, true),
    (38, '301', 3, 567.89, 1, false, true, true, true),
    (38, '302', 3, 678.90, 2, true, true, true, true),
    (38, '401', 4, 789.01, 1, false, true, true, true),
    (38, '402', 4, 890.12, 2, true, true, true, true),
    (38, '501', 5, 901.23, 1, false, true, true, true),
    (38, '502', 5, 1011.12, 2, true, true, true, true),
    (38, '601', 6, 1112.13, 1, false, true, true, true),
    (38, '602', 6, 1213.14, 2, true, true, true, true),
    (39, '101', 1, 123.45, 1, false, true, true, true),
    (39, '102', 1, 234.56, 2, true, true, true, true),
    (39, '201', 2, 345.67, 1, false, true, true, true),
    (39, '202', 2, 456.78, 2, true, true, true, true),
    (39, '301', 3, 567.89, 1, false, true, true, true),
    (39, '302', 3, 678.90, 2, true, true, true, true),
    (39, '401', 4, 789.01, 1, false, true, true, true),
    (39, '402', 4, 890.12, 2, true, true, true, true),
    (39, '501', 5, 901.23, 1, false, true, true, true),
    (39, '502', 5, 1011.12, 2, true, true, true, true),
    (39, '601', 6, 1112.13, 1, false, true, true, true),
    (39, '602', 6, 1213.14, 2, true, true, true, true),
    (40, '101', 1, 123.45, 1, false, true, true, true),
    (40, '102', 1, 234.56, 2, true, true, true, true),
    (40, '201', 2, 345.67, 1, false, true, true, true),
    (40, '202', 2, 456.78, 2, true, true, true, true),
    (40, '301', 3, 567.89, 1, false, true, true, true),
    (40, '302', 3, 678.90, 2, true, true, true, true),
    (40, '401', 4, 789.01, 1, false, true, true, true),
    (40, '402', 4, 890.12, 2, true, true, true, true),
    (40, '501', 5, 901.23, 1, false, true, true, true),
    (40, '502', 5, 1011.12, 2, true, true, true, true),
    (40, '601', 6, 1112.13, 1, false, true, true, true),
    (40, '602', 6, 1213.14, 2, true, true, true, true);

-- Insert into `room_damages` table
INSERT INTO room_damages (hotel_id, room_number, description) VALUES
    (1, '101', 'hole in wall'),
    (1, '102', 'bathroom sink not working');

-- Insert into `positions` table
INSERT INTO positions (position_name) VALUES
    ('manager'),
    ('receptionist'),
    ('housekeeper'),
    ('maintenance technician'),
    ('cook');

-- Insert into `employees` table
INSERT INTO employees (ssn, first_name, middle_initial, last_name, street_number, street_name, apt_number, city, province_or_state, country, zip, position_id, hotel_id) VALUES
    ('414149791', 'Caelestis', null, 'Iriney', '567', 'Lees Avenue', '888', 'Ottawa', 'Ontario', 'Canada', 'K1JBE9', 1, 2),
    ('404037198', 'Arnoldas', 'I', 'Sulejman', '12', 'Lawn Way', '2', 'Toronto', 'Ontario', 'Canada', 'K1G5E9', 1, 1),
    ('269884650', 'Khasan', null, 'Suman', '234', 'Patrick Avenue', '6', 'Houston', 'Texas', 'United States', '78006', 1, 3),
    ('325809765', 'Sophocles', null, 'Léandre', '56', 'Airway Street', '9', 'San Antonio', 'Texas', 'United States', '78008', 1, 4),
    ('357315340', 'Ryder', null, 'Arash', '2', 'Carling Street', '1422', 'Vancouver', 'British Columbia', 'Canada', 'V4C0E4', 1, 5),
    ('460447489', 'Geoffrey', null, 'Eckhart', '78', 'Swiss Street', '456', 'Surrey', 'British Columbia', 'Canada', 'V1M4B5', 1, 6),
    ('893095227', 'Dina', null, 'Gunna', '45', 'Queen Way', '457', 'Los Angeles', 'California', 'United States', '90005', 1, 7),
    ('326893630', 'Tiffany', null, 'Ardeth', '88', 'Louis Avenue', '458', 'San Diego', 'California', 'United States', '91005', 1, 8),
    ('519681599', 'Charlotte', null, 'Ajla', '20', 'Rue Polygon', '459', 'Montreal', 'Quebec', 'Canada', 'H1N3B5', 1, 9),
    ('927253750', 'Anila', null, 'Lassie', '206', 'Rue Pere', '500', 'Quebec City', 'Quebec', 'Canada', 'G2Z8K8', 1, 10),
    ('495449696', 'Taiwo', 'M', 'Goksu', '209', 'King Way', '501', 'Jacksonville', 'Florida', 'United States', '32012', 1, 11),
    ('936606473', 'Gili', 'S', 'Naomi', '233', 'Prince Way', '506', 'Miami', 'Florida', 'United States', '32018', 1, 12),
    ('722296177', 'Malone', 'B', 'Yachin', '84', 'Maple Street', '507', 'Calgary', 'Alberta', 'Canada', 'C2E8N9', 1, 13),
    ('282400220', 'Hanane', null, 'Shahin', '22', 'Knight Street', '55', 'Edmonton', 'Alberta', 'Canada', 'B2E8N9', 1, 14),
    ('123456789', 'John', 'D', 'Doe', '27', 'Pine Lane', '101', 'Oklahoma City', 'Oklahoma', 'United States', '73008', 1, 15),
    ('234567890', 'Jane', 'M', 'Doe', '23', 'Station Avenue', '102', 'Tulsa', 'Oklahoma', 'United States', '74039', 1, 16),
    ('345678901', 'Bob', null, 'Smith', '31', 'Marine Way', '200', 'Mississauga', 'Ontario', 'Canada', 'D4T0A1', 1, 17),
    ('456789012', 'Emily', 'A', 'Brown', '320', 'Museum Avenue', '44', 'Hamilton', 'Ontario', 'Canada', 'L0D1B0', 1, 18),
    ('567890123', 'William', 'T', 'Davis', '3340', 'Ironwood Lane', '6', 'Philadelphia', 'Pennsylvania', 'United States', '19019', 1, 19),
    ('678901234', 'Elizabeth', 'S', 'Taylor', '344', 'Globe Route', '77', 'Pittsburgh', 'Pennsylvania', 'United States', '16106', 1, 20),
    ('789012345', 'Michael', 'J', 'Wilson', '35', 'Rowan Lane', '5', 'Richmond', 'British Columbia', 'Canada', 'V6B0A2', 1, 21),
    ('890123456', 'Sarah', 'E', 'Anderson', '3', 'Monument Passage', '33', 'Burnaby', 'British Columbia', 'Canada', 'V3D0A5', 1, 22),
    ('901234567', 'David', 'K', 'Thomas', '5555', 'Meadow Route', '1', 'Phoenix', 'Arizona', 'United States', '85601', 1, 23),
    ('012345678', 'Olivia', 'L', 'Jackson', '37', 'Paradise Street', '8', 'Tuscon', 'Arizona', 'United States', '95641', 1, 24),
    ('123546789', 'Christopher', 'D', 'Harris', '4180', 'Medieval Avenue', '9', 'San Jose', 'California', 'United States', '64088', 1, 25),
    ('234657890', 'Ava', 'M', 'Martin', '4444', 'Lavender Street', '44', 'San Francisco', 'California', 'United States', '88816', 1, 26),
    ('345768901', 'Daniel', 'R', 'Thompson', '437', 'Senna Street', '66', 'Austin', 'Texas', 'United States', '73201', 1, 27),
    ('583127955', 'Matthew', 'L', 'Hutchinson', '437', 'Globe Boulevard', '66', 'El Paso', 'Texas', 'United States', '74401', 1, 28),
    ('470310645', 'Danya', null, 'Abir', '437', 'Autumn Boulevard', '66', 'Tampa', 'Florida', 'United States', '99992', 1, 29),
    ('210138121', 'Ali', null, 'Alam', '437', 'Hill Way', '66', 'Fort Lauderdale', 'Florida', 'United States', '97892', 1, 30),
    ('159773527', 'Alex', null, 'Hull', '437', 'Lower Lane', '66', 'Columbus', 'Ohio', 'United States', '93452', 1, 31),
    ('725329332', 'Adam', null, 'Olivier', '437', 'Bay View Way', '66', 'Cleveland', 'Ohio', 'United States', '98852', 1, 32),
    ('879012893', 'Chanelle', null, 'Wall', '437', 'Blossom Boulevard', '66', 'New York City', 'New York', 'United States', '92252', 1, 33),
    ('496578748', 'Hassan', null, 'Marwan', '437', 'Petal Avenue', '66', 'Brookhaven', 'New York', 'United States', '32322', 1, 34),
    ('932286200', 'Alexa', null, 'Sole', '437', 'Hazelnut Avenue', '66', 'Fresno', 'California', 'United States', '32344', 1, 35),
    ('155350115', 'Juan', 'G', 'Torres', '437', 'Greenfield Street', '66', 'Sacramento', 'California', 'United States', '32343', 1, 36),
    ('958299033', 'Adriana', null, 'Daniel', '437', 'Chapel Way', '66', 'Charlotte', 'North Calorina', 'United States', '32349', 1, 37),
    ('898460201', 'Tristan', null, 'Denis', '437', 'Amber Row', '66', 'Raleigh', 'North Calorina', 'United States', '32360', 1, 38),
    ('456202251', 'Angela', null, 'Wang', '437', 'Highland Avenue', '66', 'Seattle', 'Washington', 'United States', '44594', 1, 39),
    ('381486598', 'Tyson', null, 'High', '437', 'Bloomfield Lane', '66', 'Spokane', 'Washington', 'United States', '44094', 1, 40);
