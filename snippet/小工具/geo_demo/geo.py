# 安装
# geoip2==2.5.0
# official MaxMind geoip2 package
# https://geoip2.readthedocs.io/en/latest/#database-example


import os

import geoip2.database

# 项目根目录
Base_DIR = os.path.dirname(os.path.abspath(__file__))

Base_DIR1 = os.path.dirname(__file__)

print (Base_DIR)
print (Base_DIR1)


geoip_reader = geoip2.database.Reader(os.path.join(Base_DIR, 'GeoIP2-City.mmdb'))

resp = geoip_reader.city('111.247.233.232')
reg_country = resp.country.name,
reg_state = resp.subdivisions.most_specific.name,
reg_city = resp.city.name

print(reg_country, reg_state, reg_city)
