# hgeoip2==2.5.0ttps://github.com/mitsuhiko/python-geoip
# https://pythonhosted.org/python-geoip/
# python-geoip-geolite2==2015.303


from geoip import geolite2 # 不再支持Python3
# https://stackoverflow.com/questions/32575666/python-geoip-does-not-work-on-python3-4



def get_location(ip):
    if ip is None:
        return "Unknown"

    match = geolite2.lookup(ip)
    if match is None:
        return "Unknown"

    return match.country


