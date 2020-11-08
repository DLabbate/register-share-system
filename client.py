import socket
import sys      # for exit
import time
import pickle
import json
import utils
import threading
import datetime

class Client:

    def __init__(self):
        self.client_socket = None   #client socket
        self.host_a = ''
        self.port_a = 0
        self.host_b = ''
        self.port_b = 0
        self.current_server = ''
        self.current_request_num = 0
        self.log_file_path = '' # make a new log file for the client
        self.semaphore = threading.Semaphore(1)
        #self.log_file = 0
        #self.currentRequests = [] # requests that haven't been handled e.g. [0,1]
        
    def initialize_log_file(self):
        date_str_temp = str(datetime.datetime.now())
        date_str = date_str_temp.replace(" ","-") #This replaces spaces in the file path with a '-'
        date_str = date_str.replace(".","-") #This replaces spaces in the file path with a '-'
        date_str = date_str.replace(":","-") #This replaces spaces in the file path with a '-'
        self.log_file_path = "logs/" + "client-" + date_str + ".txt"

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

    def write_to_log(self,msg):
        self.semaphore.acquire()
        log_file = open(self.log_file_path,"a+")
        log_file.write(str(msg))
        log_file.close()
        self.semaphore.release()
    
    def initialize(self):
        msg = {"TYPE":"INITIALIZATION","MESSAGE":"New Client!"}
        msg_serialized = utils.serialize(msg)

        try:
            self.client_socket.sendto(msg_serialized, (self.host_a, self.port_a))
            self.write_to_log("MESSAGE SENT " + str(msg) + "\n")
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
        self.write_to_log("MESSAGE SENT " + str(msg) + "\n")
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
                self.write_to_log("MESSAGE RECEIVED " + str(msg_dict) + "\n")
                #print(str(msg_dict))

        except:
            print("RECEIVED AN INCORRECT RQ#!")

    

    def menu(self):
        while(True):
            print ("[Enter 1 to register]\n[Enter 2 to de-register]\n[Enter 3 to update socket#]\n[Enter 4 to update your subjects of interest]\n[Enter 5 to publish messages]\n[Enter anything else to exit]")
            command = input()
            if (command == '1'):
                print("Enter name to register:")
                name = input()
                self.send_register(name)
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

    def listen(self):
        while True:
            msg = self.client_socket.recvfrom(1024)
            # WE NEED TO MAKE SURE THAT WE RECEIVE THE APPROPRIATE RQ# (FAULT TOLERANCE)
            self.handle_response(msg)
            #date = datetime.datetime.now()
            #print("client " + str(date))

        
    def run(self):
        menu_thread = threading.Thread(target = self.menu)
        menu_thread.start()

        listening_thread = threading.Thread(target = self.listen)
        listening_thread.start()

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
        
        #print(str(threading.active_count()))