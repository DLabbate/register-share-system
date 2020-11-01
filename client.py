import socket
import sys      # for exit
import time
import pickle
import json
import utils

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
    
    def initialize(self):
        msg = pickle.dumps({"TYPE":"INITIALIZATION","MESSAGE":"New Client!"})

        try:
            self.s.sendto(msg, (self.hostA, self.portA))
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def sendRegister(self,name):
        self.currentRequestNum += 1
        clientAddress = self.s.getsockname()
        clientIP = socket.gethostbyname(socket.gethostname())
        clientPort = clientAddress[1]
        # Create message object to send to server through pickle
        msg = {"TYPE":"REGISTER","RQ#":self.currentRequestNum,"NAME":name,"IP":clientIP,"PORT":clientPort}
        msg_serialized = pickle.dumps(msg)
        #print(msg)

        try:
            self.s.sendto(msg_serialized, (self.hostA, self.portA))
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()
    
    def handle_response(self,msg):
        msg = (self.s.recvfrom(1024))[0]

        # WE NEED TO MAKE SURE THAT WE RECEIVE THE APPROPRIATE RQ# (FAULT TOLERANCE)
        try:
            msg = utils.deserialize(msg)
            msg_dict = utils.convert_to_dict(msg)

            if (msg_dict["RQ#"] == str(self.currentRequestNum)):
                print(str(msg_dict))

        except:
            print("RECEIVED AN INCORRECT RQ#!")


    def menu(self):
        print ("[Enter 1 to register]\n[Enter 2 to de-register]\n[Enter 3 to update socket#]\n[Enter 4 to update your subjects of interest]\n[Enter 5 to publish messages]\n[Enter anything else to exit]")
        command = input()
        if (command == '1'):
            print("Enter name to register:")
            name = input()
            self.sendRegister(name)
            msg = self.s.recvfrom(1024)

            # WE NEED TO MAKE SURE THAT WE RECEIVE THE APPROPRIATE RQ# (FAULT TOLERANCE)
            self.handle_response(msg)

        elif (command == '2'):
            print("Enter name to de-register:")
            name = input()
        elif (command == '3'):
            # TO DO
            print('Option 3')
        elif (command == '4'):
            print("Enter new list of subjects (e.g. sports,AI,...)")
        elif (command == '5'):
            print("Enter your message")
        else:
            sys.exit()
            
    def run(self):
        while(True):
            #msg = pickle.dumps({"TYPE":"INITIALIZATION","MESSAGE":"Hello"})

            # try:
            #     time.sleep(1)
            #     self.s.sendto(msg, (self.hostA, self.portA))
            #     d = self.s.recvfrom(1024)
            #     reply = d[0]
            #     addr = d[1]
            #     print('Server reply : ' + str(pickle.loads(reply)))

            # except OSError as msg:
            #     print('Error' + str(msg))
            #     sys.exit()

            self.menu()

            