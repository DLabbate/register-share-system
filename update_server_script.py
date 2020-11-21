from server import Server
from db_handler import DBHandler
import sys

port = int(sys.argv[1])
host_a = str(sys.argv[2])
port_a = int(sys.argv[3])
host_b = str(sys.argv[4])
port_b = int(sys.argv[5])

server = Server()
server.initialize_log_file()

# Set the port we want the new server to run on
server.new_server_initialize(port)

# Create and bind socket
server.create_socket()
server.bind_socket()

# Send the "UPDATE-SERVER" message to the servers that are currently running
server.update_server(host_a,port_a,host_b,port_b)

server.run()