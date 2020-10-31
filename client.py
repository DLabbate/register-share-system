import socket
import sys      # for exit
import time
import pickle

class Client:

    def __init__(self):
        self.s = None   #client socket
        self.hostA = ''
        self.portA = 0
        self.hostB = ''
        self.portB = 0
        self.currentServer = ''
        self.currentRequestNum = 0

    def updateServers(self,hostA,portA,hostB,portB):
        self.hostA = hostA
        self.portA = portA
        self.hostB = hostB
        self.portB = portB

    #This function creates a socket for the CLIENT    
    def createSocket(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except OSError as msg:
            print('Failed to create socket')
            sys.exit()
    
    def run(self):
        while(True):
            msg = bytes("Hello", "utf-8")

            try:
                time.sleep(1)
                self.s.sendto(msg, (self.hostA, self.portA))
                d = self.s.recvfrom(1024)
                reply = d[0]
                addr = d[1]
                #clientAddress = self.s.getsockname()
                #print(str(clientAddress[1]))
                #print(socket.gethostbyname(socket.gethostname()))
                print('Server reply : ' + str(reply.decode("utf-8")))

            except OSError as msg:
                print('Error' + str(msg))
                sys.exit()

    def initialize(self):
        msg = bytes("New Client!","utf-8")
        try:
            self.s.sendto(msg, (self.hostA, self.portA))
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()


    def sendRegister(self,name):
        # Create message object to send to server through pickle
        self.currentRequestNum += 1
        #print(str(self.s.getsockname()))
        clientAddress = self.s.getsockname()
        clientIP = socket.gethostbyname(socket.gethostname())
        clientPort = clientAddress[1]
        msg = {"TYPE":"REGISTER","RQ#":self.currentRequestNum, "NAME":name,"IP":clientIP,"Port":clientPort}
        print(msg)

        
