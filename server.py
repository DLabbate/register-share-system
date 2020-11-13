import socket
import sys      
import time
import pickle
import ast
import json
import datetime
import time
import threading

from db_handler import DBHandler
import utils

class Server:

    def __init__(self):
        self.sock = None #socket
        self.host = None
        self.port = 8888
        self.log_file_path = ''
        self.active = False
        self.host_backup = None
        self.port_backup = 0
        self.semaphore = threading.Semaphore(1)

    def change_server(self,address):
        msg = {"TYPE":"CHANGE-SERVER","IP":self.host,"PORT":self.port}
        self.sock.sendto(utils.serialize(msg),address)
        self.write_to_log("MESSAGE SENT "+str(msg))

    def gain_control(self):
        #self.semaphore.acquire()
        self.active = True
        #self.semaphore.release()

    def start_timer(self):
        #self.semaphore.acquire()
        if self.active == True:
            #self.semaphore.release()
            endtime = time.time() + 20
            while time.time() < endtime:
                #self.write_to_log("time: " + str(time.time()) + "active: " + str(self.active))
                pass
            #self.semaphore.acquire()
            self.active = False
            # We should now send a message to the other server to inform it to take
            self.change_server((self.host_backup,self.port_backup))
            #self.semaphore.release()
    
    def start_timer_thread(self):
        # self.semaphore.acquire()
        timer_thread = threading.Thread(target=self.start_timer)
        timer_thread.start()
        #self.semaphore.release()

    def server_initialize(self, status,port, host_backup, port_backup):
        if (status == 'active'):
            self.active = True
            self.start_timer_thread()
        self.port = port
        self.host_backup = host_backup
        self.port_backup = port_backup
        # self.write_to_log("Status: " + str(status))
        # self.write_to_log("Other server: (" + str(host_backup) + "," + str(port_backup) + ")")

    def write_to_log(self,msg):
        #self.semaphore.acquire()
        log_file = open(self.log_file_path,"a+")
        log_file.write(str(msg)+"\n")
        log_file.close()
        #self.semaphore.release()

    def initialize_log_file(self):
        date_str_temp = str(datetime.datetime.now())
        date_str = date_str_temp.replace(" ", "-")  #This replaces spaces in the file path with a '-'
        date_str = date_str.replace(".", "-") #This replaces spaces in the file path with a '-'
        date_str = date_str.replace(":", "-") #This replaces spaces in the file path with a '-'
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

    # Process message and call appropriate function
    def handle_client(self,message_dict,address):
        message_type = message_dict["TYPE"]
        self.write_to_log('MESSAGE RECEIVED [' + str(address) + ']: ' + str(message_dict))
        #print('Message[' + str(address) + ']: ' + str(message_dict))

        #self.semaphore.acquire()
        if (message_type == "INITIALIZATION"):
            pass
        elif (message_type == "REGISTER"):
            db = DBHandler()
            success = db.add_user(message_dict["NAME"],message_dict["IP"],message_dict["PORT"])
            if (success):
                msg = {"TYPE":"REGISTER-SUCCESS","RQ#":message_dict["RQ#"]}
                self.sock.sendto(utils.serialize(msg), address)
                self.write_to_log("MESSAGE SENT "+str(msg))
            else:
                msg = {"TYPE":"REGISTER-DENIED","RQ#":message_dict["RQ#"]}
                self.sock.sendto(utils.serialize(msg), address)
                self.write_to_log("MESSAGE SENT "+str(msg))
        elif (message_type == "DE-REGISTER"):
            pass
        elif (message_type == "UPDATE-SOCKET"):
            pass
        elif (message_type == "SUBJECTS"):
            pass
        elif (message_type == "PUBLISH"):
            pass
        elif (message_type == "CHANGE-SERVER"):
            # If the server receives this message, it gains control
            #self.write_to_log("hello")
            self.gain_control()
            self.start_timer_thread()
        else:
            pass
    #self.semaphore.release()
        
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
                self.write_to_log("ERROR CONVERTING MESSAGE TO DICTIONARY")
                #print("ERROR CONVERTING MESSAGE TO DICTIONARY")

            self.handle_client(client_dict,addr)

            #clientDict = pickle.loads(data)
            #print(clientDict["TYPE"])
            #print(type(clientData))
            #clientDict = ast.literal_eval(clientData)
            #print(clientDict["TYPE"])
            #reply = pickle.dumps(data) #SERIALIZED

            #self.sock.sendto(data, addr)
            
            #print('Message[' + str(addr) + ']: ' + str(clientData))

    