from meetup_point.models import Address


def calculate_midpoint(lat1, lng1, lat2, lng2):
    """
    Calculate the midpoint of a line segment defined by two points (lat1, lng1) and (lat2, lng2).
    
    Parameters:
    lat1, lng1: Coordinates of the first point.
    lat2, lng2: Coordinates of the second point.

    Returns:
    A tuple representing the midpoint (lat, lng).
    """
    midpoint_lat = (lat1 + lat2) / 2
    midpoint_lng = (lng1 + lng2) / 2
    return (midpoint_lat, midpoint_lng)

def saveAddress(data):
    new_address = Address(
        street=data.get("street"),
        city=data.get("city"),
        state=data.get("state"),
        zip_code=data.get("zipcode"),
    )
    if new_address.verify_address():
        print("Address is valid -- saving to database")
        new_address.save()
        return new_address
    else:
        print("Address is invalid -- not saving to database")