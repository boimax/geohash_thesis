# Geohash_Thesis

This repo will provide a detailed implementation of the geohashing system. This includes encoding and decoding geohashes, along with a function designed to identify nearby locations based on the geohashes.

# GeoHash Utilities

## Overview

This module provides utilities for working with geohashes. Geohashing encodes geographic coordinates (latitude and longitude) into a concise string.

## Functions

### 1. encode

Encodes a latitude and longitude into a geohash string.

- **Parameters**: `lat`, `lon`, `precision` (optional)
- **Returns**: Geohash string

![Encode_input](./images/encode_function_input.png)
![Encode](./images/encode_function_result.png)

### 2. decode

Decodes a geohash into its approximate central point.

- **Parameters**: `geohash`
- **Returns**: Dictionary with latitude and longitude

![Decode_input](./images/decode_function_input.png)
![Decode](./images/decode_function_result.png)

### 3. get_nearby_geohashes

Calculates geohashes within a specified radius from a point.

- **Parameters**: `latitude`, `longitude`, `radius`, `precision`
- **Returns**: List of geohashes

![Nearby Geohashes](./images/nearby_geohashes.png)
![Get Nearby Geohashes Result Input](./images/get_nearby_geohashes_input.png)
![Get Nearby Geohashes Result](./images/get_nearby_geohashes_result.png)

### 4. geohash_distance

Computes the distance between two geohashes.

- **Parameters**: `geohash1`, `geohash2`

![Distance Between 2 Geohashes Input](./images/geohashes_distance_input.png)
![Distance Between 2 Geohashes](./images/geohashes_distance_result.png)

### 5. generate_locations_data

Produces mock location data around a central point.

- **Parameters**: `size`, `central_lat`, `central_lon`, `precision`
- **Returns**: List of mock locations

![Generate Fake Locations Data Input](./images/generate_fake_locations_data_input.png)
![Generate Fake Locations Data](./images/generate_fake_locations_data_result.png)

### 6. get_nearby_locations

Retrieves locations within a specified radius from a point.

- **Parameters**: `lat`, `lon`, `radius`, `precision`, `locations_data`, `location_type` (optional)
- **Returns**: List of nearby locations

![Get Nearby Locations Result Input](./images/get_nearby_locations_input.png)
![Get Nearby Locations Result](./images/get_nearby_locations_result.png)

## Dependencies

- `math`
- `time`
- `argparse`
- `clint.textui`
- `random`
- `faker`

## Usage

Execute this module by running the command below in your terminal:

```bash
python <module_name>.py
```
