# import required Libraries
from socket import *
from threading import Thread
import sys
import atexit

# A Function to Announce that a new Client has been connected to server
def login(sock, addr, clientlist):
    # Get the New Client's Info
    clientIP, clientPort = addr[0], addr[1]

    if len(clientlist) <= 1:
        # Send Connected Message to the new Client
        sock.send("> Connected to the chat server ({} user online)".format(
            len(clientlist)).encode())
        # Send to the other Clients that a new client has been arrived
        for client in clientlist:
            if not((client[1][0] == clientIP) & (client[1][1] == clientPort)):
                client[0].send("> New user {}:{} entered ({} user online)".format(
                    clientIP, clientPort, len(clientlist)).encode())
    else:
        sock.send("> Connected to the chat server ({} users online)".format(
            len(clientlist)).encode())
        for client in clientlist:
            if not((client[1][0] == clientIP) & (client[1][1] == clientPort)):
                client[0].send("> New user {}:{} entered ({} users online)".format(
                    clientIP, clientPort, len(clientlist)).encode())


def messenger(connectionSock, addr, clientlist):
    # Get the New Client's Info
    clientIP, clientPort = addr[0], addr[1]

    while 1:
        try:
            message = connectionSock.recv(1024).decode('utf-8')
            res = "[{}:{}] {}".format(clientIP, clientPort, message)
            if len(message) > 0:
                print(res)
            for client in clientlist:
                # Send new Client's message with [You]
                if ((client[1][0] == clientIP) & (client[1][1] == clientPort)):
                    client[0].send(("[You] " + message).encode())
                # Send res to other clients
                else:
                    client[0].send(res.encode())
            continue
        except BrokenPipeError:
            if len(clientlist) <= 2:
                print("< The user {}:{} left ({} user online)".format(clientIP, clientPort, len(clientlist)-1))
            else:
                print("< The user {}:{} left ({} users online)".format(clientIP, clientPort, len(clientlist)-1))

            for client in clientlist:
                if client[1] == addr:
                    clientlist.remove(client)
            break


# Get IP address & Port to bind
IP = sys.argv[1]
serverPort = int(sys.argv[2])

# Set Socket options and initialize Server's Socket
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSock.bind(('0.0.0.0', serverPort))

print("Chat Server started on port {}.".format(serverPort))
serverSock.listen()

# Initialize a Client List
clientlist = []

# Main
while 1:

    # Continuously Accept New Client
    connectionSock, addr = serverSock.accept()
    clientlist.append((connectionSock, addr))
    login(connectionSock, addr, clientlist)
    # Print New Client's Info
    if len(clientlist) <= 1:
        print("> New user {}:{} entered ({} user online)".format(addr[0], addr[1], len(clientlist)))
    else:
        print("> New user {}:{} entered ({} users online)".format(addr[0], addr[1], len(clientlist)))

    # Start New Thread for Client
    newThread = Thread(target=messenger, args=(connectionSock, addr, clientlist))
    newThread.daemon = True
    newThread.start()


def disconnect():
    serverSock.close()


atexit.register(disconnect)