import serial
import serial.tools.list_ports
import random
import string
import copy
from time import sleep
from datetime import datetime as dt

class TextMessage:
    def __init__(self, recipient="", message="", debug=False):
        self.recipient = recipient
        self.content = message
        self.debug = debug
        self.smsnumber = None
        self.sent_dt = None
        self.ser = None
        self.pipeline = "OK"

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
            if self.debug:
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
        if self.debug:
            print('cmd:', cmd)
        try:
            r = self.ser.write(cmd.encode())
            if r:
                sleep(0.5)
                if rsize > 0:
                    r = self.ser.read(rsize)
                    self.ans = r
                    if len(r) > 0:
                        r = r.decode("utf-8")
                        if self.debug:
                            print('Modem answer:', r)
                        if cmd == 'AT+CMGL="all"\r':
                            return r
                        find_cmd = r.find(cmd)
                        find_error = r.find('ERROR')
                        find_ok = r.find('\nOK\r')
                        if find_error!=-1:
                            self.pipeline = cmd
                            return 0
                        if (find_cmd==-1 and find_ok==-1):
                            self.pipeline = cmd
                            return 0
                        else:
                            self.pipeline = 'OK'
                            return 1
                    else:
                        pass
                else:
                    pass
        except Exception as e:
            if self.debug:
                print(e)
            self.pipeline = cmd
            return 1

    def configureModem(self):
        CNMI = 'AT+CNMI=2,1,0,1,0'
        CSMP = 'AT+CSMP=49,167,0,0'
        enter = '\r'
        self.pipeline = 'OK'
        if self.pipeline=='OK':
            if self.clearmemory():
                self.pipeline='OK'
            else:
                return 0
        if self.pipeline=='OK':
            self.sComm(CNMI + enter, 32)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(CSMP + enter, 32)
        else:
            return self.pipeline
        
        
    def sendMessage(self):
        ATZ = 'ATZ'
        AT = 'AT'
        CMGF = 'AT+CMGF=1'
        CMGW = 'AT+CMGW=' + '"' + self.recipient + '"'
        CMGS = 'AT+CMGS=' + '"' + self.recipient + '"'
        MSG = self.content
        CMSS = 'AT+CMSS='
        CMGD = 'AT+CMGD=1,4'
        content = self.content
        endContent = chr(26)
        enter = '\r'
        CNMI = 'AT+CNMI=2,1,0,1,0'
        CSMP = 'AT+CSMP=49,167,0,0'

        var = self.pipeline
        
        if self.pipeline=='OK':
            self.sComm(ATZ + enter, 16)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(ATZ + enter, 16)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(AT + enter, 16)
        else:
            return self.pipeline        
        if self.pipeline=='OK':
            self.sComm(CMGF + enter, 16)
        else:
            return self.pipeline
        # if self.pipeline=='OK':
        #     self.sComm(CMGW, 32)
        if self.pipeline=='OK':
            self.sComm(CMGS + enter, 32)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            sleep(1)
            self.sComm(content[0:159], 160)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            sleep(1)
            self.sComm(endContent, 320)
        else:
            return self.pipeline
        # if self.pipeline=='OK':
        #     i = self.memSlot(self.ans.decode("utf-8"))
        #     if i.isnumeric() and self.pipeline=='OK':
        #         self.sComm((CMSS + i), 32)
        #         sleep(2)
        # else:
        #     return self.pipeline
        # if self.pipeline=='OK':
        #     self.sent_dt = dt.now()
        #     self.sComm(CMGD, 32)
        # else:
        #     return self.pipeline
        if self.pipeline=='OK':
            self.sent_dt = dt.now()
            self.sComm(ATZ + enter, 16)
        else:
            return self.pipeline
        if self.pipeline=='OK':
            self.sComm(ATZ + enter, 16)
        else:
            return self.pipeline

        # self.pipeline='OK'
        pipeline_result = self.pipeline
        if pipeline_result == 'OK':
            return 1
        else:
            return 0


    def disconnectPhone(self):
        try:
            self.ser.close()
            return 1
        except:
            return 0

    def clearmemory(self):
        CMGD = 'AT+CMGD=1,4'
        enter = '\r'
        if self.sComm(CMGD + enter, 16):
            return 1
        else:
            return 0
        

    def set_delivery_report(self, report=True):
        if report:
            cmd = "AT+CNMI=" + '2,1,0,1,0' # values to receive report
            enter = '\r'
            ans = self.sComm(cmd + enter, 24)
            # ans = self.get_answer(sleep=0.2)
            if ans:
                cmd = "AT+CSMP=" + '49,167,0,0' # values to receive report
                ans = self.sComm(cmd + enter, 24)
                # ans = self.get_answer(sleep=0.2)
            else:
                return ans
        else:
            cmd = "AT+CNMI=" + '2,1,2,1,0' # original values
            ans = self.sComm(cmd + enter, 24)
            # ans = self.get_answer(sleep=0.2)
            if ans:
                cmd = "AT+CSMP=" + '0,173,0,0' # original values
                ans = self.sComm(cmd + enter, 24)
                # ans = self.get_answer(sleep=0.2)
            else:
                return ans

    def get_delivery_report(self, phonenumber, sent, delay, exclude_sms=True):
        sleep(delay)
        cmd = 'AT+CMGL="all"'
        enter = '\r'
        ans = self.sComm(cmd + enter, 320)
        if ('AT+CMGL="all"' and 'OK' and not "+CMGL: " in ans):
            return False
        else:
            ans = ans.split("+CMGL: ")
            ans.remove(ans[0])
            ans[-1] = ans[-1].split('OK')[0]
            for elem in ans:
                rec_number = elem.split('"",')[1].split('Torpedo SMS entregue p/ ')[1].split(' (')[0].strip()
                sms_id = (elem.split(',"REC ')[0])
                delivery_date = dt.strptime((elem.split('"","')[1]).split('-')[0], '%Y/%m/%d %H:%M:%S')
                if (rec_number.strip()) in (phonenumber.strip()):
                    if ((abs(delivery_date - sent).seconds) <= delay):
                        if exclude_sms:
                            cmd = "AT+CMGD=" + str(sms_id)
                            ans = self.sComm(cmd + enter, 16)
                            if ans:
                                return True
                            else:
                                return False
                        return True
            return False

    def randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
    
    # Force delivery if Carrier denies it due Spam filter
    def force_delivery(self):
        is_delivered = False
        i = 0
        original_msg = copy.deepcopy(self.content)
        randomword = self.randomword(10)
        number = self.recipient
        while is_delivered != True :
            if i == 0:
                if len(self.content + "\r\n" + randomword) >= 160:
                    extra_len = abs(len(self.content + "\r\n" + randomword) - 160) 
                    msg = copy.deepcopy(self.content[:(len(self.content) - extra_len)])
                    msg = msg + "\r\n" + randomword
                else:
                    msg = copy.deepcopy(self.content + "\r\n" + randomword)
                self.content = copy.deepcopy(msg)
                sent = self.sendMessage()
                if sent == True:
                    is_delivered = self.get_delivery_report(number, self.sent_dt, 6)
            else:
                if i >= 3:
                    break
                randomword += self.randomword(5)
                if len(original_msg + "\r\n" + randomword) >= 160:
                    extra_len = abs(len(original_msg + "\r\n" + randomword) - 160)
                    msg = copy.deepcopy(original_msg[:(len(original_msg) - extra_len)])
                    msg = msg + '\r\n' + randomword
                else:
                    msg = original_msg + '\r\n' + randomword
                self.content = copy.deepcopy(msg)
                sent = self.sendMessage()
                if sent == True:
                    is_delivered = self.get_delivery_report(number, self.sent_dt, 6)
            i += 1
        return is_delivered


