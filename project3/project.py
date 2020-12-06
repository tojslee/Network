from socket import *
import sys
import threading

clients = []
clientAddrs = []
clientThreads = []
clientNums = 0
printNums = 1

lock = threading.Lock()

def printBar():
    print("----------------------------------------------------\n");

def newClient():
    while True:
        # get data
        clientSocket, addr = serverSocket.accept()
        data = clientSocket.recv(8192)

        # if the request from the client is GET
        request_First_line = data.split("\n")[0]
        print(request_First_line)

# get argv value Port number
serverPort = int(sys.argv[1])

# server socket connection
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
serverSocket.listen()

print("Starting proxy server on port", serverPort)
printBar()

# get client request
while True:
    # except keyboard interrupt
    try:
        # new thread for handling new client
        setClient = threading.Thread(target=newClient, args=())
        setClient.daemon = True
        setClient.start()
        setClient.join()
    except KeyboardInterrupt:
        print()
        print('exit')
        sys.exit()



