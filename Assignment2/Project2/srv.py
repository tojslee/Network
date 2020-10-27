from socket import *
import sys
import threading
import time

clients = []
clientAddrs = []
clientThreads = []
clientNums = 0

lock = threading.Lock()

def newClient(serverSocket):
    global clients, clientAddrs, clientNums, clientThreads
    
    while True:
        clientSocket, addr = serverSocket.accept()

        # handle information of the new client
        lock.acquire()
        clients.append(clientSocket)
        clientAddrs.append(addr)
        clientNums += 1

        # create new thread for receiving data
        newThread = threading.Thread(target = receiver, args = (clientSocket, ))
        newThread.daemon = True
        newThread.start()
        clientThreads.append(newThread)
        lock.release()

        printFormat = str(addr[0]) + ':' + str(addr[1])
        if clientNums < 2:
            onlineStatus = '(' + str(clientNums) + ' user online)'
            print('> New user', printFormat, 'entered', onlineStatus)
        else:
            onlineStatus = '(' + str(clientNums) + ' users online)'
            print('> New user', printFormat, 'entered', onlineStatus)
        
        #lock.acquire()
        #forNew = str(addr[0]) + ':' + str(addr[1]) + '|enter|' + str(clientNums)
        #for socket in clients:
        #    socket.send(forNew.encode('utf-8'))
        #lock.release()
        # send all clients that there is a new online client
        sendThread = threading.Thread(target = send_new, args = (addr, ))
        sendThread.daemon = True
        sendThread.start()
        
        

def receiver(clientSocket):
    global clinets, clientAddrs, clientNums, clientThreads
    #print('receiver')
    while True:
        data = clientSocket.recv(1024)
        decodedData = data.decode('utf-8')
        index = decodedData.find('/')
        if index == -1:
            index = decodedData.find('|')
            # delete socket and addr from the list
            lock.acquire()
            for i in range(clientNums):
                if clients[i] == clientSocket:
                    del clients[i]
                    del clientAddrs[i]
                    break
            clientNums -= 1
            lock.release()
            # close the socket
            clientSocket.close()
            header = decodedData[:index]
            if clientNums < 2:
                onlineStatus = '(' + str(clientNums) + ' user online)'
                print('< The user', header, 'left', onlineStatus)
            else:
                onlineStatus = '(' + str(clientNums) + ' users online)'
                print('< The user', header, 'left', onlineStatus)

            # send data to all clients that there is a client which has been exited
            sendThread = threading.Thread(target = send_exit, args = (header, ))
            sendThread.daemon = True
            sendThread.start()
            #lock.acquire()
            #forExit = header + '|exited|' + str(clientNums)
            #for socket in clients:
            #    socket.send(forExit.encode('utf-8'))
            #lock.release()
            break
        else:
            header = decodedData[:index]
            realData = decodedData[index + 1:]
            overall = '[' + header + '] ' + realData
            print(overall)
            # send data to all clients with header
            sendThread = threading.Thread(target = send_data, args = (header, realData, ))
            sendThread.daemon = True
            sendThread.start()
            #forData = header + '/' + realData
            #lock.acquire()
            #for socket in clients:
            #    socket.send(forData.encode('utf-8'))
            #lock.release()


# if there is a new client send all clients that there is a new client
def send_new(addr):
    global clientNums, clients
    lock.acquire()
    forNew = str(addr[0]) + ':' + str(addr[1]) + '|enter|' + str(clientNums)
    for socket in clients:
        socket.send(forNew.encode('utf-8'))
    lock.release()
    return

def send_exit(header):
    global clientNums, clients
    lock.acquire()
    forExit = header + '|exited|' + str(clientNums)
    for socket in clients:
        socket.send(forExit.encode('utf-8'))
    lock.release()
    return


def send_data(header, data):
    global clients
    forData = header + '/' + data
    lock.acquire()
    for socket in clients:
        socket.send(forData.encode('utf-8'))
    lock.release()
    return


# get argv value IP, Port number
serverIP = sys.argv[1]
serverPort = int(sys.argv[2])

#server socket connection
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen()

print("Chat Server started on port", serverPort)

try:
    setClient = threading.Thread(target = newClient, args =(serverSocket, ))
    setClient.daemon = True
    setClient.start()
    setClient.join()
except KeyboardInterrupt:
    print()
    print('exit')
    sys.exit()