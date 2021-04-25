import time
from socket import *
from threading import Thread
import sys


def recv_timeout(the_socket,timeout=2):
    the_socket.setblocking(0)
    
    total_data=[]
    data=''
    
    begin=time.time()
    while True:
        if total_data and time.time()-begin > timeout:
            break
        elif time.time()-begin > timeout*2:
            break

        try:
            data = the_socket.recv(65535)
            if data:
                total_data.append(data)
                begin=time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    
    res = b""
    for i in total_data:
        res = res+i
    return res

def myTask(connSock, thread_id, count):
    log = []
    global total_thread_no
    urlFilter = "X"
    imgFilter = "X"
    try:
        # CLI ==> PRX
        data = connSock.recv(8192).decode('utf-8', errors = 'ignore')
        data_lines = data.split("\r\n")
        # print("Request Length : {}".format(len(data)))
        if ("GET" in data) and ("windowsupdate" not in data) and ("microsoft.com" not in data):
            if ("yonsei" in data):
                urlFilter = "O"
            log.append("{}  [Conn: {}/ {}]".format(count, thread_id, total_thread_no))
            # print("{}  [Conn: {}/ {}]".format(count, thread_id, total_thread_no))
            log.append("[ {} ] URL filter | [ {} ] Image filter\n".format(urlFilter, imgFilter))
            # print("[ {} ] URL filter | [ {} ] Image filter\n".format(urlFilter, imgFilter))
            log.append("[CLI connected to {}:{}]".format(addr[0], addr[1]))
            # print("[CLI connected to {}:{}]".format(addr[0], addr[1]))
            log.append("[CLI ==> PRX --- SRV]")
            # print("[CLI ==> PRX --- SRV]")
            data_dict = {}
            # print(data)
            for line in data_lines:
                line_split = line.split(" ")
                data_dict[line_split[0]] = line_split[1:]
                # print (line)
            method_message = data_dict['GET'][0]
            log.append(" > GET " + method_message)
            # print(" > GET", method_message)
            userAgent = data_dict['User-Agent:']
            userAgent_message = ""
            for word in userAgent:
                userAgent_message += (word+" ")
            log.append(" > " + userAgent_message)
            # print(' >', userAgent_message)


            # PRX ==> SRV
            url = data_dict['GET'][0].split(" ")[0]
            if ("?image_off" in url):
                imgFilter = "O"
            elif ("?image_on" in url):
                imgFilter = "X"
            host = data_dict['Host:'][0]
            outerSock = socket(AF_INET, SOCK_STREAM)
            outerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            req = data.split("\r\n")

            # Redirect if "yonsei" is included
            if (urlFilter == "O"): 
                url = "www.linuxhowtos.org"
                host = "linuxhowtos.org"
                req[0] = "GET http://linuxhowtos.org/ HTTP/1.1"
                req[1] = "Host: linuxhowtos.org"

            log.append("[SRV connected to {}:80]".format(host))
            log.append("[CLI --- PRX ==> SRV]")
            outerSock.connect((host, 80))
            data_toServer = ""
            for line in req:
                data_toServer += line+"\r\n"
            log.append(" > GET " + url)
            log.append(" > " + userAgent_message)
            outerSock.send(data_toServer.encode("utf-8", errors = 'ignore'))


            # PRX <== SRV
            log.append("[CLI --- PRX <== SRV]")
            res = []
            response_raw = recv_timeout(outerSock)
            response_string = response_raw.decode("utf-8", errors = 'ignore')
            response_Lines = response_string.split("\r\n")
            response_dict = {}
            status = ""
            contentInfo = ""
            for i in range(len(response_Lines)):
                line = response_Lines[i]
                if (i == 0):
                    status = line
                    log.append(" > "+status[9:])
                elif ("Content-Type" in line):
                    contentInfo += line[14:]
                elif ("Content-Length" in line):
                    contentInfo += line.split(" ")[1] +" bytes "
            log.append(" > " + contentInfo)
            if (imgFilter == 'O'):
                if ("image" in contentInfo):
                    connSock.close()
                    total_thread_no -= 1
                    return

            # CLI <== PRX
            log.append("[CLI <== PRX --- SRV]")
            connSock.send(response_raw)
            log.append(" > "+status)
            log.append(" > "+contentInfo)
            connSock.close()
            log.append("[CLI disconnected]")
            log.append("[SRV disconnected]")
            outerSock.close()
            log.append("-----------------------------------------------")
            res = "\n".join(log)
            print(res)
            total_thread_no -= 1

    except KeyboardInterrupt as e:
        print (e)
        sys.exit()
    
    except Exception as e:
        print (e)
        return


if (__name__ == "__main__"):

    srvSock = socket(AF_INET, SOCK_STREAM)

    serverPort = int(sys.argv[1])
    print("Starting proxy server on port {}...".format(serverPort))
    srvSock.bind(('127.0.0.1', serverPort))
    srvSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)


    total_thread_no = 0
    count = 0
    srvSock.listen()

    while 1:
        cliSock, addr = srvSock.accept()
        thread_id = total_thread_no
        total_thread_no += 1
        count += 1
        myThread = Thread(target = myTask, args = (cliSock, thread_id, count))
        myThread.daemon = True
        myThread.start()
        