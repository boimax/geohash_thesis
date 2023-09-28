import math
import time
import argparse
from clint.textui import puts, indent, colored
import random
from faker import Faker

class Main:
    BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


    #----------------------------------------#1.ENCODING FUNCTION----------------------------------------
    @staticmethod
    def encode(lat, lon, precision=None):
        """
        Recursion for Optimal Precision: Check if a specific precision is given; if not, calculate the optimal precision automatically.
        """
        if precision is None:
            for p in range(1, 13):
                hash = Main.encode(lat, lon, p)
                posn = Main.decode(hash)
                if posn['lat'] == lat and posn['lon'] == lon:
                    return hash
            precision = 12
        
        """
        Input Validation:lat, lon, and precision should be right types
        """
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)) or not isinstance(precision, int):
            raise ValueError("Invalid geohash")


        """
        Bit Manipulation and Bounds Adjustment
        """

        idx = 0  # Initialise the index for BASE32 character selection
        bit = 0  # Bit counter to keep track of bit processing (5 bits    represent a character in BASE32)
        evenBit = True  # Flag to alternate between long and lat
        geohash = ''  

        # Initialize boundaries for latitude and longitude
        latMin, latMax = -90, 90
        lonMin, lonMax = -180, 180

        # Loop to make the geohash string up to the required precision
        while len(geohash) < precision:
            if evenBit:  # If it's an even bit, process longitude
                lonMid = (lonMin + lonMax) / 2 # Find midpoint for lon
                if lon >= lonMid:
                    idx = idx*2 + 1
                    lonMin = lonMid
                else:
                    idx = idx*2
                    lonMax = lonMid
            else:  # If it's an odd bit, process latitude
                latMid = (latMin + latMax) / 2 # Find midpoint for lat
                if lat >= latMid:
                    idx = idx*2 + 1
                    latMin = latMid
                else:
                    idx = idx*2
                    latMax = latMid

            evenBit = not evenBit  # Toggle the evenBit flag for next iteration
            """
            BASE32 Character Addition: If 5 bits are processed (0 to 4), append the corresponding BASE32 character to the geohash, reset bit counter and index
            """
            if bit == 4: 
                geohash += Main.BASE32[idx]
                bit = 0 
                idx = 0  
            else:
                bit += 1 
        
        return geohash 



    #----------------------------------------#2.DECODING FUNCTION----------------------------------------

    @staticmethod
    def bounds(geohash):
        """
        This function takes a geohash and returns the bounding box                 
        Is represented in terms of southwest and northeast coordinates.
        """
        geohash_len = len(geohash)
        lat_min, lat_max = -90.0, 90.0
        lon_min, lon_max = -180.0, 180.0

        is_lon = True
        for i in range(geohash_len):
            char_idx = Main.BASE32.index(geohash[i])
            for j in range(5):
                #isolate each bit from the char_idx.
                mask = 1 << (4 - j)
                """
                For longitude (is_lon == True): If the bit is 1, it updates lon_min; if 0, it updates lon_max.          
                For latitude (is_lon == False): If the bit is 1, it updates lat_min; if 0, it updates lat_max.
                """
                if is_lon:
                    if char_idx & mask:
                        lon_min = (lon_min + lon_max) / 2
                    else:
                        lon_max = (lon_min + lon_max) / 2
                else:
                    if char_idx & mask:
                        lat_min = (lat_min + lat_max) / 2
                    else:
                        lat_max = (lat_min + lat_max) / 2
                is_lon = not is_lon

        return {'sw': {'lat': lat_min, 'lon': lon_min}, 'ne': {'lat': lat_max, 'lon': lon_max}}

    @staticmethod
    def decode(geohash):
        """
        This function decodes a geohash to its approximate central point, 
        utilizing the bounds function to find the geographical area it represents, 
        then calculating the central point within that area.
        """
        bounds = Main.bounds(geohash)
        lat_min, lon_min = bounds['sw']['lat'], bounds['sw']['lon']
        lat_max, lon_max = bounds['ne']['lat'], bounds['ne']['lon']

        lat = (lat_min + lat_max) / 2
        lon = (lon_min + lon_max) / 2

        # return {lat, lon}
        return {'lat': lat, 'lon': lon}

    

        #----------------------------------------#3.GET NEARBY GEOHASHES FUNCTION----------------------------------------

    """
        This function calculates a bounding box around the point [lat, lon]
        with the given radius, precision and returns the geohashes that are within this bounding box.
    
        Returns:
        list: A list of geohashes within the bounding box.
    """
    
    @staticmethod
    def in_circle_check(latitude, longitude, centre_lat, centre_lon, radius):
        x_diff = longitude - centre_lon
        y_diff = latitude - centre_lat
        return math.pow(x_diff, 2) + math.pow(y_diff, 2) <= math.pow(radius, 2)
    

    @staticmethod
    def get_centroid(latitude, longitude, height, width):
        y_cen = latitude + (height / 2)
        x_cen = longitude + (width / 2)
        return x_cen, y_cen


    @staticmethod
    def convert_to_latlon(y, x, latitude, longitude):
        r_earth = 6371000
        lat_diff = (y / r_earth) * (180 / math.pi)
        lon_diff = (x / r_earth) * (180 / math.pi) / math.cos(latitude * math.pi / 180)
        return latitude + lat_diff, longitude + lon_diff


    @staticmethod
    def get_nearby_geohashes(latitude, longitude, radius, precision):
        original_hash = Main.encode(latitude, longitude, precision) 

        grid_width = [5009400.0, 1252300.0, 156500.0, 39100.0, 4900.0, 1200.0, 152.9, 38.2, 4.8, 1.2, 0.149, 0.0370]
        grid_height = [4992600.0, 624100.0, 156000.0, 19500.0, 4900.0, 609.4, 152.4, 19.0, 4.8, 0.595, 0.149, 0.0199]

        height = grid_height[precision - 1] / 2
        width = grid_width[precision - 1] / 2
        """
        The lines calculate cell-heights and cell-widths within the search area's radius. 
        This determines moves to check in each direction from the original geohash.
        """
        lat_moves = math.ceil(radius / height)
        lon_moves = math.ceil(radius / width)

        #generate a grid of points around the original latitude and longitude within a certain radius.
        points = []
        for i in range(lat_moves):
            temp_lat = height * i
            for j in range(lon_moves):
                temp_lon = width * j
                """
                Checks if (temp_lat, temp_lon) is within the specified radius from (0, 0) as the grid of points is square, while the search area is a circle. 
                This filters out points in the square corners but outside the circle.
                """
                if Main.in_circle_check(temp_lat, temp_lon, 0, 0, radius):  
                    """
                    Explore grid cells around the original point in all four quadrants (NE, NW, SE, SW).
                    """
                    for x_cen, y_cen in [(temp_lat, temp_lon), (-temp_lat, temp_lon), (temp_lat, -temp_lon), (-temp_lat, -temp_lon)]:
                        lat, lon = Main.convert_to_latlon(y_cen, x_cen, latitude, longitude)
                        points.append((lat, lon))

        geohashes = [Main.encode(point[0], point[1], precision) for point in points if Main.encode(point[0], point[1], precision) != original_hash]
        geohashes = sorted(list(set(geohashes)))
        return geohashes



    #----------------------------------------#4.CALCULATE 2 GEOHASHES DISTANCE FUNCTION----------------------------------------


    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points
        on the Earth's surface given their latitude and longitude
        in decimal degrees.
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        r = 6371  # Radius of Earth in kilometers
        return r * c

    def geohash_distance(geohash1, geohash2):

        geohash_decode1 = Main.decode(geohash1)
        lat1, lon1 = geohash_decode1['lat'], geohash_decode1['lon']
        for hash2 in geohash2:
            geohash_decode2 = Main.decode(hash2)
            lat2, lon2 = geohash_decode2['lat'], geohash_decode2['lon']
            distance = Main.haversine_distance(lat1, lon1, lat2, lon2)
            puts(colored.green((f"Distance between {geohash1} -> {hash2} = {distance:.2f} km")))
    


    #----------------------------------------#5.GENERATE LOCATIONS DATA FUNCTION----------------------------------------

    """
        Faking locations_data for testing the main function: get_nearby_locations()
    """

    def generate_locations_data(size, central_lat, central_lon, precision):
        fake = Faker()
        location_types = ['restaurant', 'hotel', 'cafe']
        locations_data = []
        location_counts = {loc_type: 0 for loc_type in location_types}

        perturb = 0.05  # Adjust this value for more/less deviation

        for _ in range(size):
            location_type = random.choice(location_types)
            location_counts[location_type] += 1
            name = f"{location_type}{location_counts[location_type]}"
            
            # Generate a latitude and longitude that's a small deviation from central_lat, central_lon
            latitude = central_lat + random.uniform(-perturb, perturb)
            longitude = central_lon + random.uniform(-perturb, perturb)
            geohash = Main.encode(latitude, longitude, precision)
            
            location = {
                'geohash': geohash,
                'name': name,
                'latitude': latitude,
                'longitude': longitude,
                'type': location_type
            }
            locations_data.append(location)

        return locations_data
    



    #----------------------------------------#6.GET NEARBY LOCATIONS FUNCTION----------------------------------------



    def get_nearby_locations(lat, lon, radius, precision, locations_data, location_type):
        """
        This function retrieves locations that are within a specified radius from a given latitude and longitude point.

        Returns:
        list: A list of dictionaries representing nearby locations, each containing details like name, latitude, longitude, and type.
        """

        # Step 1: Get the nearby geohashes around the specified radius
        nearby_geohashes = Main.get_nearby_geohashes(lat, lon, radius, precision)
        
        # Step 2: Filter the locations data based on the nearby geohashes and (optionally) the location type
        result = []
        for location in locations_data:
            if location['geohash'] in nearby_geohashes:
                if location_type is None or location['type'] == location_type:
                    result.append(location)
        
        return result




    
