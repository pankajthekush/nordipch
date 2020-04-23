from slre.slre import RemoteSelenium
from nordipch import connect

rs = None
driver = None

def connect_vpn(vpname):
    _,_,_,status = connect(serverdomain=vpname)

    if status:
        run_chrome()
    else:
        print('can not connect to vpn')


def run_chrome():
    rs = RemoteSelenium()
    driver = rs.driver
    driver.get('https://www.google.com/search?q=hello+world')

    

import os
if __name__ == "__main__":
    vpnfile = os.path.join('ovpn_tcp','us4633.nordvpn.com.tcp.ovpn')
    connect_vpn(vpname=vpnfile)
