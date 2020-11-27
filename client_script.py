import sys
import socket
from client import Client

host_a = str(sys.argv[1]) # Argument for IP of Server A
port_a = int(sys.argv[2]) # Argument for Port of Server A
host_b = str(sys.argv[3]) # Argument for IP of Server B
port_b = int(sys.argv[4]) # Argument for Port of Server B

# This script creates a client object
# The client object initializes the log file, and other information (passed through command line)
client = Client()
client.create_socket()
client.update_servers(host_a,port_a,host_b,port_b)
client.initialize_log_file()
client.initialize()
client.run()