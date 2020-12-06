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
    print("----------------------------------------------------");

def substitute_web(URL, data):
    idx = URL.find("yonsei")
    if idx != -1:
        # there is yonsei in the URL
        start = data.find(URL)
        end = data.find(" ", start)
        newData = data[:start] + "www.linuxhowtos.org" + data[end:]
        return (newData, True)

    return (data, False)


def setClient(clientSocket, addr, data):
    # gather information of client and request for printing data
    clientIP = str(addr[0])
    clientPort = str(addr[1])
    request_first_line = data.split("\n")[0]
    request_user_agent = data.split("\n")[2][12:]

    #print(request_first_line)
    #print(request_user_agent)

    web_URL = request_first_line.split(" ")[1]
    #print(web_URL)

    newData, flag = substitute_web(web_URL, data)
    #print(newData)

    if flag:
        # new web_URL
        web_URL = "www.linuxhowtos.org"

    new_request_first_line = data.split("\n")[0]
    new_request_user_agent = data.split("\n")[2][12:]

    proxy_server = socket(AF_INET, SOCK_STREAM)
    #proxy_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    proxy_server.connect((web_URL, 80))
    proxy_server.send(data.encode('utf-8'))

    while True:
        respond = proxy_server.recv(8192)
        decoded_respond = respond.decode('utf-8')
        print(respond)
        if len(decoded_respond) > 0:
            respond_first_line = decoded_respond.split("\n")[0]
            clientSocket.send(respond)


def newClient(serverSocket):
    while True:
        # get data
        clientSocket, addr = serverSocket.accept()
        data = clientSocket.recv(8192)
        decoded = data.decode('utf-8')

        # if the request from the client is GET
        request_First_line = decoded.split("\n")[0]
        method = request_First_line.split(" ")[0]
        if method=="GET":
            getClient = threading.Thread(target=setClient, args=(clientSocket, addr, decoded, ))
            getClient.daemon = True
            getClient.start()
            getClient.join()

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
        getClient = threading.Thread(target=newClient, args=(serverSocket,))
        getClient.daemon = True
        getClient.start()
        getClient.join()
    except KeyboardInterrupt:
        print()
        print('exit')
        sys.exit()
