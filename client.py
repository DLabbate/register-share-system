import socket   # for sockets
import sys      # for exit
import time
import pickle

class Client:

    def __init__(self):
        self.s = None
        self.hostA = ''
        self.portA = 0
        self.hostB = ''
        self.portB = 0
        self.currentServer = ''

    def updateServers(self,hostA,portA,hostB,portB):
        self.hostA = hostA
        self.portA = portA
        self.hostB = hostB
        self.portB = portB
        
    def createSocket(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except OSError as msg:
            print('Failed to create socket')
            sys.exit()
    
    def run(self):
        while(True):
            msg = bytes("Hello!", "utf-8")

            try:
                time.sleep(1)
                self.s.sendto(msg, (self.hostA, self.portA))
                d = self.s.recvfrom(1024)
                reply = d[0]
                addr = d[1]
                print('Server reply : ' + str(reply.decode("utf-8")))

            except OSError as msg:
                print('Error' + str(msg))
                sys.exit()