import socket


# 局域网ip地址
ips = socket.gethostbyname_ex(socket.gethostname())[-1]

# 主机地址
host_name = socket.gethostname()
