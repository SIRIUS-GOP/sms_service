import requests
from client_venv.app import getconfig

def verifyPV(pv):
    url = getconfig.read('EPICS','url')
    pvlist = requests.get(url, allow_redirects=True, verify=False)

    if pvlist.find(pv):
        return 1
    else:
        return 0

verifyPV('TS-01:PS-CV-1:Current-Mon')