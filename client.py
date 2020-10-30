import socket   
import sys
import time

#GLOBAL VARIABLES
sock = 0
host = socket.gethostbyname(socket.gethostname())
port = 8888


def createSocket():
    global sock
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except OSError as msg:
        print('Failed to create socket')
        sys.exit()

def run():
    global sock
    while(True):
        msg = bytes("Hello!", "utf-8")

        try:
            time.sleep(1)
            sock.sendto(msg, (host, port))
            d = sock.recvfrom(1024)
            reply = d[0]
            addr = d[1]
            print('Server reply : ' + str(reply.decode("utf-8")))

        except OSError as msg:
            print('Error' + str(msg))
            sys.exit()


#SCRIPT
createSocket()
run()