#------------------------------------------------TESTING-----------------------------------------------------------


def print_header(message):
    puts(colored.yellow(f'----------------{message}--------------------'))

def print_colored_message(message, value, color=colored.green):
    puts(color(f'{message} {value}'))

#1. ENCODING FUNCTION
def display_encode_function(lat, lon, precision=None):
    print_header("#1.ENCODE FUNCTION")
    start_time = time.time()
    geohash = Main.encode(lat, lon, precision)
    print_colored_message(f'Geohash of the coordinate {{{lat}, {lon}}} is:', geohash, colored.green)
    elapsed_time = time.time() - start_time
    print_colored_message('\nTotal execution time #1:', f'{elapsed_time} seconds', colored.red)
    puts('\n\n')


#2. DECODE FUNCTION
def display_decode_function(geohash):
    print_header("#2.DECODE FUNCTION")
    start_time = time.time()
    coords = Main.decode(geohash)
    print_colored_message(f'Coordinate of {geohash} is:', coords)
    elapsed_time = time.time() - start_time
    print_colored_message('\nTotal execution time #2:', f'{elapsed_time} seconds', colored.red)
    puts('\n\n')


#3. GET NEARBY GEOHASHES FUNCTION  
def display_nearby_geohashes(lat, lon, radius, precision):
    print_header("#3.GET NEARBY GEOHASHES FUNCTION")
    start_time = time.time()
    geohashes = Main.get_nearby_geohashes(lat, lon, radius, precision)
    print_colored_message(f'Total {len(geohashes)} geohashes within {radius}m of ({lat}, {lon}) coordinate (geohash: {Main.encode(lat, lon, 6)}):\n','\n'.join(geohashes))
    elapsed_time = time.time() - start_time
    print_colored_message('\nTotal execution time #3:', f'{elapsed_time} seconds', colored.red)
    puts('\n\n')


