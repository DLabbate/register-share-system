import socket
import sys      
import time
import pickle

class Server:

    def __init__(self):
        self.sock = None #socket
        self.host = None
        self.port = 8888

    def createSocket(self):
        try:
            # printing the IP address of the host
            print(socket.gethostbyname(socket.gethostname()))
            
            # configure host IP address
            self.host = socket.gethostbyname(socket.gethostname())
            
            # create the socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print('Socket created')

        except OSError as msg:
            print('Failed to create socket. Error Code : ' + str(msg))
            sys.exit()

    def bindSocket(self):
        try:
            self.sock.bind((self.host, self.port))
            print('Socket bind complete')
        except OSError as msg:
            print('Bind failed. Error Code : ' + str(msg))
            sys.exit()

            

    def run(self):
        while (True):
            d = self.sock.recvfrom(1024)
            data = d[0]
            addr = d[1]
            if not data:
                break

            reply = bytes('OK...' + str(data), "utf-8")

            self.sock.sendto(data, addr)
            print('Message[' + str(addr) + ']: ' + str(data.decode("utf-8")))

    