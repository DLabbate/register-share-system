from server import Server
from db_handler import DBHandler
import sys

status = str(sys.argv[1])
port = int(sys.argv[2])
host_backup = str(sys.argv[3])
port_backup = int(sys.argv[4])


server = Server()
server.server_initialize(status, port, host_backup, port_backup)
server.initialize_log_file()
server.create_socket()
server.bind_socket()
server.run()