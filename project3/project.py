from socket import *
import sys
import threading

clients = []
clientAddrs = []
clientThreads = []
clientNums = 0

lock = threading.Lock()

def printBar():
    print("----------------------------------------------------\n");


def newClient(serverSocket):
    global clients, clientAddrs, clientNums, clientThreads

    while True:
        clientSocket, addr = serverSocket.accept()

        # handle information of the new client
        lock.acquire()
        clients.append(clientSocket)
        clientAddrs.append(addr)
        clientNums += 1

        newThread = threading.Thread(target=receiver, args=(clientSocket,addr))
        newThread.daemon = True
        newThread.start()
        clientThreads.append(newThread)
        lock.release()

def receiver(clientSocket, addr):
    # handle request and sent request to server
    data = clientSocket.recv(8192)
    print(data)

# get argv value Port number
serverPort = int(sys.argv[1])

# server socket connection
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
serverSocket.listen()

print("Starting proxy server on port", serverPort);
printBar();

# get client request
while True:
    # except keyboard interrupt
    try:
        # new thread for handling new client
        setClient = threading.Thread(target=newClient, args=(serverSocket, ))
        setClient.daemon = True
        setClient.start()
        setClient.join()
    except KeyboardInterrupt:
        print()
        print('exit')
        sys.exit()



