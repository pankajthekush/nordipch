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

production = True
current_path = os.path.dirname(os.path.realpath(__file__))
opvn_zip_path = os.path.join(current_path,'ovpn.zip')
ovpn_tcp = os.path.join(current_path,'ovpn_tcp')
ovpn_udp = os.path.join(current_path,'ovpn_udp')
nord_json_file = 'nordip.json'



class NProxy:
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
        self.getipfile()
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
        min_load = int(self.config['min_load'])
        max_load = int(self.config['max_load'])
        list_countries = self.config['list_country_flags']
        acceptable_flag = [cnt.upper() for cnt in list_countries]
        if len(acceptable_flag) == 0:
            raise ValueError('need country flags,edit the json now')

        list_proxy = []
        for proxy in self.jsonnord:
            flag = proxy['flag']
            load = proxy['load']
            if flag.upper() in acceptable_flag and load >= min_load and load <= max_load:
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
        with open(nord_json_file,'r',encoding='utf-8') as f:
            jobj = json.load(f)
            if len(jobj) < 100:
                print("bad api endpoint ,falling back to local files")
                jobj = self.get_local_ovpns()
            self.jsonnord = jobj

    
        
    def get_local_ovpns(self):
        all_tcp = os.listdir(ovpn_tcp)
        
        jobjlist = list()
        for tcp_file in all_tcp:
            flag = tcp_file[:2].upper()
            jobj = dict()
            jobj['id'] = tcp_file
            jobj['domain'] = str(tcp_file).replace('.tcp.ovpn','')
            jobj['flag'] = flag
            jobj['load'] = 10
            jobjlist.append(jobj)
        return jobjlist
        

    def get_random_proxy(self,auto_update='YES'):
        
        pxy_id,pxy_domain = next(self.groupedproxies)
        return pxy_id,pxy_domain

    
    
    def download_ovpn_files(self):
        tcp_exists = os.path.exists(ovpn_tcp)
        udp_exists = os.path.exists(ovpn_udp)

        if tcp_exists and udp_exists and self.production == False:
            return 0
    
        if os.path.exists(opvn_zip_path):
            os.remove(opvn_zip_path)
       
        if os.path.exists(ovpn_tcp):
            shutil.rmtree(ovpn_tcp)
        if os.path.exists(ovpn_udp):
            shutil.rmtree(ovpn_udp)

        self.download_file('https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip',opvn_zip_path)
        with zipfile.ZipFile(opvn_zip_path, 'r') as zip_ref:
            zip_ref.extractall(current_path)
        tcp_files = glob.glob(os.path.join(ovpn_tcp,'*.ovpn'))
        udP_files = glob.glob(os.path.join(ovpn_udp,'*.ovpn'))
        
        for file in tcp_files:
            with open(file,'a') as f:
                f.write('management localhost 7505\n')
                
               
                if sys.platform == 'linux':
                    #in case of linux
                    f.write('script-security 2\n')
                    f.write('up /etc/openvpn/update-resolv-conf\n')
                    f.write('down /etc/openvpn/update-resolv-conf')
       
        for file in udP_files:
            with open(file,'a') as f:
                f.write('management localhost 7505\n')

                if sys.platform == 'linux':
                    #in case of linux
                    f.write('script-security 2\n')
                    f.write('up /etc/openvpn/update-resolv-conf\n')
                    f.write('down /etc/openvpn/update-resolv-conf')

        os.remove(opvn_zip_path)



    def group_proxies(self):
        list_grouped_ips = list()
        all_ip_list = list()
       
        ip_list = list()
    
        for proxy in self.jsonnord:
            ip_addr = proxy['ip_address']
            ip_list.append(ip_addr)
          
        #https://stackoverflow.com/a/6545090/3025905
        #sorted_ip = sorted(ip_list, key=lambda item: socket.inet_aton(item))

        #https://www.lesinskis.com/python_sorting_IP_addresses.html
        sorted_ip = sorted(ip_list,key=ipaddress.IPv4Address)
        
        #group now
        for group,ips in groupby(sorted_ip,key=get_network_ip):
            dictgroup =dict()
            ips = list(ips)
            random.shuffle(ips)
            dictgroup[group] =  ips
            list_grouped_ips.append(dictgroup)
        
        random.shuffle(list_grouped_ips)
        for item in list_grouped_ips:
            for _,v in item.items():
                for ip in v:
                    for proxy in self.jsonnord:
                        ip_addr = proxy['ip_address']
                        pxy_domain = proxy['domain']
                        if ip_addr == ip:
                            tuple_data = (ip,pxy_domain)
                            all_ip_list.append(tuple_data)
                            break
        if self.recyle_ip == 'YES':
            all_ip_list = cycle(all_ip_list)
        else:
            all_ip_list = iter(all_ip_list)
        self.groupedproxies = all_ip_list
           


def get_network_ip(ip):
    ip_with_subnet = ip+'/'+'255.255.255.0'
    net = ipaddress.ip_network(ip_with_subnet, strict=False)
    network_ip = (net.network_address)
    return network_ip




import time
if __name__ == "__main__":
    npx = NProxy(production=False)
    # npx.download_ovpn_files()
    # print(npx.get_random_proxy())
    # # npx.download_file('https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip','ovpn.zip')
    # # with zipfile.ZipFile('ovpn.zip', 'r') as zip_ref:
    # #     zip_ref.extractall(str(os.getcwd()))

    while True:
        print(npx.get_random_proxy())
        time.sleep(1)
