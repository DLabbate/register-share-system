import socket
import sys      
import time
import pickle
import ast
import json
from db_handler import DBHandler
import utils

class Server:

    def __init__(self):
        self.sock = None #socket
        self.host = None
        self.port = 8888

    def create_socket(self):
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

    def bind_socket(self):
        try:
            self.sock.bind((self.host, self.port))
            print('Socket bind complete')
        except OSError as msg:
            print('Bind failed. Error Code : ' + str(msg))
            sys.exit()

    # Process message and call appropriate function
    def handle_client(self,message_dict,address):
        message_type = message_dict["TYPE"]

        print('Message[' + str(address) + ']: ' + str(message_dict))
        if (message_type == "INITIALIZATION"):
            pass

        elif (message_type == "REGISTER"):
            db = DBHandler()
            success = db.add_user(message_dict["NAME"],message_dict["IP"],message_dict["PORT"])

            if (success):
                msg = {"TYPE":"REGISTER-SUCCESS","RQ#":message_dict["RQ#"]}
                self.sock.sendto(utils.serialize(msg), address)
            else:
                msg = {"TYPE":"REGISTER-DENIED","RQ#":message_dict["RQ#"]}
                self.sock.sendto(utils.serialize(msg), address)

        elif (message_type == "DE-REGISTER"):
            db = DBHandler()
            success = db.remove_user(message_dict["NAME"])

            if (success):
                msg = {"TYPE":"DE-REGISTER-SUCCESS","RQ#":message_dict["RQ#"]}
                self.sock.sendto(utils.serialize(msg), address)
            else:
                msg = {"TYPE":"DE-REGISTER-DENIED","RQ#":message_dict["RQ#"]}
                self.sock.sendto(utils.serialize(msg), address)


        elif (message_type == "UPDATE-SOCKET"):
            db = DBHandler()
            success = db.update_socket(message_dict["NAME"], message_dict["IP"], message_dict["PORT"])

            if (success):
                msg = {"TYPE":"UPDATE-SOCKET-SUCCESS","RQ#":message_dict["RQ#"]}
                self.sock.sendto(utils.serialize(msg), address)
            else:
                msg = {"TYPE":"DE-REGISTER-DENIED","RQ#":message_dict["RQ#"]}
                self.sock.sendto(utils.serialize(msg), address)
            
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
            client_data = pickle.loads(data) #DESERIALIZED DATA
            client_dict = ''
            
            #handleclient(clientData,address)

            try:
                client_dict = ast.literal_eval(str(client_data))
                #print(clientDict["TYPE"])
            except:
                print("ERROR CONVERTING MESSAGE TO DICTIONARY")

            self.handle_client(client_dict,addr)

            #clientDict = pickle.loads(data)
            #print(clientDict["TYPE"])
            #print(type(clientData))
            #clientDict = ast.literal_eval(clientData)
            #print(clientDict["TYPE"])
            #reply = pickle.dumps(data) #SERIALIZED

            #self.sock.sendto(data, addr)
            
            #print('Message[' + str(addr) + ']: ' + str(clientData))

    