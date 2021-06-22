#This server will operate from the LNL632 computer
#It will receive orders to send SMS, queueing them
#and sending accordingly

import socket, sys, json, sendsms, writer, config
from multiprocessing import Process, Queue, Pool, Manager, Value
from time import sleep
from datetime import datetime
from re import sub
from ctypes import c_bool
from systray import systray_run

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def init():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the port
    ip = str(config.read("IP", "server_ip"))
    port = int(config.read("IP", "server_port"))
    print(ip, port)
    if (ip==0 or port==0):
        exit()
    else:
        server_address = (ip, port)
        sock.bind(server_address)
        sock.listen(1)
        t = sock
        return t

def listen(sock):
    # Listen for incoming connections
    sock.listen(1)

#listen()

def server(sock, queue, stop):
    data = ''
    #print('server on')
    while True:
        if stop.value:
            #print('P2 OFF')
            exit()
        sleep(1)
        # Wait for a connection
        connection, client_address = sock.accept()
        try:
            #print('connection from', client_address)
            ip1 = config.read("IP", "client_ip1")
            ip2 = config.read("IP", "client_ip2")
            ip3 = config.read("IP", "client_ip3")
            if (client_address[0] == ip1 or client_address[0] == ip2 or client_address[0] == ip3):
                #Receive the data in small chunks and retransmit it
                data = connection.recv(1024)
                #print(datetime.now(),' received "%s"' % data, type(data))
                if data:
                    #print('sending data back to the client')
                    connection.sendall(data) #echo
                    to_sms = data.decode()
                    #print('to_sms: ', to_sms, type(to_sms))
                    queue.put_nowait(json.loads(to_sms)) #increment queue
                # else:
                #     pass
                #     print('no more data from ', client_address)
                #     break
            else:
                connection.close()
        finally:
            #Clean up the connection
            connection.close()
            listen(sock)
            sleep(1)

def watcherseye(queue, stop): #queue watcher
    #print('watcherseye on')
    while True:
        if stop.value:
            #print('P3 OFF')
            exit()
        sleep(1)
        if queue.empty() == False:
            n = queue.get_nowait()
            msg = str('PV: ' + n['pv'] + '\n\r Rule: ' + n['rule'] + '\n\r Limit(s): '\
                      + n['limits'] + '\n\r PV Value: ' + n['value'])
            r = sendsms.sendSMS(sub("[^0-9]", "", n['phone']), msg)
            print(r)
            if r==True:
                writer.write(msg)
            else:
                writer.write('Modem error: ' + str(r))
        else:
            sleep(1)

def main():
    sock = init()
    q = Queue()
    start = Value(c_bool, False)
    stop = Value(c_bool, False)
    exit = Value(c_bool, False)
    #t = systray_run(stop, exit)
    p1 = Process(target=systray_run, args=(start, stop, exit))
    p1.start()
    #print('p1 ok')
    p2 = Process(target=server, args=(sock, q, stop))
    p2.start()
    #print('\rp2 ok')
    p3 = Process(target=watcherseye, args=(q, stop))
    p3.start()
    #print('p3 ok')
    while exit.value == False:
        sleep(1)
        if (start.value == True and stop.value == True):
            stop.value = False
            sock = init()
            p2 = Process(target=server, args=(sock, q, stop))
            p2.start()
            #print(start, '\np2 ok')
            p3 = Process(target=watcherseye, args=(q, stop))
            p3.start()
            #print('p3 ok')
            start.value = False

if __name__ == '__main__':
    main()