#4. GEOHASHES DISTANCE FUNCTION
def display_geohashes_distance(geohash1, lat, lon, radius, precision):
    print_header("#4.GEOHASHES DISTANCE FUNCTION")
    start_time = time.time()
    geohash2 = Main.get_nearby_geohashes(lat, lon, radius, precision)
    Main.geohash_distance(geohash1, geohash2)
    elapsed_time = time.time() - start_time
    print_colored_message('\nTotal execution time #4:', f'{elapsed_time} seconds', colored.red)
    puts('\n\n')


#5. GENERATE LOCATIONS DATA FUNCTION
def display_locations_data(size, central_lat, central_lon, precision):
    print_header("#5.GENERATE LOCATIONS DATA FUNCTION")
    start_time = time.time()
    locations_data = Main.generate_locations_data(size, central_lat, central_lon, precision)
    print_colored_message(f'Fake Locations Data:\n', locations_data)
    elapsed_time = time.time() - start_time
    print_colored_message('\nTotal execution time #5:', f'{elapsed_time} seconds', colored.red)
    puts('\n\n')


#6. GET NEARBY LOCATIONS FUNCTION
def display_nearby_locations(lat, lon, radius, precision, location_type):
    print_header("#6.GET NEARBY LOCATIONS FUNCTION")
    start_time = time.time()
    locations_data = Main.generate_locations_data(50, lat, lon, precision)
    nearby_locations = Main.get_nearby_locations(lat, lon, radius, precision, locations_data, location_type)
    print_colored_message(f'Total {len(nearby_locations)} {location_type} within {radius}m of current coordinate ({lat}, {lon}):\n', nearby_locations)
    elapsed_time = time.time() - start_time
    print_colored_message('\nTotal execution time #6:', f'{elapsed_time} seconds', colored.red)
    puts('\n\n')


#MAIN 

if __name__ == "__main__":
    lat, lon, precision = 37.422131, -122.084801, 6

    display_encode_function(lat, lon, precision)
    display_decode_function('9q9hvu')
    display_nearby_geohashes(lat, lon, 2000, precision)
    display_geohashes_distance('9q9hvu', lat, lon, 2000, precision) #Auxiliary function
    display_locations_data(50, lat, lon, 6) #Auxiliary function
    display_nearby_locations(lat, lon, 2000, 6, 'cafe')


