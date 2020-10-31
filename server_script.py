from server import Server
from db_handler import DBHandler

server = Server()
server.createSocket()
server.bindSocket()

db_handler = DBHandler()
db_handler.addUser("domenic","192.192.192","8888")

server.run()