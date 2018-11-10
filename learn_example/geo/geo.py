from geoip import geolite2


def get_location(ip):
    if ip is None:
        return "Unknown"

    match = geolite2.lookup(ip)
    if match is None:
        return "Unknown"

    return match.country

print (get_location(b'111.197.244.232'))
