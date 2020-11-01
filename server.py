import socket
import sys      
import time
import pickle
import ast
import json
from db_handler import DBHandler

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

    # Process message and call appropriate function
    def handleClient(self,message_dict,address):
        message_type = message_dict["TYPE"]

        print('Message[' + str(address) + ']: ' + str(message_dict))
        if (message_type == "INITIALIZATION"):
            pass
        elif (message_type == "REGISTER"):
            db = DBHandler()
            db.addUser(message_dict["NAME"],message_dict["IP"],message_dict["PORT"])
        elif (message_type == "DE-REGISTER"):
            pass
        elif (message_type == "UPDATE-SOCKET"):
            pass
        elif (message_type == "SUBJECTS"):
            pass
        elif (message_type == "PUBLISH"):
            pass
        else:
            pass

    def run(self):
        while (True):
            d = self.sock.recvfrom(1024)
            data = d[0]
            addr = d[1]
            if not data:
                break


            #reply = bytes('OK...' + str(data), "utf-8")
            clientData = pickle.loads(data) #DESERIALIZED DATA
            clientDict = ''
            
            #handleclient(clientData,address)

            try:
                clientDict = ast.literal_eval(str(clientData))
                print(clientDict["TYPE"])
            except:
                print("ERROR CONVERTING MESSAGE TO DICTIONARY")

            self.handleClient(clientDict,addr)

            #clientDict = pickle.loads(data)
            #print(clientDict["TYPE"])
            #print(type(clientData))
            #clientDict = ast.literal_eval(clientData)
            #print(clientDict["TYPE"])
            #reply = pickle.dumps(data) #SERIALIZED

            self.sock.sendto(data, addr)
            
            #print('Message[' + str(addr) + ']: ' + str(clientData))

    