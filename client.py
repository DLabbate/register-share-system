import socket
import sys      # for exit
import pickle
import utils
import threading
import datetime

class Client:

    def __init__(self):
        self.client_socket = None # client socket
        self.host_a = ''
        self.port_a = 0
        self.host_b = ''
        self.port_b = 0
        self.active_a = True # This will be True when server a is active, and False when server b is active
        self.current_request_num = 1
        self.log_file_path = '' # make a new log file for the client
        self.semaphore_log = threading.Semaphore(1) # Semaphore for writing/reading to the log
        self.semaphore_server = threading.Semaphore(1) # Semaphore to protect "active_a" variable
        self.current_requests = [] # List of requests that have been sent but have not yet been handled e.g. [0,1]
        
    def initialize_log_file(self):
        date_str_temp = str(datetime.datetime.now())
        date_str = date_str_temp.replace(" ","-") #This replaces spaces in the file path with a '-'
        date_str = date_str.replace(".","-") #This replaces spaces in the file path with a '-'
        date_str = date_str.replace(":","-") #This replaces spaces in the file path with a '-'
        self.log_file_path = "logs/client/" + "client-" + date_str + ".txt"
        self.write_to_log("----- Client Log -----" + "\n")

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
            print('Failed to create socket' + str(msg))
            sys.exit()

    def write_to_log(self,msg):
        self.semaphore_log.acquire()
        log_file = open(self.log_file_path,"a+")
        log_file.write(str(msg))
        log_file.close()
        self.semaphore_log.release()
    
    def initialize(self):
        msg = {"TYPE":"INITIALIZATION","MESSAGE":"New Client!"}
        msg_serialized = utils.serialize(msg)

        try:
            self.client_socket.sendto(msg_serialized, (self.host_a, self.port_a))
            self.client_socket.sendto(msg_serialized, (self.host_b, self.port_b))

            # Write client socket info to the log
            self.write_to_log(str(socket.gethostbyname(socket.gethostname())) + "\n")
            self.write_to_log(str(self.client_socket.getsockname()[1]) + "\n")
            self.write_to_log('Client socket created ' + "\n")

            self.write_to_log("MESSAGE SENT\t\t " + str(msg) + "\n")
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def send_to_current_server(self,msg_serialized):
        self.semaphore_server.acquire()
        try:
            if (self.active_a == True):
                self.client_socket.sendto(msg_serialized, (self.host_a, self.port_a))
            else:
                self.client_socket.sendto(msg_serialized, (self.host_b, self.port_b))

        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()
        
        finally:
            self.semaphore_server.release()

    def send_register(self,name):
        cient_address = self.client_socket.getsockname()
        client_ip = socket.gethostbyname(socket.gethostname())
        client_port = cient_address[1]
        # Create message object to send to server through pickle
        msg = {"TYPE":"REGISTER","RQ#":self.current_request_num,"NAME":name,"IP":client_ip,"PORT":client_port}
        self.write_to_log("MESSAGE SENT\t\t " + str(msg) + "\n")
        msg_serialized = pickle.dumps(msg)

        try:
            self.client_socket.sendto(msg_serialized, (self.host_a, self.port_a))
            self.client_socket.sendto(msg_serialized, (self.host_b, self.port_b))
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def send_deregister(self,name):
        # Create message object to send to server through pickle
        msg = {"TYPE":"DE-REGISTER","RQ#":self.current_request_num,"NAME":name}
        self.write_to_log("MESSAGE SENT\t\t " + str(msg) + "\n")
        msg_serialized = pickle.dumps(msg)

        try:
            self.send_to_current_server(msg_serialized)
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def send_update(self,name):
        cient_address = self.client_socket.getsockname()
        client_ip = socket.gethostbyname(socket.gethostname())
        client_port = cient_address[1]
        # Create message object to send to server through pickle
        msg = {"TYPE":"UPDATE-SOCKET","RQ#":self.current_request_num,"NAME":name,"IP":client_ip,"PORT":client_port}
        self.write_to_log("MESSAGE SENT\t\t " + str(msg) + "\n")
        msg_serialized = pickle.dumps(msg)

        try:
            self.send_to_current_server(msg_serialized)
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def send_update_subjects(self, name, subjects):
        # Create message object to send to server through pickle
        msg = {"TYPE": "SUBJECTS", "RQ#": self.current_request_num, "NAME": name, "SUBJECT-LIST": subjects}
        self.write_to_log("MESSAGE SENT\t\t " + str(msg) + "\n")
        msg_serialized = pickle.dumps(msg)

        try:
            self.send_to_current_server(msg_serialized)
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def send_publish (self, name, subject, text):
        # Create message object to send to server through pickle
        msg = {"TYPE": "PUBLISH", "RQ#": self.current_request_num, "NAME": name, "SUBJECT": subject, "TEXT":text}
        self.write_to_log("MESSAGE SENT\t\t " + str(msg) + "\n")
        msg_serialized = pickle.dumps(msg)

        try:
            self.send_to_current_server(msg_serialized)
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def send_retrieve_texts(self, name):
        # Create message object to send to server through pickle
        msg = {"TYPE": "RETRIEVE-TEXTS", "RQ#": self.current_request_num, "NAME": name}
        self.write_to_log("MESSAGE SENT\t\t " + str(msg) + "\n")
        msg_serialized = utils.serialize(msg)

        try:
            self.send_to_current_server(msg_serialized)
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def send_end_connection(self):
        cient_address = self.client_socket.getsockname()
        client_ip = socket.gethostbyname(socket.gethostname())
        client_port = cient_address[1]
        # Create message object to send to server through pickle
        msg = {"TYPE": "END-CONNECTION", "RQ#": self.current_request_num, "IP": client_ip, "PORT": client_port}
        self.write_to_log("MESSAGE SENT\t\t " + str(msg) + "\n")
        msg_serialized = pickle.dumps(msg)

        try:
            self.client_socket.sendto(msg_serialized, (self.host_a, self.port_a))
            self.client_socket.sendto(msg_serialized, (self.host_b, self.port_b))
        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()

    def check_valid_request(self,rq):
        is_valid = False
        if rq in self.current_requests:
            is_valid = True
        return is_valid

    def handle_response(self,msg):
        msg = (msg)[0]
        
        # WE NEED TO MAKE SURE THAT WE RECEIVE THE APPROPRIATE RQ# (FAULT TOLERANCE)
        try:
            msg = utils.deserialize(msg)
            msg_dict = utils.convert(msg)
        except:
            self.write_to_log("FAILED TO DESERIALIZE RECEIVED MESSAGE!")

        try:
            # If there is an RQ# in the message, we check that it is valid
            if "RQ#" in msg_dict:
                if ( self.check_valid_request(int(msg_dict["RQ#"])) ):
                
                    self.write_to_log("MESSAGE RECEIVED\t " + str(msg_dict) + "\n")
                    self.current_requests.remove((int(msg_dict["RQ#"])))
                    
                    if "RETRIEVE-SUCCESS" == msg_dict.get("TYPE"):

                        posts_list = utils.convert(msg_dict["POSTS"])

                        for posts in posts_list:
                            self.write_to_log(str(posts) + "\n")

                else:
                    self.write_to_log("RECEIVED AN INVALID RQ#!")
            else:
                # In this branch, the message does not have a key for RQ#
                # This might be a message coming from the server to inform the client that the server location has changed

                # If we get a CHANGE-SERVER message, we know the active server has switched
                if "CHANGE-SERVER" == msg_dict.get("TYPE"):
                    self.semaphore_server.acquire()
                    try:
                        self.active_a = not self.active_a
                        self.write_to_log("MESSAGE RECEIVED\t " + str(msg_dict) + "\n")
                    finally:
                        self.semaphore_server.release()
                
                # If we receive this message, we should update the new IP and PORT
                # of server A or server B (depending on which one sent the message)
                elif "UPDATE-SERVER" == msg_dict.get("TYPE"):
                    self.semaphore_server.acquire()
                    try:
                        if ("A" == msg_dict.get("SERVER-TAG")):
                            self.host_a = msg_dict.get("IP")
                            self.port_a = msg_dict.get("PORT")
                        elif ("B" == msg_dict.get("SERVER-TAG")):
                            self.host_b = msg_dict.get("IP")
                            self.port_b = msg_dict.get("PORT")
                        self.write_to_log("MESSAGE RECEIVED\t " + str(msg_dict) + "\n")
                    finally:
                        self.semaphore_server.release()
                
                # This message indicates initialization success and also informs the client
                # about which server is the active one ("A" or "B")
                elif "INITIALIZATION-SUCCESS" == msg_dict.get("TYPE"):
                    self.semaphore_server.acquire()
                    try:
                        if "A" == msg_dict.get("SERVER-TAG"):
                            self.active_a = True
                        elif "B" == msg_dict.get("SERVER-TAG"):
                            self.active_a = False
                        self.write_to_log("MESSAGE RECEIVED\t " + str(msg_dict) + "\n")
                    finally:
                        self.semaphore_server.release()

        except:
            self.write_to_log("ERROR READING MESSAGE!")

    def menu(self):
        while(True):
            print ("[Enter 1 to register]\n[Enter 2 to de-register]\n[Enter 3 to update socket#]\n[Enter 4 to update your subjects of interest]\n"
                   "[Enter 5 to publish text]\n[Enter 6 to retrieve texts]\n[Enter e to exit]")
            command = input()
            self.current_requests.append(self.current_request_num)
            if (command == '1'):
                name = input("Enter name to register: ")
                self.send_register(name)
            elif (command == '2'):
                name = input("Enter name to de-register: ")
                self.send_deregister(name)
            elif (command == '3'):
                name = input ("Enter name to update socket#: ")
                self.send_update(name)
            elif (command == '4'):
                name = input ("Enter name to update subjects: ")
                subjects = input ("Enter new list of subjects (e.g. sports,AI,...): ")
                self.send_update_subjects(name,subjects)
            elif (command == '5'):
                name = input("Enter name to publish a text: ")
                subject = input ("Enter subject of the text: ")
                text = input ("Enter text: ")
                self.send_publish(name,subject,text)
            elif (command == '6'):
                name = input ("Enter name to retrieve texts on your subjects: ")
                self.send_retrieve_texts(name)
            elif (command == 'e'):
                self.send_end_connection()
                sys.exit()
            else:
                pass
            self.current_request_num += 1

    def listen(self):
        while True:
            msg = self.client_socket.recvfrom(1024)
            self.handle_response(msg)
    
    # This function creates one thread for the menu, and one for listening to incoming messages from the servers
    def run(self):
        menu_thread = threading.Thread(target = self.menu)
        menu_thread.start()

        listening_thread = threading.Thread(target = self.listen)
        listening_thread.start()