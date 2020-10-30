from server import Server
server = Server()
server.createSocket()
server.bindSocket()
server.run()