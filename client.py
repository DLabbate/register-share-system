import socket
import sys      # for exit
import time
import pickle
import json
import utils

class Client:

    def __init__(self):
        self.client_socket = None   #client socket
        self.host_a = ''
        self.port_a = 0
        self.host_b = ''
        self.port_b = 0
        self.current_server = ''
        self.current_request_num = 0
        #self.currentRequests = [] # requests that haven't been handled e.g. [0,1]

    def update_servers(self,host_a,port_a,host_b,port_b):
        self.host_a = host_a
        self.port_a = port_a
        self.host_b = host_b
        self.port_b = port_b

    #This function creates a socket for the CLIENT    
    def create_socket(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except OSError as msg:
            print('Failed to create socket')
            sys.exit()
    
    def initialize(self):
        msg = pickle.dumps({"TYPE":"INITIALIZATION","MESSAGE":"New Client!"})

        try:
            self.client_socket.sendto(msg, (self.host_a, self.port_a))
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def send_register(self,name):
        self.current_request_num += 1
        cient_address = self.client_socket.getsockname()
        client_ip = socket.gethostbyname(socket.gethostname())
        client_port = cient_address[1]
        # Create message object to send to server through pickle
        msg = {"TYPE":"REGISTER","RQ#":self.current_request_num,"NAME":name,"IP":client_ip,"PORT":client_port}
        msg_serialized = pickle.dumps(msg)
        #print(msg)

        try:
            self.client_socket.sendto(msg_serialized, (self.host_a, self.port_a))
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()
    
    def handle_response(self,msg):
        msg = (self.client_socket.recvfrom(1024))[0]

        # WE NEED TO MAKE SURE THAT WE RECEIVE THE APPROPRIATE RQ# (FAULT TOLERANCE)
        try:
            msg = utils.deserialize(msg)
            msg_dict = utils.convert_to_dict(msg)

            if (str(msg_dict["RQ#"]) == str(self.current_request_num)):
                print(str(msg_dict))

        except:
            print("RECEIVED AN INCORRECT RQ#!")


    def menu(self):
        print ("[Enter 1 to register]\n[Enter 2 to de-register]\n[Enter 3 to update socket#]\n[Enter 4 to update your subjects of interest]\n[Enter 5 to publish messages]\n[Enter anything else to exit]")
        command = input()
        if (command == '1'):
            print("Enter name to register:")
            name = input()
            self.send_register(name)
            msg = self.client_socket.recvfrom(1024)

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

            