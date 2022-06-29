from requests import session
import os
import sys 
import requests
import json
import time
import random
import zipfile
import shutil
import glob
from shelper import config_file
from itertools import cycle, groupby, accumulate
import socket
import ipaddress
from time import sleep

import logging, sys
# logging
# logging, I know this is comple BS code , but google could not help me
formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)-8s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)



production = True
current_path = os.path.dirname(os.path.realpath(__file__))
opvn_zip_path = os.path.join(current_path,'ovpn.zip')
ovpn_tcp = os.path.join(current_path,'ovpn_ipvanish')
nord_json_file = 'nordip.json'
certificate_path = os.path.join(current_path,'ovpn_ipvanish','ca.ipvanish.com.crt')


class IProxy:
    def __init__(self,production = True):
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                #'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'}
        self.config = config_file()
        self.production = production
        self.Session = session()
        self.Session.headers = self.headers
        self.jsonnord = None
        self.download_ovpn_files()
        self.nordjson()
        self.cleanproxylist()
        self.groupedproxies = None
        self.recyle_ip = self.config['recycle_proxy'].upper()
        self.group_proxies()
        
  
    def download_file(self,link='https://api.nordvpn.com/server',filename = nord_json_file):
        print('\n')
        print(f'Downloading...')
        print(filename)

        resp = self.Session.get(link,stream=True)
        handle = open(filename,'wb')

        for chunk in resp.iter_content(chunk_size=512):
            if chunk:
                handle.write(chunk)
                sys.stdout.write('\r.')
                sys.stdout.flush()
                sys.stdout.write('\r..')
                sys.stdout.flush()
                sys.stdout.write('\r...')

        handle.close()
                
    
    def cleanproxylist(self):
        acceptable_flag = list()

        """
        due to docker requirements, need to get the country flag from env

        """
        is_dockerized = self.config['is_dockerized']
        
        list_countries = [] 
        os_env_country= None

        """
        don't loose your mind testig it , when you export a variable while running program
        it is not visible to current shell
        """
        if is_dockerized:
            while os_env_country is None:
                os_env_country = os.getenv('ip_country')
                logger.info(f'getting country from env {os_env_country}') 
                sleep(10)
            
            list_countries = os_env_country.split()
        else:
            list_countries = self.config['list_country_flags']

        acceptable_flag = [cnt.upper() for cnt in list_countries]
        if len(acceptable_flag) == 0:
            raise ValueError('need country flags,edit the json now')

        list_proxy = []
        for proxy in self.jsonnord:
            flag = proxy['flag']
            if flag.upper() in acceptable_flag:
                list_proxy.append(proxy)
        self.jsonnord = list_proxy


    def getipfile(self):
        is_available = os.path.exists(nord_json_file)
        
        # if is_available and self.production == False:
        #     self.nordjson()
        #     return 0
        #commenting as i want the file to be downloadedevery time, it runs

        if is_available:
            os.remove(nord_json_file)
            self.download_file(filename=nord_json_file)
            time.sleep(3)

        else:
            self.download_file(filename=nord_json_file)
            time.sleep(3)



    def nordjson(self):
        jobj = None
        jobj = self.get_local_ovpns()
        self.jsonnord = jobj

    
        
    def get_local_ovpns(self):


        #since load is not available publicily
        #taking all ovpn file
        all_tcp = os.listdir(ovpn_tcp)
        
        jobjlist = list()
        for tcp_file in all_tcp:
    
            if tcp_file == 'ca.ipvanish.com.crt':
                continue
            
            flag = tcp_file.split('-')[1].upper()
            jobj = dict()
            jobj['id'] = tcp_file
            jobj['domain'] = str(tcp_file).replace('.tcp.ovpn','')
            jobj['flag'] = flag
            jobj['load'] = 10
            jobjlist.append(jobj)
        return jobjlist
        

    def get_random_proxy(self,auto_update='YES'):        
        pxy_domain = next(self.groupedproxies)
        return pxy_domain

    
    
    def download_ovpn_files(self):
        tcp_exists = os.path.exists(ovpn_tcp)
        

        if tcp_exists and self.production == False:
            return 0
    
        if os.path.exists(opvn_zip_path):
            os.remove(opvn_zip_path)
       
        if os.path.exists(ovpn_tcp):
            shutil.rmtree(ovpn_tcp)

        self.download_file('https://www.ipvanish.com/software/configs/configs.zip',opvn_zip_path)

        with zipfile.ZipFile(opvn_zip_path, 'r') as zip_ref:
            zip_path = os.path.join(current_path,'ovpn_ipvanish')
            zip_ref.extractall(zip_path)
        tcp_files = glob.glob(os.path.join(ovpn_tcp,'*.ovpn'))

        certificate_text = None
        with open(certificate_path,'r',encoding='utf-8') as f:
            certificate_text = f.read()
        new_line = '\n'
        certificate_text = f'<ca>{new_line}{certificate_text}{new_line  }</ca>{new_line}'
        
        for file in tcp_files:
            ovpn_txt = None
            if 'ca.ipvanish.com.crt' in str(file):
                #donot process certificate file
                continue

            with open(file,'a') as f:
                f.write('management localhost 7505\n')
                if sys.platform == 'linux':
                    #in case of linux
                    f.write(certificate_text)
                    f.write('script-security 2\n')
                    f.write('up /etc/openvpn/update-resolv-conf\n')
                    f.write('down /etc/openvpn/update-resolv-conf')
                else:
                    f.write(certificate_text)
                    #windows support
            #read ovpn file text ,and replace certificate string
            with open(file,'r') as f:
                ovpn_txt = f.read()    
                ovpn_txt = ovpn_txt.replace('ca ca.ipvanish.com.crt','')
            
            with open(file,'w') as f:
                f.write(ovpn_txt)

        os.remove(opvn_zip_path)



    def group_proxies(self):
       
        ip_list = list()
        all_ip_list = None

        for proxy in self.jsonnord:
            ip_domain = proxy['domain']
            ip_list.append(ip_domain)

        random.shuffle(ip_list)  

        if self.recyle_ip == 'YES':
            all_ip_list = cycle(ip_list)
        else:
            all_ip_list = iter(ip_list)
        self.groupedproxies = all_ip_list
           


def get_network_ip(ip):
    ip_with_subnet = ip+'/'+'255.255.255.0'
    net = ipaddress.ip_network(ip_with_subnet, strict=False)
    network_ip = (net.network_address)
    return network_ip




import time
if __name__ == "__main__":
    npx = IProxy(production=False)
    npx.download_ovpn_files()
    # print(npx.get_random_proxy())
    # # npx.download_file('https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip','ovpn.zip')
    # # with zipfile.ZipFile('ovpn.zip', 'r') as zip_ref:
    # #     zip_ref.extractall(str(os.getcwd()))
