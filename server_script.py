from server import Server
from db_handler import DBHandler

server = Server()
server.initialize_log_file()
server.create_socket()
server.bind_socket()
server.run()