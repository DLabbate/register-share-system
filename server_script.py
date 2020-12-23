from server import Server
from db_handler import DBHandler
import sys

status = str(sys.argv[1]) # Argument for whether the server is initialized as "active" or "inactive"
port = int(sys.argv[2]) # Argument for where we would like to set the Port of this server
host_backup = str(sys.argv[3]) # Argument for IP of the other server
port_backup = int(sys.argv[4]) # Argument for Port of the other server

# This script creates a server object
# The server object initializes the log file, and other information (passed through command line)
server = Server()
server.initialize_log_file()
server.server_initialize(status, port, host_backup, port_backup)
server.create_socket()
server.bind_socket()
server.run()