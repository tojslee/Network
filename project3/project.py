from socket import *
import sys
import threading

class aClient:
    urlFilter = 'X'
    imageFilter = 'X'
    def __init__(self, clientSocket, thr):
        self.socket = clientSocket
        self.thread = thr

clients = []
threads = []
printNum = 1

lock = threading.Lock()

def printBar():
    print("----------------------------------------------------");

def substitute_web(URL, data):
    idx = URL.find(b'yonsei')
    if idx != -1:
        # there is yonsei in the URL
        start = data.find(URL)
        end = data.find(b' ', start)
        newData = data[:start] + b'http://www.linuxhowtos.org/' + data[end:]

        #change host to new URL
        start = newData.find(b'Host')
        end = newData.find(b'\r\n', start)
        newData = newData[:start+6] + b'www.linuxhowtos.org' + newData[end:]
        return (newData, True)

    return (data, False)


def setClient(clientSocket, addr, data):
    global printNum, clients, threads
    # gather information of client and request for printing data
    try:
        # get information
        clientIP = str(addr[0])
        clientPort = str(addr[1])

        request_first_line = data.split(b'\n')[0]
        request_user_agent = data.split(b'\n')[2][12:]
        web_URL = request_first_line.split(b' ')[1]
        questionMark = web_URL.find(b'?image_off')
        if questionMark != -1:
            #image filter needed
            imageF = True
        else:
            imageF = False

        flag = False
        if b'GET' in data:
            # URL filter
            data, flag = substitute_web(web_URL, data)

        if flag:
            # new web_URL
            web_URL = "www.linuxhowtos.org"
        else:
            st = web_URL.find(b'://')
            ed = web_URL.find(b'/', st+3)
            web_URL = web_URL[st+3:ed]

        # set information of the connection
        lock.acquire()
        for i in range(len(clients)):
            if clients[i].socket == clientSocket:
                if flag:
                    clients[i].urlFilter = 'O'
                else:
                    clients[i].urlFilter = 'X'
                if imageF:
                    clients[i].imageFilter = 'O'
                else:
                    clients[i].imageFilter = 'X'
                break
        lock.release()

        #get data
        new_request_first_line = data.split(b'\n')[0]
        new_request_user_agent = data.split(b'\n')[2][12:]

        # connect to actual server
        proxy_server = socket(AF_INET, SOCK_STREAM)
        proxy_server.connect((web_URL, 80))
        proxy_server.send(data)
        respond = proxy_server.recv(8192)
        rec_header = respond.split(b'\r\n\r\n')[0]
        # get data
        stat = rec_header.split(b'\r\n')[0]
        ind = stat.find(b' ')
        response_status = stat[ind+1:]
        content = rec_header.find(b'Content-Type')
        content_end = rec_header.find(b'\r\n', content)
        if content != -1:
            if content_end != -1:
                response_mime_type = rec_header[content+14:content_end]
            else:
                response_mime_type = rec_header[content+14:]
        else:
            response_mime_type = b'Not-defined'
        content = rec_header.find(b'Content-Length')
        content_end = rec_header.find(b'\r\n', content)
        if content != -1:
            if content_end != -1:
                response_byte = rec_header[content+16:content_end]
            else:
                response_byte = rec_header[content+16:]
        else:
            response_byte = b'Not-defined'

        # image Filter

        clientSocket.send(respond)

        # print interface & information & delete aClass class
        lock.acquire()
        for i in range(len(clients)):
            if clients[i].socket == clientSocket:
                for j in range(len(threads)):
                    if threads[j] == clients[i].thread:
                        print("%d [Conn: %d / %d]"%(printNum, i+1, len(threads)))
                        printNum = printNum + 1
                        del threads[j]
                        break
                print("[%c] URL filter | [%c] Image filter\n"%(clients[i].urlFilter, clients[i].imageFilter))
                print("[CLI connected to %s:%s]"%(clientIP, clientPort))
                print("[CLI ==> PRX --- SRV]")
                print(" > %s"%(request_first_line.decode('utf-8')))
                print(" > %s"%(request_user_agent.decode('utf-8')))
                print("[SRV connected to %s:%d]"%(web_URL, 80))
                print("[CLI --- PRX ==> SRV]")
                print(" > %s"%(new_request_first_line.decode('utf-8')))
                print(" > %s"%(new_request_user_agent.decode('utf-8')))
                print("[CLI --- PRX <== SRV]")
                print(" > %s"%(response_status.decode('utf-8')))
                print(" > %s %sbyte"%(response_mime_type.decode('utf-8'), response_byte.decode('utf-8')))
                print("[CLI <== PRX --- SRV]")
                print(" > %s"%(response_status.decode('utf-8')))
                #print(" > %s %s"%(response_mime_type.decode('utf-8'), new_response_size.decode('utf-8')))
                print("[CLI disconnected]")
                print("[SRV disconnected]")
                printBar()
                del clients[i]
                break
        lock.release()
        proxy_server.close()
        clientSocket.close()
    except Exception as e:
        print(e)
        clientSocket.close()

def newClient(serverSocket):
    global seqNum,clients,threads
    while True:
        try:
            clientSocket, addr = serverSocket.accept()
            data = clientSocket.recv(8192)
            getClient = threading.Thread(target=setClient, args=(clientSocket, addr, data, ))
            getClient.daemon = True
            lock.acquire()
            newC = aClient(clientSocket, getClient)
            clients.append(newC)
            threads.append(getClient)
            lock.release()
            getClient.start()
            getClient.join()
        except Exception as e:
            clientSocket.close()
            print(e)
            continue
# get argv value Port number
serverPort = int(sys.argv[1])

# server socket connection
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
serverSocket.listen()

print("Starting proxy server on port", serverPort)
printBar()

# ecept keyboard interrupt
try:
    # new thread for handling new client
    getClient = threading.Thread(target=newClient, args=(serverSocket,))
    getClient.daemon = True
    getClient.start()
    getClient.join()
    #newClient(serverSocket)
except KeyboardInterrupt:
    #print()
    print('exit')
    sys.exit()
