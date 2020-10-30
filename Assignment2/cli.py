from socket import *
import sys
import threading
import time

clientNums = 0

# for sender thread
def sender(clientSocket):
    while True:
        data = input()
        sendString = str(clientSocket.getsockname()[0]) + ':' + str(clientSocket.getsockname()[1]) + '/' + data
        clientSocket.send(sendString.encode('utf-8'))

# for receiving thread
def receiver(clientSocket):
    global clientNums
    while True:
        data = clientSocket.recv(1024)
        decodedData = data.decode('utf-8')
        index = decodedData.find('/')

        # if it is not data received
        if index == -1:
            # get data from the received line
            index = decodedData.find('|')
            num = decodedData.find('|', index+1)
            signal = decodedData[index + 1:num]
            clientNums = int(decodedData[num+1:])
            addr = decodedData[:index]
            descp = addr.find(':')
            sendIP = addr[:descp]
            sendPort = int(addr[descp+1:])

            # if the data is about the client which is receiving the line
            if clientSocket.getsockname()[0] == sendIP and clientSocket.getsockname()[1] == sendPort:
                if clientNums < 2:
                    numcounter = '(' + str(clientNums) + ' user online)'
                    print('> Connected to the chat server', numcounter)
                else:
                    numcounter = '(' + str(clientNums) + ' users online)'
                    print('> Connected to the chat server', numcounter)
            else: # or else
                if signal == 'enter':
                    if clientNums < 2:
                        numcounter = '(' + str(clientNums) + ' user online)'
                        print('> New user', decodedData[:index], 'entered', numcounter)
                    else:
                        numcounter = '(' + str(clientNums) + ' users online)'
                        print('> New user', decodedData[:index], 'entered', numcounter)
                else:
                    if clientNums < 2:
                        numcounter = '(' + str(clientNums) + ' user online)'
                        print('< The user', decodedData[:index], 'left', numcounter)
                    else:
                        numcounter = '(' + str(clientNums) + ' users online)'
                        print('< The user', decodedData[:index], 'left', numcounter)
        else: # the data has been received
            realData = decodedData[index+1:]
            addr = decodedData[:index]
            header = '[' + addr + ']'
            idx = addr.find(':')
            sendIP = addr[:idx]
            sendPort = int(addr[idx+1:])
            # data from the other client
            if not (clientSocket.getsockname()[0] == sendIP and clientSocket.getsockname()[1] == sendPort):
                print(header, realData)
            else: # if the data has sended from this client
                print("\x1B[F\x1B[2K"+"[You]", realData)
        #break
        

# get argv value IP, Port number
clientIP = sys.argv[1]
clientPort = int(sys.argv[2])

#server socket connection
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((clientIP, clientPort))

# try except block to catch keyboard interrupt
try:   
    receiveMessage = threading.Thread(target = receiver, args =(clientSocket, ))
    sendMessage = threading.Thread(target = sender, args = (clientSocket, ))
    receiveMessage.daemon = True
    sendMessage.daemon = True
    receiveMessage.start()
    sendMessage.start()
    receiveMessage.join()
    sendMessage.join()
except KeyboardInterrupt:
    sendString = str(clientSocket.getsockname()[0]) + ':' + str(clientSocket.getsockname()[1]) + '|exited'
    clientSocket.send(sendString.encode('utf-8'))
    print()
    print('exit')
    sys.exit()