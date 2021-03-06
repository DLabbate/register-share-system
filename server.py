import socket
import sys      
import time
import pickle
import ast
import datetime
import threading
from db_handler import DBHandler
from private.connection import connection_string_1, connection_string_2
import utils

class Server:

    def __init__(self):
        self.sock = None # socket
        self.host = None
        self.port = 8888
        self.log_file_path = ''
        self.active = False # Indicates if the server is active or not
        self.host_backup = None # Reference to the IP of the other server
        self.port_backup = 0 # Reference to the Port of the other server
        self.semaphore = threading.Semaphore(1) # Semaphore to protect the critical section ("active" variable)
        self.client_list = [] # This is a list of addresses of all the connected clients
        self.db = None # Reference to MongoDB database
        self.server_tag = "B" # This is simply a tag for the server ("A" or "B")

    def change_server(self,address):
        msg = {"TYPE":"CHANGE-SERVER","IP":self.host,"PORT":self.port}
        msg_serialized = utils.serialize(msg)
        self.sock.sendto(msg_serialized,address)

        # Send this message to the other server
        self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t '  + str(msg))

        # Also send this message to all the connected clients
        try:
            for i in self.client_list:
                self.sock.sendto(msg_serialized,i)
                self.write_to_log('MESSAGE SENT\t\t [' + str(i) + ']:\t '  + str(msg))
        except:
            print("ERROR SENDING CHANGE-SERVER MESSAGE TO ALL CLIENTS")

    def gain_control(self):
        self.semaphore.acquire()
        self.active = True
        self.semaphore.release()

    def start_timer(self):
        # Set the timer to a duration of 120 seconds (2 minutes)
        endtime = time.time() + 120

        # Busy wait
        while time.time() < endtime:
            pass

        self.semaphore.acquire()
        self.active = False
        self.semaphore.release()

        # We should now send a message to the other server to inform it to take
        self.change_server((self.host_backup,self.port_backup))
        
    
    def start_timer_thread(self):
        timer_thread = threading.Thread(target=self.start_timer)
        timer_thread.start()

    # This function is called the first time we initialize server A or server B (1 active & 1 inactive)
    def server_initialize(self, status,port, host_backup, port_backup):
        if (status == 'active'):
            self.server_tag = "A"
            self.active = True
            self.db = DBHandler(connection_string_1,"register-share-system-1")
            self.start_timer_thread()
        else:
            self.server_tag = "B"
            self.db = DBHandler(connection_string_2,"register-share-system-2")
            
        self.port = port
        self.host_backup = host_backup
        self.port_backup = port_backup

    # This function is called when there are two servers already in the system, but we want to
    # change the IP/Port of the inactive server
    def new_server_initialize(self,port):
        self.port = port

    # This function sends an "UPDATE-SERVER" message to both servers that are already in the system
    # We refer to these as server A and server B
    def update_server(self,host_a,port_a,host_b,port_b):
        msg = {"TYPE":"UPDATE-SERVER","IP":self.host,"PORT":self.port}
        msg_serialized = utils.serialize(msg)
        try:
            self.sock.sendto(msg_serialized,(host_a,port_a))
            self.sock.sendto(msg_serialized,(host_b,port_b))
        except:
            print("FAILED TO SEND UPDATE-SERVER MESSAGE")

    def write_to_log(self,msg):
        log_file = open(self.log_file_path,"a+")
        log_file.write(str(msg)+"\n")
        log_file.close()

    def initialize_log_file(self):
        date_str_temp = str(datetime.datetime.now())
        date_str = date_str_temp.replace(" ", "-")  # This replaces spaces in the file path with a '-'
        date_str = date_str.replace(".", "-") # This replaces spaces in the file path with a '-'
        date_str = date_str.replace(":", "-") # This replaces spaces in the file path with a '-'
        self.log_file_path = "logs/server/" + "server-" + date_str + ".txt"
        self.write_to_log("----- Server Log -----")

    def create_socket(self):
        try:
            # printing the IP address of the host
            print(socket.gethostbyname(socket.gethostname()))
            
            # configure host IP address
            self.host = socket.gethostbyname(socket.gethostname())
            
            # create the socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.write_to_log(socket.gethostbyname(socket.gethostname()))
            self.write_to_log(self.port)
            self.write_to_log('Server socket created ')

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

    # Process messages (from either client or other server) and take appropriate action
    def handle_message(self,message_dict,address):
        message_type = message_dict["TYPE"]
        self.write_to_log('MESSAGE RECEIVED\t [' + str(address) + ']:\t ' + str(message_dict))

        if (message_type == "INITIALIZATION"):
            self.client_list.append(address)

            self.semaphore.acquire()
            try:
                if self.active == True:
                    # Notify the client about which server is the active one ("A" or "B")
                    msg = {"TYPE":"INITIALIZATION-SUCCESS","SERVER-TAG":self.server_tag}
                    msg_serialized = utils.serialize(msg)
                    self.sock.sendto(msg_serialized,address)
                    self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
            finally:
                self.semaphore.release()

        elif (message_type == "REGISTER"):

            success = self.db.add_user(message_dict["NAME"],message_dict["IP"],message_dict["PORT"])
            if (success == 0):
                msg = {"TYPE":"REGISTER-SUCCESS","RQ#":message_dict["RQ#"]}

                self.semaphore.acquire()
                try:
                    if self.active == True:
                        self.sock.sendto(utils.serialize(msg), address)
                        self.sock.sendto(utils.serialize(msg), (self.host_backup,self.port_backup))
                        self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                        self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup,self.port_backup)) + ']:\t ' + str(msg))
                finally:
                    self.semaphore.release()
            else:
                
                if (success == 1):
                    msg = {"TYPE":"REGISTER-DENIED","RQ#":message_dict["RQ#"],"REASON":"USERNAME ALREADY EXISTS"}

                elif (success == 2):
                    msg = {"TYPE":"REGISTER-DENIED","RQ#":message_dict["RQ#"],"REASON":"NOT A VALID USERNAME"}

                elif(success == 3):
                    msg = {"TYPE":"REGISTER-DENIED","RQ#":message_dict["RQ#"],"REASON":"DATABASE CONNECTION ERROR"}

                self.semaphore.acquire()
                try:
                    if self.active == True:
                        self.sock.sendto(utils.serialize(msg), address)
                        self.sock.sendto(utils.serialize(msg), (self.host_backup, self.port_backup))
                        self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                        self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg))
                finally:
                    self.semaphore.release()
                    
        elif (message_type == "DE-REGISTER"):
            
            success = self.db.remove_user(message_dict["NAME"])

            if (success):
                msg_client = {"TYPE":"DE-REGISTER-SUCCESS","RQ#":message_dict["RQ#"]}
                msg_server = {"TYPE":"DE-REGISTER-SUCCESS","RQ#":message_dict["RQ#"],"NAME":message_dict["NAME"]}
                self.sock.sendto(utils.serialize(msg_client), address)
                self.sock.sendto(utils.serialize(msg_server), (self.host_backup,self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg_client))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg_server))
            else:
                msg_client = {"TYPE":"DE-REGISTER-DENIED","RQ#":message_dict["RQ#"]}
                msg_server = {"TYPE":"DE-REGISTER-DENIED","RQ#":message_dict["RQ#"],"NAME":message_dict["NAME"]}
                self.sock.sendto(utils.serialize(msg_client), address)
                self.sock.sendto(utils.serialize(msg_server), (self.host_backup,self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg_client))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg_server))


        elif (message_type == "UPDATE-SOCKET"):
            
            success = self.db.update_socket(message_dict["NAME"], message_dict["IP"], message_dict["PORT"])

            if (success):
                msg = {"TYPE":"UPDATE-SOCKET-SUCCESS","RQ#":message_dict["RQ#"],"NAME":message_dict["NAME"],"IP":message_dict["IP"],"PORT":message_dict["PORT"]}
                self.sock.sendto(utils.serialize(msg), address)
                self.sock.sendto(utils.serialize(msg), (self.host_backup,self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg))
            else:
                msg = {"TYPE":"UPDATE-SOCKET-DENIED","RQ#":message_dict["RQ#"],"NAME":message_dict["NAME"],"IP":message_dict["IP"],"PORT":message_dict["PORT"]}
                self.sock.sendto(utils.serialize(msg), address)
                self.sock.sendto(utils.serialize(msg), (self.host_backup,self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg))
            
        elif (message_type == "SUBJECTS"):
            
            subjects_list = message_dict["SUBJECT-LIST"].split(",")
            print (subjects_list)

            success = self.db.update_subjects(message_dict["NAME"], subjects_list)

            if (success):
                msg = {"TYPE":"UPDATE-SUBJECTS-SUCCESS","RQ#":message_dict["RQ#"],"NAME":message_dict["NAME"],"SUBJECT-LIST":message_dict["SUBJECT-LIST"]}
                self.sock.sendto(utils.serialize(msg), address)
                self.sock.sendto(utils.serialize(msg), (self.host_backup,self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg))
            else:
                msg = {"TYPE":"UPDATE-SUBJECTS-DENIED","RQ#":message_dict["RQ#"],"NAME":message_dict["NAME"],"SUBJECT-LIST":message_dict["SUBJECT-LIST"]}
                self.sock.sendto(utils.serialize(msg), address)
                self.sock.sendto(utils.serialize(msg), (self.host_backup,self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg))


        elif (message_type == "PUBLISH"):
 
            success = self.db.publish_message(message_dict["NAME"], message_dict["SUBJECT"], message_dict["TEXT"])

            if (success):
                msg = {"TYPE":"PUBLISH-SUCCESS","RQ#":message_dict["RQ#"],"NAME":message_dict["NAME"],"SUBJECT":message_dict["SUBJECT"], "TEXT":message_dict["TEXT"]}
                self.sock.sendto(utils.serialize(msg), address)
                self.sock.sendto(utils.serialize(msg), (self.host_backup,self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg))
            else:
                msg = {"TYPE":"PUBLISH-DENIED","RQ#":message_dict["RQ#"],"NAME":message_dict["NAME"],"SUBJECT":message_dict["SUBJECT"], "TEXT":message_dict["TEXT"]}
                self.sock.sendto(utils.serialize(msg), address)
                self.sock.sendto(utils.serialize(msg), (self.host_backup,self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg))

        elif (message_type == "RETRIEVE-TEXTS"):

            msg_list = self.db.retrieve_texts(message_dict["NAME"])

            if (msg_list != None):
                msg = {"TYPE":"RETRIEVE-SUCCESS","RQ#":message_dict["RQ#"],"NAME":message_dict["NAME"],"POSTS":msg_list}
                self.sock.sendto(utils.serialize(msg), address)
                self.sock.sendto(utils.serialize(msg), (self.host_backup, self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg))

            else: 
                msg = {"TYPE":"RETRIEVE-DENIED","RQ#":message_dict["RQ#"]}
                self.sock.sendto(utils.serialize(msg), address)
                self.sock.sendto(utils.serialize(msg), (self.host_backup, self.port_backup))
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t ' + str(msg))
                self.write_to_log('MESSAGE SENT\t\t [' + str((self.host_backup, self.port_backup)) + ']:\t ' + str(msg))

        elif (message_type == "CHANGE-SERVER"):
            # If the server receives this message, it gains control
            self.gain_control()
            self.start_timer_thread()

        elif (message_type == "UPDATE-SERVER"):
            self.semaphore.acquire()
            try:
                if self.active == True:

                    # If a server receives this message, it means it the inactive server has 
                    # changed its IP and PORT. Thus, we should update these values
                    self.host_backup = message_dict["IP"]
                    self.port_backup = message_dict["PORT"]

                    # We should now reply to the new server that we have taken note of its IP and PORT
                    # We also send it our IP and PORT number so it knows which one is the active server
                    msg_reply = {"TYPE":"UPDATE-SERVER-SUCCESS","IP":self.host,"PORT":self.port,"SERVER-TAG":self.server_tag,"CLIENT-LIST":self.client_list}
                    msg_reply_serialized = utils.serialize(msg_reply)
                    self.sock.sendto(msg_reply_serialized,address)
                    self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t '  + str(msg_reply))

                # else if the inactive server receives this message, it should send a message 
                # to all the connected clients so they know where the new inactive server is
                else:
                    new_host = message_dict["IP"]
                    new_port = message_dict["PORT"]
                    msg_client = {"TYPE":"UPDATE-SERVER","IP":new_host,"PORT":new_port,"SERVER-TAG":self.server_tag}
                    msg_client_serialized = utils.serialize(msg_client)

                    for i in self.client_list:
                        self.sock.sendto(msg_client_serialized,i)
                        self.write_to_log('MESSAGE SENT\t\t [' + str(i) + ']:\t '  + str(msg_client))
                    self.write_to_log("SERVER-CLOSED")
                    print ("SERVER-CLOSED")

            except:
                print("ERROR SENDING UPDATE-SERVER MESSAGE")
                msg_error = {"TYPE":"UPDATE-SERVER-DENIED"}
                msg_error_serialized = utils.serialize(msg_error)
                self.sock.sendto(msg_error_serialized, address)
                self.write_to_log('MESSAGE SENT\t\t [' + str(address) + ']:\t '  + str(msg_error))
            finally:
                self.semaphore.release()

        elif (message_type == "END-CONNECTION"):
            try:
                self.client_list.remove(address)
            except:
                pass

        elif ((message_type == "REGISTER-SUCCESS") or (message_type == "REGISTER-DENIED")):
            pass

        elif ((message_type == "DE-REGISTER-SUCCESS") or (message_type == "DE-REGISTER-DENIED")):
            try: 
                if (message_type == "DE-REGISTER-SUCCESS"):
                    success = self.db.remove_user(message_dict["NAME"])
            except Exception as msg:
                print(str(msg))

        elif ((message_type == "UPDATE-SOCKET-SUCCESS") or (message_type == "UPDATE-SOCKET-DENIED")):
            try: 
                if (message_type == "UPDATE-SOCKET-SUCCESS"):
                    self.db.update_socket(message_dict["NAME"], message_dict["IP"], message_dict["PORT"])
            except:
                pass

        elif ((message_type == "UPDATE-SUBJECTS-SUCCESS") or (message_type == "UPDATE-SUBJECTS-DENIED")):
            subjects_list = message_dict["SUBJECT-LIST"].split(",")
            try: 
                if (message_type == "UPDATE-SUBJECTS-SUCCESS"):
                    self.db.update_subjects(message_dict["NAME"], subjects_list)
            except:
                pass
        
        elif ((message_type == "PUBLISH-SUCCESS") or (message_type == "PUBLISH-DENIED")):
            try: 
                if (message_type == "PUBLISH-SUCCESS"):
                    self.db.publish_message(message_dict["NAME"], message_dict["SUBJECT"], message_dict["TEXT"])
            except:
                pass

        elif ((message_type == "RETRIEVE-SUCCESS") or (message_type == "RETRIEVE-DENIED")):
            try: 
                if (message_type == "RETRIEVE-SUCCESS"):
                    self.db.retrieve_texts(message_dict["NAME"])
            except:
                pass

        elif ((message_type == "UPDATE-SERVER-SUCCESS") or (message_type == "UPDATE-SERVER-DENIED")):
            try: 
                if (message_type == "UPDATE-SERVER-SUCCESS"):
                    if message_dict["SERVER-TAG"] == "A":
                        self.server_tag = "B"
                        self.db = DBHandler(connection_string_2,"register-share-system-2")
                    else:
                        self.server_tag = 'A'
                        self.db = DBHandler(connection_string_1, "register-share-system-1")

                    self.host_backup = message_dict["IP"]
                    self.port_backup = message_dict["PORT"]
                    self.client_list = utils.convert(message_dict["CLIENT-LIST"])

            except:
                pass

        else:
            pass
    
    # This function is an ongoing loop that receives messages from clients and the other server
    def run(self):
        while (True):
            d = self.sock.recvfrom(1024)
            data = d[0]
            addr = d[1]
            if not data:
                break

            client_data = pickle.loads(data) # DESERIALIZED DATA
            client_dict = ''

            try:
                client_dict = ast.literal_eval(str(client_data))
            except:
                self.write_to_log("ERROR CONVERTING MESSAGE TO DICTIONARY")

            self.handle_message(client_dict,addr)

    