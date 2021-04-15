#This client sends data to PC server
#with pv name, rule, owner and phone

import socket
import sys
from app import getconfig

#data = b''

def client(msg): #rodar essa function no client
    # Create a TCP/IP socket 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data = b''
    # Connect the socket to the port where the server is listening
    try:
        server_ip = getconfig.read('IP', 'server_ip')
        server_address = (server_ip, 5007)
        #print('connecting to %s port %s' % server_address)
        sock.connect(server_address)
        # Send data
        #print('sending "%s"' % msg)
        s = sock.sendall(msg.encode())
        #print('s: ', s)
    except:
        #print('error on connect')
        return 0
    if s == None:
        # Look for the response
        amount_received = 0
        amount_expected = len(msg)
        #print('ammount_expected: ', amount_expected)
        #global data
        while amount_received < amount_expected:
            data = data + sock.recv(1024)
            amount_received += len(data)
            #print('data: ', data)
        #print('received "%s"' % data, type(data))
        if data.decode() == msg:
            #print('data: ', type(data.decode()), 'msg: ', type(msg))
            sock.close()
            return 1
        else:
            #print('echo error')
            sock.close()
            return 0
    else:
        #print('Error on sendall()')
        sock.close()
        return 0
    
# msg = '{"pv" : "SI-13C4:DI-DCCT:Current-Mon", \
#         "value" : "0.002", \
#         "rule" : "pv < L", \
#         "limits" : "L=0.002", \
#         "phone" : "19997397443", \
#         "owner" : "rone.castro"}'

# client(msg)