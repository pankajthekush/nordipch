from requests import session
import os
import sys 
import requests
import json
import time
import random

production = True
current_path = os.path.dirname(os.path.realpath(__file__))

class NProxy:
    def __init__(self):
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                #'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'}
        self.useragents = self.get_ua_file()
        self.Session = session()
        self.Session.headers = self.headers
        self.jsonnord = None
        self.getipfile()
        self.cleanproxylist()
        self.get_ua_file()

    def download_file(self,link='https://api.nordvpn.com/server',filename = 'nordip.json'):
        
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
        is_available = os.path.exists('nordip.json')
        
        if is_available and not production:
            with open('nordip.json','r',encoding='utf-8') as f:
                jobj = json.load(f)
                self.jsonnord = jobj
                return 0


        if is_available:
            os.remove('nordip.json')
            self.download_file()
            with open('nordip.json','r',encoding='utf-8') as f:
                jobj = json.load(f)
                self.jsonnord = jobj
        else:
            self.download_file()
            with open('nordip.json','r',encoding='utf-8') as f:
                jobj = json.load(f)
                self.jsonnord = jobj


    def nordjson(self):
        jobj = None
        with open('nordip.json','r',encoding='utf-8') as f:
            jobj = json.load(f)
            self.jsonnord = jobj
        return jobj
    
    def get_random_proxy(self):
        dict_pxy = None
        dict_proxy = random.choice(self.jsonnord)
        dict_pxy = dict_proxy['id']
        self.jsonnord.remove(dict_proxy) #remove this proxy from list
        self.get_random_ua()
        return dict_pxy

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
            


if __name__ == "__main__":
    npx = NProxy()
    print(npx.cleanproxylist())
