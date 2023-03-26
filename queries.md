#### Create `chains` table

```sql
CREATE TABLE IF NOT EXISTS chains (
    chain_id SERIAL PRIMARY KEY,
    chain_name TEXT NOT NULL
    num_hotels INTEGER,
);
```

#### Create `chain_offices` table

```sql
CREATE TABLE IF NOT EXISTS chain_offices (
    chain_id INTEGER,
    street_number TEXT NOT NULL,
    street_name TEXT NOT NULL,
    apt_number TEXT,
    city TEXT NOT NULL,
    province_or_state TEXT,
    country TEXT NOT NULL,
    zip TEXT NOT NULL,
    FOREIGN KEY (chain_id) REFERENCES chains(chain_id)
);
```

#### Create `chain_phone_numbers` table

```sql
CREATE TABLE IF NOT EXISTS chain_phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    description TEXT,
    chain_id INTEGER,
    FOREIGN KEY(chain_id) REFERENCES chains(chain_id) ON DELETE CASCADE
);

```

#### Create `chain_email_addresses` table

```sql
CREATE TABLE IF NOT EXISTS chain_email_addresses (
    id SERIAL PRIMARY KEY,
    email_address TEXT NOT NULL,
    description TEXT,
    chain_id INTEGER,
    FOREIGN KEY(chain_id) REFERENCES chains(chain_id) ON DELETE CASCADE
);
```

#### Create `hotels` table

```sql
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
```

#### Create `hotel_phone_numbers` table

```sql
CREATE TABLE IF NOT EXISTS hotel_phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    description TEXT,
    hotel_id INTEGER,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE
);
```

#### Create `hotel_email_addresses` table

```sql
CREATE TABLE IF NOT EXISTS hotel_email_addresses (
    id SERIAL PRIMARY KEY,
    email_address TEXT NOT NULL,
    description TEXT,
    hotel_id INTEGER,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE
);
```

#### Create `view_types` table

```sql
CREATE TABLE IF NOT EXISTS view_types (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL
);
```

#### Create `rooms` table

```sql
CREATE TABLE IF NOT EXISTS rooms (
    hotel_id INTEGER,
    room_number TEXT,
    capacity INTEGER NOT NULL,
    price NUMERIC(8, 2) NOT NULL,
    view_type INTEGER,
    extensible BOOLEAN,
    CHECK (capacity > 0),
    CHECK (price > 0),
    PRIMARY KEY (hotel_id, room_number),
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE,
    FOREIGN KEY (view_type) REFERENCES view_types(id)
);
```

#### Create `room_amenities` table

```sql
CREATE TABLE IF NOT EXISTS room_amenities (
    hotel_id INTEGER,
    room_number TEXT,
    tv BOOLEAN,
    air_condition BOOLEAN,
    fridge BOOLEAN,
    PRIMARY KEY (hotel_id, room_number),
    FOREIGN KEY (hotel_id, room_number) REFERENCES rooms (hotel_id, room_number)
);
```

#### Create `room_damages` table

```sql
CREATE TABLE IF NOT EXISTS room_damages (
    hotel_id INTEGER,
    room_number TEXT,
    description TEXT NOT NULL,
    PRIMARY KEY (hotel_id, room_number, description),
    FOREIGN KEY (hotel_id, room_number) REFERENCES rooms (hotel_id, room_number)
);
```

#### Create `positions` table

```sql
CREATE TABLE IF NOT EXISTS positions (
    position_id SERIAL PRIMARY KEY,
    position_name TEXT NOT NULL,
)
```

#### Create `employees` table

```sql
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
    FOREIGN KEY (position_id) REFERENCES positions(position_id)
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
);
```

#### Add `manager_id` column to `hotels` table

```sql
ALTER TABLE hotels
ADD COLUMN manager_id INTEGER
FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
```

#### Create `customers` table

