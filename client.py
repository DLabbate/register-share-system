import socket   
import sys
import time


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except OSError as msg:
    print('Failed to create socket')
    sys.exit()

#host = 'localhost'
host = socket.gethostbyname(socket.gethostname())
port = 8888

# https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal
while(True):
    msg = bytes("Hello!", "utf-8")

    try:
        time.sleep(1)
        s.sendto(msg, (host, port))
        d = s.recvfrom(1024)
        reply = d[0]
        addr = d[1]
        print('Server reply : ' + str(reply.decode("utf-8")))

    except OSError as msg:
        print('Error' + str(msg))
        sys.exit()
