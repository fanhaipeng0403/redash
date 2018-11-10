# 安装
# geoip2==2.5.0


import os
import geoip2.database
geoFile = os.path.dirname(__file__) + '/GeoIP2-city.mmdb'
print(geoFile)
print(os.path.dirname(__file__))
print(os.path.dirname(os.path.abspath(__file__)))
print(os.path.abspath(__file__))

geoip_reader = geoip2.database.Reader(geoFile)
resp = geoip_reader.city('111.247.233.232')
reg_country = resp.country.name,
reg_state = resp.subdivisions.most_specific.name,
reg_city = resp.city.name

print(reg_country, reg_state, reg_city)
