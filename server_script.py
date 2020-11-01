from server import Server
from db_handler import DBHandler

server = Server()
server.createSocket()
server.bindSocket()
server.run()