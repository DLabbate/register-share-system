import sys
import socket
from client import Client

host_a = str(sys.argv[1])
port_a = int(sys.argv[2])
host_b = str(sys.argv[3])
port_b = int(sys.argv[4])

client = Client()
client.create_socket()
client.update_servers(host_a,port_a,host_b,port_b)
client.initialize()
client.run()