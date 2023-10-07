import serial
import serial.tools.list_ports
from time import sleep

class TextMessage:
    def __init__(self, recipient="", message=""):
        self.recipient = recipient
        self.content = message

    pipeline = "OK"
    ans = b''
        
    def get_port(self):
        modem_port = serial.tools.list_ports.grep("ZTE Modem Device")
        aux = []
        for p in modem_port:
            aux.append(p)
        if len(aux) == 1:
            modem_port_name = aux[0].name
            return modem_port_name
        else:
            modem_port_name = aux[-1].name
            return modem_port_name
            
    def connectPhone(self):
        try:
            modem_port = self.get_port()
            print('modem_port', modem_port)
            self.ser = serial.Serial(modem_port, 115200, timeout=2)
            sleep(1)
            return 1
        except:
            # print('Error connecPhone')
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
        print('cmd:', cmd)
        try:
            r = self.ser.write((cmd + '\r').encode())
            if r:
                sleep(1)
                if rsize > 0:
                    r = self.ser.read(rsize)
                    self.ans = r
                    if len(r) > 0:
                        r = r.decode("utf-8")
                        print('Modem answer:', r)
                        if (r.find(cmd)==-1 and r.find('\nOK\r')==-1):
                            self.pipeline = cmd
                            return 1
                        else:
                            self.pipeline = 'OK'
                            return 0
                    else:
                        pass
                        # print('len(r) < 0', r)
                else:
                    pass
                    # print('error on write to modem')
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
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(content)
        else:
            return self.pipeline
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
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(ATZ, 16)
        else:
            return self.pipeline

        # self.pipeline='OK'

        if self.pipeline == 'OK':
            return 1
        else:
            return 0

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

# msg = "WARNING\n\rCAX:3:BASLER01:ImgDVFStatus-Mon = 0\n\rLimit: L=100\n\rRule: pv < L"
# msg = "WARNING\n\r1) ^RAD:Thermo.+:TotalDoseRate:Dose$ = pv ok\n\rLimit: L=1\n\rRule: pv > L\n\r2) RAD:ELSE:TotalDoseRate:Dose = 1.04225251"
# msg = "WARNING\n\rSI-13C4:DI-DCCT:Current-Mon = 99.918693512\n\rLimit: L=200\n\rRule: pv < L"
# n = 124
# msg = (msg[:n]) if len(msg) > n else msg
# print(msg)
# print(sendSMS('19997397443', msg))