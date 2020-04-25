from slre.slre import RemoteSelenium
from nordipch import connect

rs = None
driver = None

def connect_vpn(vpname,user_agent):
    #rs.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent":"python 2.7", "platform":"Windows"})
    
    _,_,_,status = connect(serverdomain=vpname)

    if status:
        run_chrome(user_agent)
    else:
        print('can not connect to vpn')


def run_chrome(user_agent):
    rs = RemoteSelenium()
    driver = rs.driver
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent":user_agent})
    driver.get('https://www.google.com/search?q=hello+world')
    input('hit enter to quit and work with next ip')
    

import os
if __name__ == "__main__":

    vpnserver = input('enter vpn servername :')
    user_agent = input('enter user agent :')
    vpnfile = os.path.join('ovpn_tcp',vpnserver)
    connect_vpn(vpname=vpnfile,user_agent=user_agent)
