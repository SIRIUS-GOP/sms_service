import serial
from time import sleep

class TextMessage:
    def __init__(self, recipient="", message=""):
        self.recipient = recipient
        self.content = message

    pipeline = "OK"
    ans = b''
        
    def connectPhone(self):
        try:
            self.ser = serial.Serial('COM8', 115200, timeout=2)
            sleep(1)
            return 1
        except:
            #print('Error connecPhone')
            return 'Cannot connect to the modem'

    def memSlot(self, index):
        try:
            if index:
                start = index.find("CMGW: ")
                end = index.find("\r\n\r")
                if (start==-1 or end==-1):
                    return 'Could not locate index'
                else:
                    n = index[start+6:end]
                    return n

            else:
                return "Index not set"
        finally:
            pass

    def sComm(self, cmd, rsize=0):
        try:
            r = self.ser.write((cmd + '\r').encode())
            if r:
                sleep(1)
                if rsize > 0:
                    r = self.ser.read(rsize)
                    self.ans = r
                    if len(r) > 0:
                        r = r.decode("utf-8")
                        if (r.find(cmd)==-1 and r.find('\nOK\r')==-1):
                            self.pipeline = cmd
                            return 1
                        else:
                            self.pipeline = 'OK'
                            return 0
        except:
            self.pipeline = cmd
            return 1

    def sendMessage(self):
        ATZ = 'ATZ'
        AT = 'AT'
        CMGF = 'AT+CMGF=1'
        CMGW = 'AT+CMGW=' + '"' + self.recipient + '"'
        MSG = self.content
        CMSS = 'AT+CMSS='
        CMGD = 'AT+CMGD=1,4'
        content = self.content
        endContent = chr(26)

        if self.pipeline=='OK':
            self.sComm(ATZ, 16)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(ATZ, 16)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(AT, 16)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(CMGF, 16)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(CMGW, 32)
        else:
            return pipeline
        if self.pipeline=='OK':
            self.sComm(content)
        else:
            return pipeline
        if self.pipeline=='OK':
            self.sComm(endContent, 256)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            i = self.memSlot(self.ans.decode("utf-8"))
            if i.isnumeric() and self.pipeline=='OK':
                self.sComm((CMSS + i), 32)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(CMGD, 32)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(ATZ, 16)
        else:
            return pipeline
        if self.pipeline=='OK':
            self.sComm(ATZ, 16)
        else:
            return self.pipeline

        self.pipeline='OK'

        return 1

    def disconnectPhone(self):
        try:
            self.ser.close()
            return 1
        except:
            return 'Error disconnecting modem'

def sendSMS(phone, msg):
    sms = TextMessage(phone, msg)
    r = sms.connectPhone()
    if r==True:
        r = sms.sendMessage()
        if r==True:
            r = sms.disconnectPhone()
            if r==True:
                return r
        else:
            return r
    else:
        return r
