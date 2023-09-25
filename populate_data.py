import random
from faker import Faker

def generate_locations_data(size):
    fake = Faker()
    location_types = ['restaurant', 'hotel', 'cafe']
    locations_data = []
    location_counts = {loc_type: 0 for loc_type in location_types}

    for _ in range(size):
        location_type = random.choice(location_types)
        location_counts[location_type] += 1
        name = f"{location_type}{location_counts[location_type]}"
        latitude, longitude = fake.latitude(), fake.longitude()
        geohash = fake.unique.md5()[:6]  # Generating a unique 6-character geohash for demonstration. In a real-world scenario, you might want to use a geohashing library.
        
        location = {
            'geohash': geohash,
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'type': location_type
        }
        locations_data.append(location)

    return locations_data

def write_to_sql_file(locations_data):
    with open("insert.sql", "w") as file:
        # Create table statement
        file.write('''CREATE TABLE IF NOT EXISTS locations (
            geohash VARCHAR(6) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            type VARCHAR(50) NOT NULL
        );
        ''')
        
        # Insert data
        file.write("INSERT INTO locations (geohash, name, latitude, longitude, type) VALUES\n")
        for i, location in enumerate(locations_data):
            file.write("('{}', '{}', {}, {}, '{}')".format(
                location['geohash'], location['name'], location['latitude'], location['longitude'], location['type']
            ))
            if i != len(locations_data) - 1:
                file.write(",\n")
            else:
                file.write(";\n")

locations_data = generate_locations_data(200)
write_to_sql_file(locations_data)