def sendSMS(phone, msg, debug=False):
    sms = TextMessage(phone, msg , debug=debug)
    r = 0
    if sms.connectPhone() == True:
        sms.configureModem()
        sms.smsnumber = phone
        if sms.sendMessage() == True:
            sent = sms.sent_dt
            is_delivered = sms.get_delivery_report(phone, sent, 6)
            if not(is_delivered):
                if sms.force_delivery() == True:
                    return sms.disconnectPhone()
            else:
                return sms.disconnectPhone()
    return r



# msg = "WARNING\n\rCAX:B:BASLER01:ImgDVFStatus-Mon = 0\n\rLimit: L=100\n\rRule: pv < L"
# msg = "WARNING\n\r1) ^RAD:Thermo.+:TotalDoseRate:Dose$ = pv ok\n\rLimit: L=1\n\rRule: pv > L\n\r2) RAD:ELSE:TotalDoseRate:Dose = 1.04225251"
# msg = "1) SI-13C4:DI-DCCT:Current-Mon = 99.918693512\n\rLimit: L=200\n\rRule: pv < L\n\r2) AS-Glob:AP-MachShift:Mode-Sts = 0\n\rLimit: L=0"
# msg = "1) SI-13C4:DI-DCCT:Current-Mon = 100.00495162\n\rLimit: L=200\n\r2) AS-Glob:AP-MachShift:Mode-Sts = 0\n\rLimit: L=0"
# msg = "1) SI-13C4:DI-DCCT:Current-Mon = 100.10985548\n\rLimit: L=420\n\r2) AS-Glob:AP-MachShift:Mode-Sts = 0\n\rLimit: L=69"
# msg = "Here we go"
# n = 124
# msg = (msg[:n]) if len(msg) > n else msg
# print(msg)
# phone = '19997397443'
# if (sendSMS(phone, msg, debug=True)):
#     print('Delivery successfull!')
# else:
#     print("Message not delivered!")