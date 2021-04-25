from socket import *
from threading import Thread
import sys
import atexit

# Get Server's IP address & Port to connect
IP = sys.argv[1]
serverPort = int(sys.argv[2])

# Connect to Server
clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
clientSock.connect((IP, serverPort))

# Sending Message
def sender():
    while 1:
        sending_message = input()
        clientSock.send(sending_message.encode('utf-8'))

# Receiving Message
def receiver():
    while 1:
        received_message = clientSock.recv(1024).decode('utf-8')
        print(received_message)

# Make 2 Threads
sendingThread = Thread(target = sender)
receivingThread = Thread(target = receiver)
receivingThread.start()
sendingThread.start()

def disconnect():
    clientSock.close()

atexit.register(disconnect)