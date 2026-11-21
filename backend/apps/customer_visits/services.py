
import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates in meters.
    Uses the Haversine formula.
    """

    earth_radius = 6371000

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    latitude_difference = lat2 - lat1
    longitude_difference = lon2 - lon1

    a = (
        math.sin(latitude_difference / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(longitude_difference / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = earth_radius * c

    return round(distance, 2)
