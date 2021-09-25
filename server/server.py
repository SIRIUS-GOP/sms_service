#This server will operate from the LNL632 computer
#It will receive orders to send SMS, queueing them
#and sending accordingly

import socket, sys, json, sendsms, writer, config, re
from multiprocessing import Process, Queue, Pool, Manager, Value
from time import sleep
from datetime import datetime
from re import sub
from ctypes import c_bool
from systray import systray_run

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def on_new_client(connection, client_address, queue):
    while True:
        try:
            #print('connection from', client_address)
            ip1 = config.read("IP", "client_ip1")
            ip2 = config.read("IP", "client_ip2")
            ip3 = config.read("IP", "client_ip3")
            ip4 = config.read("IP", "client_ip4")
            data = ''
            if (client_address[0] == ip1 or client_address[0] == ip2 or client_address[0] == ip3 or client_address[0] == ip4):
                #Receive the data in small chunks and retransmit it
                data = connection.recv(1024)
                #print(datetime.now(),' received "%s"' % data, type(data))
                if data:
                    #print('sending data back to the client')
                    connection.sendall(data) #echo
                    to_sms = data.decode()
                    #print('to_sms: ', to_sms, type(to_sms))
                    queue.put_nowait(json.loads(to_sms)) #increment queue
                else:
                    #print('no data from ', client_address)
                    break
            else:
                connection.close()
        finally:
            #Clean up the connection
            connection.close()
            break
    #print('on_new_client OFF')
    quit()

def init():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the port
    ip = str(config.read("IP", "server_ip"))
    port = int(config.read("IP", "server_port"))
    #print(ip, port)
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
    while True:
        if stop.value:
            #print('server OFF')
            exit()
        sleep(1)
        # Wait for a connection
        connection, client_address = sock.accept()
        if client_address[0] != '10.20.31.19':
            try:
                #print('setting p')
                p = Process(target=on_new_client, args=(connection, client_address, queue))
                #print('on_new_client on')
                p.start()
            finally:
                #Clean up the connection
                #listen(sock)
                sleep(1)
        else:
            #print('server OFF')
            break

def watcherseye(queue, stop): #queue watcher
    while True:
        if stop.value:
            #print('watcherseye OFF')
            exit()
        sleep(1)
        if queue.empty() == False:
            n = queue.get_nowait()
            prefix = 'WARNING'
            msg, msg1, msg2, msg3 = '', '', '', ''
            if int(n['numpvs']) == 1:
                msg = prefix + '\n\r' + n['rule1']
                msg = msg.replace('pv', n['pv1'])
                msg = msg.replace('L', n['value1']) + '\n\r Rule: ' + n['rule1']
            elif int(n['numpvs']) == 2:
                if n['rule1'].find('(pv < LL) and (pv > LU)'): #outside range
                    msg1 = prefix + '\n\r' + n['pv1'] + ' outside limits!' + '\n\r Rule1: ' + n['rule1']
                elif n['rule1'].find('(pv > LL) and (pv < LU)'): #within range
                    msg1 = prefix + '\n\r' + n['pv1'] + ' within limits!'
                elif (bool(re.search('^pv .+ L$', n['rule1']))) != -1: #other rules
                    msg1 = prefix + '\n\r' + n['rule1']
                    msg1 = msg1.replace('pv', n['pv1'])
                    msg1 = msg1.replace('L', n['value1'])
                    msg1 = msg1 + '\n\r' + 'PV outside limit!' + '\n\r Rule1: ' + n['rule1']
                if n['rule2'].find('(pv < LL) and (pv > LU)'): #outside range
                    msg2 = '\n\r' + n['pv2'] + ' outside limits!' + '\n\r Rule2: ' + n['rule2']
                elif n['rule2'].find('(pv > LL) and (pv < LU)'): #within range
                    msg2 = '\n\r' + n['pv2'] + ' within limits!'
                elif (bool(re.search('^pv .+ L$', n['rule2']))): #other rules
                    msg2 = '\n\r' + n['rule2']
                    msg2 = msg2.replace('pv', n['pv2'])
                    msg2 = msg2.replace('L', n['value2'])
                    msg2 = '\n\r' + 'PV outside limit!' + '\n\r Rule2: ' + n['rule2']
                msg = msg1 + msg2
            elif int(n['numpvs']) == 3:
                if n['rule1'].find('(pv < LL) and (pv > LU)'): #outside range
                    msg1 = prefix + '\n\r' + n['pv1'] + ' outside limits!' + '\n\r Rule1: ' + n['rule1']
                elif n['rule1'].find('(pv > LL) and (pv < LU)'): #within range
                    msg1 = prefix + '\n\r' + n['pv1'] + ' within limits!'
                elif (bool(re.search('^pv .+ L$', n['rule1']))) != -1: #other rules
                    msg1 = prefix + '\n\r' + n['rule1']
                    msg1 = msg1.replace('pv', n['pv1'])
                    msg1 = msg1.replace('L', n['value1'])
                    msg1 = msg1 + '\n\r' + 'PV outside limit!' + '\n\r Rule1: ' + n['rule1']
                if n['rule2'].find('(pv < LL) and (pv > LU)'): #outside range
                    msg2 = '\n\r' + n['pv2'] + ' outside limits!' + '\n\r Rule2: ' + n['rule2']
                elif n['rule2'].find('(pv > LL) and (pv < LU)'): #within range
                    msg2 = '\n\r' + n['pv2'] + ' within limits!'
                elif (bool(re.search('^pv .+ L$', n['rule2']))): #other rules
                    msg2 = '\n\r' + n['rule2']
                    msg2 = msg2.replace('pv', n['pv2'])
                    msg2 = msg2.replace('L', n['value2'])
                    msg2 = '\n\r' + 'PV outside limit!' + '\n\r Rule2: ' + n['rule2']
                if n['rule3'].find('(pv < LL) and (pv > LU)'): #outside range
                    msg3 = '\n\r' + n['pv3'] + ' outside limits!' + '\n\r Rule3: ' + n['rule3']
                elif n['rule3'].find('(pv > LL) and (pv < LU)'): #within range
                    msg3 = '\n\r' + n['pv3'] + ' within limits!'
                elif (bool(re.search('^pv .+ L$', n['rule3']))): #other rules
                    msg3 = '\n\r' + n['rule3']
                    msg3 = msg3.replace('pv', n['pv3'])
                    msg3 = msg3.replace('L', n['value3'])
                    msg3 = '\n\r' + 'PV outside limit!' + '\n\r Rule3: ' + n['rule3']
                msg = msg1 + msg2 + msg3
            r = sendsms.sendSMS(sub("[^0-9]", "", n['phone']), msg)
            #print('r', r)
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
    #print('systray_run ok')
    p2 = Process(target=server, args=(sock, q, stop))
    p2.start()
    #print('server ok')
    p3 = Process(target=watcherseye, args=(q, stop))
    p3.start()
    #print('watcherseye ok')
    while exit.value == False:
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
        sleep(1)

if __name__ == '__main__':
    main()