```sql
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    ssn VARCHAR(11) UNIQUE NOT NULL,
    registration_date DATE NOT NULL,
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
```

### Install uuid module

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

#### Create `bookings` table

```sql
CREATE TABLE IF NOT EXISTS bookings (
    booking_id UUID DEFAULT uuid_generate_v4(),
    customer_id INTEGER,
    hotel_id INTEGER,
    room_number TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    PRIMARY KEY (booking_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    FOREIGN KEY (hotel_id, room_number) REFERENCES rooms (hotel_id, room_number)
);
```

#### Create `rentals` table

```sql
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
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    FOREIGN KEY (booking_id) REFERENCES bookings (booking_id),
    FOREIGN KEY (hotel_id, room_number) REFERENCES rooms (hotel_id, room_number)
);
```

#### Insert into `chains` table

```sql
INSERT INTO chains(chain_name) VALUES
    ('Hotel Chain 1'),
    ('Hotel Chain 2'),
    ('Hotel Chain 3'),
    ('Hotel Chain 4'),
    ('Hotel Chain 5');
```

#### Insert into `hotels` table

```sql
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
```

#### Insert into `view_types` table

```sql
INSERT INTO view_types (description) VALUES
    ('Mountain'),
    ('Sea');
```

#### Insert into `rooms` table

