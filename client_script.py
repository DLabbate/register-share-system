import sys
import socket
from client import Client

hostA = str(sys.argv[1])
portA = int(sys.argv[2])
hostB = str(sys.argv[3])
portB = int(sys.argv[4])

client = Client()
client.createSocket()
client.updateServers(hostA,portA,hostB,portB)
client.initialize()
client.sendRegister("dom")
client.run()