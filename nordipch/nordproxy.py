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

production = True
current_path = os.path.dirname(os.path.realpath(__file__))
opvn_zip_path = os.path.join(current_path,'ovpn.zip')
ovpn_tcp = os.path.join(current_path,'ovpn_tcp')
ovpn_udp = os.path.join(current_path,'ovpn_udp')
nord_json_file = os.path.join(current_path,'nordip.json')


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
        self.production = production
        self.useragents = self.get_ua_file()
        self.get_random_ua()
        self.Session = session()
        self.Session.headers = self.headers
        self.jsonnord = None
        self.download_ovpn_files()
        self.getipfile()
        self.cleanproxylist()
        self.get_ua_file()
        
  
    def download_file(self,link='https://api.nordvpn.com/server',filename = nord_json_file):
        print('\n')
        print(f'Downloading...')

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
        acceptable_flag = ['US']
        list_proxy = []
        for proxy in self.jsonnord:
            flag = proxy['flag']
            load = proxy['load']
            if flag in acceptable_flag and load <= 80:
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
            self.nordjson()
        else:
            self.download_file(filename=nord_json_file)
            time.sleep(3)
            self.nordjson()


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
        

    def get_random_proxy(self,auto_update=True):
        dict_proxy = random.choice(self.jsonnord)
        pxy_id = dict_proxy['id']
        pxy_domain = dict_proxy['domain']

        #do not remove proxy as per request
        if auto_update:
            self.jsonnord.remove(dict_proxy) #remove this proxy from list
        else:
            pass

        self.get_random_ua()
        return pxy_id,pxy_domain

    def get_ua_file(self):
        useragents = list()
        file_path = os.path.join(current_path,'ua','ua.csv')
        with open(file_path,'r',encoding='utf-8') as f:
            useragents = [ua.strip() for ua in f.readlines()]
        return useragents
    
    def get_random_ua(self):
        ua = random.choice(self.useragents)
        with open('ua.txt','w',encoding='utf-8') as f:
            f.write(ua)
        self.useragents.remove(ua)
        return ua
    
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
                f.write('management localhost 7505')
        for file in udP_files:
            with open(file,'a') as f:
                f.write('management localhost 7505')

        os.remove(opvn_zip_path)

def get_random_ua2():
    useragents = list()
    file_path = os.path.join(current_path,'ua','ua.csv')

    with open(file_path,'r',encoding='utf-8') as f:
        useragents = [ua.strip() for ua in f.readlines()]
    return useragents


if __name__ == "__main__":
    # npx = NProxy(production=False)
    # npx.download_ovpn_files()
    # print(npx.get_random_proxy())
    # # npx.download_file('https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip','ovpn.zip')
    # # with zipfile.ZipFile('ovpn.zip', 'r') as zip_ref:
    # #     zip_ref.extractall(str(os.getcwd()))
    print(get_random_ua2())