```sql
INSERT INTO rooms (hotel_id, room_number, capacity, price, view_type, extensible) VALUES
    (1, '101', 1, 123.45, 1, false),
    (1, '102', 1, 234.56, 2, true),
    (1, '201', 2, 345.67, 1, false),
    (1, '202', 2, 456.78, 2, true),
    (1, '301', 3, 567.89, 1, false),
    (1, '302', 3, 678.90, 2, true),
    (1, '401', 4, 789.01, 1, false),
    (1, '402', 4, 890.12, 2, true),
    (1, '501', 5, 901.23, 1, false),
    (1, '502', 5, 1011.12, 2, true),
    (1, '601', 6, 1112.13, 1, false),
    (1, '602', 6, 1213.14, 2, true),
    (2, '101', 1, 123.45, 1, false),
    (2, '102', 1, 234.56, 2, true),
    (2, '201', 2, 345.67, 1, false),
    (2, '202', 2, 456.78, 2, true),
    (2, '301', 3, 567.89, 1, false),
    (2, '302', 3, 678.90, 2, true),
    (2, '401', 4, 789.01, 1, false),
    (2, '402', 4, 890.12, 2, true),
    (2, '501', 5, 901.23, 1, false),
    (2, '502', 5, 1011.12, 2, true),
    (2, '601', 6, 1112.13, 1, false),
    (2, '602', 6, 1213.14, 2, true),
    (3, '101', 1, 123.45, 1, false),
    (3, '102', 1, 234.56, 2, true),
    (3, '201', 2, 345.67, 1, false),
    (3, '202', 2, 456.78, 2, true),
    (3, '301', 3, 567.89, 1, false),
    (3, '302', 3, 678.90, 2, true),
    (3, '401', 4, 789.01, 1, false),
    (3, '402', 4, 890.12, 2, true),
    (3, '501', 5, 901.23, 1, false),
    (3, '502', 5, 1011.12, 2, true),
    (3, '601', 6, 1112.13, 1, false),
    (3, '602', 6, 1213.14, 2, true),
    (4, '101', 1, 123.45, 1, false),
    (4, '102', 1, 234.56, 2, true),
    (4, '201', 2, 345.67, 1, false),
    (4, '202', 2, 456.78, 2, true),
    (4, '301', 3, 567.89, 1, false),
    (4, '302', 3, 678.90, 2, true),
    (4, '401', 4, 789.01, 1, false),
    (4, '402', 4, 890.12, 2, true),
    (4, '501', 5, 901.23, 1, false),
    (4, '502', 5, 1011.12, 2, true),
    (4, '601', 6, 1112.13, 1, false),
    (4, '602', 6, 1213.14, 2, true),
    (5, '101', 1, 123.45, 1, false),
    (5, '102', 1, 234.56, 2, true),
    (5, '201', 2, 345.67, 1, false),
    (5, '202', 2, 456.78, 2, true),
    (5, '301', 3, 567.89, 1, false),
    (5, '302', 3, 678.90, 2, true),
    (5, '401', 4, 789.01, 1, false),
    (5, '402', 4, 890.12, 2, true),
    (5, '501', 5, 901.23, 1, false),
    (5, '502', 5, 1011.12, 2, true),
    (5, '601', 6, 1112.13, 1, false),
    (5, '602', 6, 1213.14, 2, true),
    (6, '101', 1, 123.45, 1, false),
    (6, '102', 1, 234.56, 2, true),
    (6, '201', 2, 345.67, 1, false),
    (6, '202', 2, 456.78, 2, true),
    (6, '301', 3, 567.89, 1, false),
    (6, '302', 3, 678.90, 2, true),
    (6, '401', 4, 789.01, 1, false),
    (6, '402', 4, 890.12, 2, true),
    (6, '501', 5, 901.23, 1, false),
    (6, '502', 5, 1011.12, 2, true),
    (6, '601', 6, 1112.13, 1, false),
    (6, '602', 6, 1213.14, 2, true),
    (7, '101', 1, 123.45, 1, false),
    (7, '102', 1, 234.56, 2, true),
    (7, '201', 2, 345.67, 1, false),
    (7, '202', 2, 456.78, 2, true),
    (7, '301', 3, 567.89, 1, false),
    (7, '302', 3, 678.90, 2, true),
    (7, '401', 4, 789.01, 1, false),
    (7, '402', 4, 890.12, 2, true),
    (7, '501', 5, 901.23, 1, false),
    (7, '502', 5, 1011.12, 2, true),
    (7, '601', 6, 1112.13, 1, false),
    (7, '602', 6, 1213.14, 2, true),
    (8, '101', 1, 123.45, 1, false),
    (8, '102', 1, 234.56, 2, true),
    (8, '201', 2, 345.67, 1, false),
    (8, '202', 2, 456.78, 2, true),
    (8, '301', 3, 567.89, 1, false),
    (8, '302', 3, 678.90, 2, true),
    (8, '401', 4, 789.01, 1, false),
    (8, '402', 4, 890.12, 2, true),
    (8, '501', 5, 901.23, 1, false),
    (8, '502', 5, 1011.12, 2, true),
    (8, '601', 6, 1112.13, 1, false),
    (8, '602', 6, 1213.14, 2, true),
    (9, '101', 1, 123.45, 1, false),
    (9, '102', 1, 234.56, 2, true),
    (9, '201', 2, 345.67, 1, false),
    (9, '202', 2, 456.78, 2, true),
    (9, '301', 3, 567.89, 1, false),
    (9, '302', 3, 678.90, 2, true),
    (9, '401', 4, 789.01, 1, false),
    (9, '402', 4, 890.12, 2, true),
    (9, '501', 5, 901.23, 1, false),
    (9, '502', 5, 1011.12, 2, true),
    (9, '601', 6, 1112.13, 1, false),
    (9, '602', 6, 1213.14, 2, true),
    (10, '101', 1, 123.45, 1, false),
    (10, '102', 1, 234.56, 2, true),
    (10, '201', 2, 345.67, 1, false),
    (10, '202', 2, 456.78, 2, true),
    (10, '301', 3, 567.89, 1, false),
    (10, '302', 3, 678.90, 2, true),
    (10, '401', 4, 789.01, 1, false),
    (10, '402', 4, 890.12, 2, true),
    (10, '501', 5, 901.23, 1, false),
    (10, '502', 5, 1011.12, 2, true),
    (10, '601', 6, 1112.13, 1, false),
    (10, '602', 6, 1213.14, 2, true),
    (11, '101', 1, 123.45, 1, false),
    (11, '102', 1, 234.56, 2, true),
    (11, '201', 2, 345.67, 1, false),
    (11, '202', 2, 456.78, 2, true),
    (11, '301', 3, 567.89, 1, false),
    (11, '302', 3, 678.90, 2, true),
    (11, '401', 4, 789.01, 1, false),
    (11, '402', 4, 890.12, 2, true),
    (11, '501', 5, 901.23, 1, false),
    (11, '502', 5, 1011.12, 2, true),
    (11, '601', 6, 1112.13, 1, false),
    (11, '602', 6, 1213.14, 2, true),
    (12, '101', 1, 123.45, 1, false),
    (12, '102', 1, 234.56, 2, true),
    (12, '201', 2, 345.67, 1, false),
    (12, '202', 2, 456.78, 2, true),
    (12, '301', 3, 567.89, 1, false),
    (12, '302', 3, 678.90, 2, true),
    (12, '401', 4, 789.01, 1, false),
    (12, '402', 4, 890.12, 2, true),
    (12, '501', 5, 901.23, 1, false),
    (12, '502', 5, 1011.12, 2, true),
    (12, '601', 6, 1112.13, 1, false),
    (12, '602', 6, 1213.14, 2, true),
    (13, '101', 1, 123.45, 1, false),
    (13, '102', 1, 234.56, 2, true),
    (13, '201', 2, 345.67, 1, false),
    (13, '202', 2, 456.78, 2, true),
    (13, '301', 3, 567.89, 1, false),
    (13, '302', 3, 678.90, 2, true),
    (13, '401', 4, 789.01, 1, false),
    (13, '402', 4, 890.12, 2, true),
    (13, '501', 5, 901.23, 1, false),
    (13, '502', 5, 1011.12, 2, true),
    (13, '601', 6, 1112.13, 1, false),
    (13, '602', 6, 1213.14, 2, true),
    (14, '101', 1, 123.45, 1, false),
    (14, '102', 1, 234.56, 2, true),
    (14, '201', 2, 345.67, 1, false),
    (14, '202', 2, 456.78, 2, true),
    (14, '301', 3, 567.89, 1, false),
    (14, '302', 3, 678.90, 2, true),
    (14, '401', 4, 789.01, 1, false),
    (14, '402', 4, 890.12, 2, true),
    (14, '501', 5, 901.23, 1, false),
    (14, '502', 5, 1011.12, 2, true),
    (14, '601', 6, 1112.13, 1, false),
    (14, '602', 6, 1213.14, 2, true),
    (15, '101', 1, 123.45, 1, false),
    (15, '102', 1, 234.56, 2, true),
    (15, '201', 2, 345.67, 1, false),
    (15, '202', 2, 456.78, 2, true),
    (15, '301', 3, 567.89, 1, false),
    (15, '302', 3, 678.90, 2, true),
    (15, '401', 4, 789.01, 1, false),
    (15, '402', 4, 890.12, 2, true),
    (15, '501', 5, 901.23, 1, false),
    (15, '502', 5, 1011.12, 2, true),
    (15, '601', 6, 1112.13, 1, false),
    (15, '602', 6, 1213.14, 2, true),
    (16, '101', 1, 123.45, 1, false),
    (16, '102', 1, 234.56, 2, true),
    (16, '201', 2, 345.67, 1, false),
    (16, '202', 2, 456.78, 2, true),
    (16, '301', 3, 567.89, 1, false),
    (16, '302', 3, 678.90, 2, true),
    (16, '401', 4, 789.01, 1, false),
    (16, '402', 4, 890.12, 2, true),
    (16, '501', 5, 901.23, 1, false),
    (16, '502', 5, 1011.12, 2, true),
    (16, '601', 6, 1112.13, 1, false),
    (16, '602', 6, 1213.14, 2, true),
    (17, '101', 1, 123.45, 1, false),
    (17, '102', 1, 234.56, 2, true),
    (17, '201', 2, 345.67, 1, false),
    (17, '202', 2, 456.78, 2, true),
    (17, '301', 3, 567.89, 1, false),
    (17, '302', 3, 678.90, 2, true),
    (17, '401', 4, 789.01, 1, false),
    (17, '402', 4, 890.12, 2, true),
    (17, '501', 5, 901.23, 1, false),
    (17, '502', 5, 1011.12, 2, true),
    (17, '601', 6, 1112.13, 1, false),
    (17, '602', 6, 1213.14, 2, true),
    (18, '101', 1, 123.45, 1, false),
    (18, '102', 1, 234.56, 2, true),
    (18, '201', 2, 345.67, 1, false),
    (18, '202', 2, 456.78, 2, true),
    (18, '301', 3, 567.89, 1, false),
    (18, '302', 3, 678.90, 2, true),
    (18, '401', 4, 789.01, 1, false),
    (18, '402', 4, 890.12, 2, true),
    (18, '501', 5, 901.23, 1, false),
    (18, '502', 5, 1011.12, 2, true),
    (18, '601', 6, 1112.13, 1, false),
    (18, '602', 6, 1213.14, 2, true),
    (19, '101', 1, 123.45, 1, false),
    (19, '102', 1, 234.56, 2, true),
    (19, '201', 2, 345.67, 1, false),
    (19, '202', 2, 456.78, 2, true),
    (19, '301', 3, 567.89, 1, false),
    (19, '302', 3, 678.90, 2, true),
    (19, '401', 4, 789.01, 1, false),
    (19, '402', 4, 890.12, 2, true),
    (19, '501', 5, 901.23, 1, false),
    (19, '502', 5, 1011.12, 2, true),
    (19, '601', 6, 1112.13, 1, false),
    (19, '602', 6, 1213.14, 2, true),
    (20, '101', 1, 123.45, 1, false),
    (20, '102', 1, 234.56, 2, true),
    (20, '201', 2, 345.67, 1, false),
    (20, '202', 2, 456.78, 2, true),
    (20, '301', 3, 567.89, 1, false),
    (20, '302', 3, 678.90, 2, true),
    (20, '401', 4, 789.01, 1, false),
    (20, '402', 4, 890.12, 2, true),
    (20, '501', 5, 901.23, 1, false),
    (20, '502', 5, 1011.12, 2, true),
    (20, '601', 6, 1112.13, 1, false),
    (20, '602', 6, 1213.14, 2, true),
    (21, '101', 1, 123.45, 1, false),
    (21, '102', 1, 234.56, 2, true),
    (21, '201', 2, 345.67, 1, false),
    (21, '202', 2, 456.78, 2, true),
    (21, '301', 3, 567.89, 1, false),
    (21, '302', 3, 678.90, 2, true),
    (21, '401', 4, 789.01, 1, false),
    (21, '402', 4, 890.12, 2, true),
    (21, '501', 5, 901.23, 1, false),
    (21, '502', 5, 1011.12, 2, true),
    (21, '601', 6, 1112.13, 1, false),
    (21, '602', 6, 1213.14, 2, true),
    (22, '101', 1, 123.45, 1, false),
    (22, '102', 1, 234.56, 2, true),
    (22, '201', 2, 345.67, 1, false),
    (22, '202', 2, 456.78, 2, true),
    (22, '301', 3, 567.89, 1, false),
    (22, '302', 3, 678.90, 2, true),
    (22, '401', 4, 789.01, 1, false),
    (22, '402', 4, 890.12, 2, true),
    (22, '501', 5, 901.23, 1, false),
    (22, '502', 5, 1011.12, 2, true),
    (22, '601', 6, 1112.13, 1, false),
    (22, '602', 6, 1213.14, 2, true),
    (23, '101', 1, 123.45, 1, false),
    (23, '102', 1, 234.56, 2, true),
    (23, '201', 2, 345.67, 1, false),
    (23, '202', 2, 456.78, 2, true),
    (23, '301', 3, 567.89, 1, false),
    (23, '302', 3, 678.90, 2, true),
    (23, '401', 4, 789.01, 1, false),
    (23, '402', 4, 890.12, 2, true),
    (23, '501', 5, 901.23, 1, false),
    (23, '502', 5, 1011.12, 2, true),
    (23, '601', 6, 1112.13, 1, false),
    (23, '602', 6, 1213.14, 2, true),
    (24, '101', 1, 123.45, 1, false),
    (24, '102', 1, 234.56, 2, true),
    (24, '201', 2, 345.67, 1, false),
    (24, '202', 2, 456.78, 2, true),
    (24, '301', 3, 567.89, 1, false),
    (24, '302', 3, 678.90, 2, true),
    (24, '401', 4, 789.01, 1, false),
    (24, '402', 4, 890.12, 2, true),
    (24, '501', 5, 901.23, 1, false),
    (24, '502', 5, 1011.12, 2, true),
    (24, '601', 6, 1112.13, 1, false),
    (24, '602', 6, 1213.14, 2, true),
    (25, '101', 1, 123.45, 1, false),
    (25, '102', 1, 234.56, 2, true),
    (25, '201', 2, 345.67, 1, false),
    (25, '202', 2, 456.78, 2, true),
    (25, '301', 3, 567.89, 1, false),
    (25, '302', 3, 678.90, 2, true),
    (25, '401', 4, 789.01, 1, false),
    (25, '402', 4, 890.12, 2, true),
    (25, '501', 5, 901.23, 1, false),
    (25, '502', 5, 1011.12, 2, true),
    (25, '601', 6, 1112.13, 1, false),
    (25, '602', 6, 1213.14, 2, true),
    (26, '101', 1, 123.45, 1, false),
    (26, '102', 1, 234.56, 2, true),
    (26, '201', 2, 345.67, 1, false),
    (26, '202', 2, 456.78, 2, true),
    (26, '301', 3, 567.89, 1, false),
    (26, '302', 3, 678.90, 2, true),
    (26, '401', 4, 789.01, 1, false),
    (26, '402', 4, 890.12, 2, true),
    (26, '501', 5, 901.23, 1, false),
    (26, '502', 5, 1011.12, 2, true),
    (26, '601', 6, 1112.13, 1, false),
    (26, '602', 6, 1213.14, 2, true),
    (27, '101', 1, 123.45, 1, false),
    (27, '102', 1, 234.56, 2, true),
    (27, '201', 2, 345.67, 1, false),
    (27, '202', 2, 456.78, 2, true),
    (27, '301', 3, 567.89, 1, false),
    (27, '302', 3, 678.90, 2, true),
    (27, '401', 4, 789.01, 1, false),
    (27, '402', 4, 890.12, 2, true),
    (27, '501', 5, 901.23, 1, false),
    (27, '502', 5, 1011.12, 2, true),
    (27, '601', 6, 1112.13, 1, false),
    (27, '602', 6, 1213.14, 2, true),
    (28, '101', 1, 123.45, 1, false),
    (28, '102', 1, 234.56, 2, true),
    (28, '201', 2, 345.67, 1, false),
    (28, '202', 2, 456.78, 2, true),
    (28, '301', 3, 567.89, 1, false),
    (28, '302', 3, 678.90, 2, true),
    (28, '401', 4, 789.01, 1, false),
    (28, '402', 4, 890.12, 2, true),
    (28, '501', 5, 901.23, 1, false),
    (28, '502', 5, 1011.12, 2, true),
    (28, '601', 6, 1112.13, 1, false),
    (28, '602', 6, 1213.14, 2, true),
    (29, '101', 1, 123.45, 1, false),
    (29, '102', 1, 234.56, 2, true),
    (29, '201', 2, 345.67, 1, false),
    (29, '202', 2, 456.78, 2, true),
    (29, '301', 3, 567.89, 1, false),
    (29, '302', 3, 678.90, 2, true),
    (29, '401', 4, 789.01, 1, false),
    (29, '402', 4, 890.12, 2, true),
    (29, '501', 5, 901.23, 1, false),
    (29, '502', 5, 1011.12, 2, true),
    (29, '601', 6, 1112.13, 1, false),
    (29, '602', 6, 1213.14, 2, true),
    (30, '101', 1, 123.45, 1, false),
    (30, '102', 1, 234.56, 2, true),
    (30, '201', 2, 345.67, 1, false),
    (30, '202', 2, 456.78, 2, true),
    (30, '301', 3, 567.89, 1, false),
    (30, '302', 3, 678.90, 2, true),
    (30, '401', 4, 789.01, 1, false),
    (30, '402', 4, 890.12, 2, true),
    (30, '501', 5, 901.23, 1, false),
    (30, '502', 5, 1011.12, 2, true),
    (30, '601', 6, 1112.13, 1, false),
    (30, '602', 6, 1213.14, 2, true),
    (31, '101', 1, 123.45, 1, false),
    (31, '102', 1, 234.56, 2, true),
    (31, '201', 2, 345.67, 1, false),
    (31, '202', 2, 456.78, 2, true),
    (31, '301', 3, 567.89, 1, false),
    (31, '302', 3, 678.90, 2, true),
    (31, '401', 4, 789.01, 1, false),
    (31, '402', 4, 890.12, 2, true),
    (31, '501', 5, 901.23, 1, false),
    (31, '502', 5, 1011.12, 2, true),
    (31, '601', 6, 1112.13, 1, false),
    (31, '602', 6, 1213.14, 2, true),
    (32, '101', 1, 123.45, 1, false),
    (32, '102', 1, 234.56, 2, true),
    (32, '201', 2, 345.67, 1, false),
    (32, '202', 2, 456.78, 2, true),
    (32, '301', 3, 567.89, 1, false),
    (32, '302', 3, 678.90, 2, true),
    (32, '401', 4, 789.01, 1, false),
    (32, '402', 4, 890.12, 2, true),
    (32, '501', 5, 901.23, 1, false),
    (32, '502', 5, 1011.12, 2, true),
    (32, '601', 6, 1112.13, 1, false),
    (32, '602', 6, 1213.14, 2, true),
    (33, '101', 1, 123.45, 1, false),
    (33, '102', 1, 234.56, 2, true),
    (33, '201', 2, 345.67, 1, false),
    (33, '202', 2, 456.78, 2, true),
    (33, '301', 3, 567.89, 1, false),
    (33, '302', 3, 678.90, 2, true),
    (33, '401', 4, 789.01, 1, false),
    (33, '402', 4, 890.12, 2, true),
    (33, '501', 5, 901.23, 1, false),
    (33, '502', 5, 1011.12, 2, true),
    (33, '601', 6, 1112.13, 1, false),
    (33, '602', 6, 1213.14, 2, true),
    (34, '101', 1, 123.45, 1, false),
    (34, '102', 1, 234.56, 2, true),
    (34, '201', 2, 345.67, 1, false),
    (34, '202', 2, 456.78, 2, true),
    (34, '301', 3, 567.89, 1, false),
    (34, '302', 3, 678.90, 2, true),
    (34, '401', 4, 789.01, 1, false),
    (34, '402', 4, 890.12, 2, true),
    (34, '501', 5, 901.23, 1, false),
    (34, '502', 5, 1011.12, 2, true),
    (34, '601', 6, 1112.13, 1, false),
    (34, '602', 6, 1213.14, 2, true),
    (35, '101', 1, 123.45, 1, false),
    (35, '102', 1, 234.56, 2, true),
    (35, '201', 2, 345.67, 1, false),
    (35, '202', 2, 456.78, 2, true),
    (35, '301', 3, 567.89, 1, false),
    (35, '302', 3, 678.90, 2, true),
    (35, '401', 4, 789.01, 1, false),
    (35, '402', 4, 890.12, 2, true),
    (35, '501', 5, 901.23, 1, false),
    (35, '502', 5, 1011.12, 2, true),
    (35, '601', 6, 1112.13, 1, false),
    (35, '602', 6, 1213.14, 2, true),
    (36, '101', 1, 123.45, 1, false),
    (36, '102', 1, 234.56, 2, true),
    (36, '201', 2, 345.67, 1, false),
    (36, '202', 2, 456.78, 2, true),
    (36, '301', 3, 567.89, 1, false),
    (36, '302', 3, 678.90, 2, true),
    (36, '401', 4, 789.01, 1, false),
    (36, '402', 4, 890.12, 2, true),
    (36, '501', 5, 901.23, 1, false),
    (36, '502', 5, 1011.12, 2, true),
    (36, '601', 6, 1112.13, 1, false),
    (36, '602', 6, 1213.14, 2, true),
    (37, '101', 1, 123.45, 1, false),
    (37, '102', 1, 234.56, 2, true),
    (37, '201', 2, 345.67, 1, false),
    (37, '202', 2, 456.78, 2, true),
    (37, '301', 3, 567.89, 1, false),
    (37, '302', 3, 678.90, 2, true),
    (37, '401', 4, 789.01, 1, false),
    (37, '402', 4, 890.12, 2, true),
    (37, '501', 5, 901.23, 1, false),
    (37, '502', 5, 1011.12, 2, true),
    (37, '601', 6, 1112.13, 1, false),
    (37, '602', 6, 1213.14, 2, true),
    (38, '101', 1, 123.45, 1, false),
    (38, '102', 1, 234.56, 2, true),
    (38, '201', 2, 345.67, 1, false),
    (38, '202', 2, 456.78, 2, true),
    (38, '301', 3, 567.89, 1, false),
    (38, '302', 3, 678.90, 2, true),
    (38, '401', 4, 789.01, 1, false),
    (38, '402', 4, 890.12, 2, true),
    (38, '501', 5, 901.23, 1, false),
    (38, '502', 5, 1011.12, 2, true),
    (38, '601', 6, 1112.13, 1, false),
    (38, '602', 6, 1213.14, 2, true),
    (39, '101', 1, 123.45, 1, false),
    (39, '102', 1, 234.56, 2, true),
    (39, '201', 2, 345.67, 1, false),
    (39, '202', 2, 456.78, 2, true),
    (39, '301', 3, 567.89, 1, false),
    (39, '302', 3, 678.90, 2, true),
    (39, '401', 4, 789.01, 1, false),
    (39, '402', 4, 890.12, 2, true),
    (39, '501', 5, 901.23, 1, false),
    (39, '502', 5, 1011.12, 2, true),
    (39, '601', 6, 1112.13, 1, false),
    (39, '602', 6, 1213.14, 2, true),
    (40, '101', 1, 123.45, 1, false),
    (40, '102', 1, 234.56, 2, true),
    (40, '201', 2, 345.67, 1, false),
    (40, '202', 2, 456.78, 2, true),
    (40, '301', 3, 567.89, 1, false),
    (40, '302', 3, 678.90, 2, true),
    (40, '401', 4, 789.01, 1, false),
    (40, '402', 4, 890.12, 2, true),
    (40, '501', 5, 901.23, 1, false),
    (40, '502', 5, 1011.12, 2, true),
    (40, '601', 6, 1112.13, 1, false),
    (40, '602', 6, 1213.14, 2, true);
```

#### num_hotels trigger

```sql
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
```

#### num_rooms trigger

```sql
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
```
