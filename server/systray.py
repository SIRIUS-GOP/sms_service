
import pystray, socket, config
from pystray import MenuItem as item
from PIL import Image
from time import sleep
from os import path

class tray:
    c_icon = None
    def __init__(self, vstart=None, vstop=None, vexit=None):
        self.vstart = vstart
        self.vstop = vstop
        self.vexit = vexit
    
    def start(self):
        self.vstart.value = True

    def stop(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = config.read("IP", "server_ip")
            port = int(config.read("IP", "server_port"))
            server_address = (ip, port)
            sock.settimeout(5)
            sock.connect(server_address)
        except:
            return 1
        finally:
            self.vstart.value = False
            self.vstop.value = True

    def exit(self):
        print('systray_run OFF')
        self.stop()
        self.vexit.value = True
        self.c_icon.stop()

    def run_icon(self):
        try:
            dir_path = path.dirname(path.realpath(__file__)) #current folder application path
            image_path = path.join(dir_path, 'smartphone.png')
            image = Image.open(image_path)
            menu = (item('Start Server', self.start), item('Stop Server', self.stop), item('Exit Service', self.exit))
            icon = pystray.Icon("sms", image, "SMS Service", menu)
            self.c_icon = icon
            icon.run()
        except:
            #print('Icon creation error')
            exit()

def systray_run(vstart, vstop, vexit):
    t = tray(vstart, vstop, vexit)
    #print('icon created')
    t.run_icon()
