import socket
import sys

#GLOBAL VARIABLES
#---------------------------------------------------------------------------------------------------
host = ''      # Symbolic name meaning all available interfaces
port = 8888    # Arbitrary non-privileged port
sock = 0
#---------------------------------------------------------------------------------------------------


#FUNCTIONS
#---------------------------------------------------------------------------------------------------
def createSocket():
    try:
        # printing the IP address of the host
        print(socket.gethostbyname(socket.gethostname()))
        # configure host IP address
        global host
        host = socket.gethostbyname(socket.gethostname())
         #HOST = "localhost"
         # create the socket
        global sock 
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Socket created')

        # https://stackoverflow.com/questions/31964722/python-3-4-socket-error-deprecated-new-equivalent
    except OSError as msg:
        print('Failed to create socket. Error Code : ' + str(msg))
        sys.exit()

def bindSocket():
    global sock
    try:
        sock.bind((host, port))
    except OSError as msg:
        print('Bind failed. Error Code : ' + str(msg))
        sys.exit()

    print('Socket bind complete')

def run():
    while (True):
        d = sock.recvfrom(1024)
        data = d[0]
        addr = d[1]
        if not data:
            break

        reply = bytes('OK...' + str(data), "utf-8")

        sock.sendto(data, addr)
        print('Message[' + str(addr) + ']: ' + str(data.decode("utf-8")))

    sock.close()
#---------------------------------------------------------------------------------------------------




#SCRIPT
#---------------------------------------------------------------------------------------------------
createSocket()
bindSocket()
run()
#---------------------------------------------------------------------------------------------------
