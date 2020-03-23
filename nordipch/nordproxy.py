from requests import session
import os
import sys 
import requests
import json
import time
import random

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
        self.Session = session()
        self.Session.headers = self.headers
        self.jsonnord = None
    
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
                
    
    def getipfile(self):
        last_updated = None
        is_available = os.path.exists('nordip.json')
        last_updated_day = None
        current_day = None
        
        if is_available:
            last_updated = os.path.getmtime('nordip.json')
            last_updated_day = time.localtime(last_updated)[2]
            current_day =  time.localtime(time.time())[2]
            if current_day == last_updated_day:            
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
        dict_proxy = random.choice(self.jsonnord)
        print(dict_proxy)



if __name__ == "__main__":
    npx = NProxy()
    npx.getipfile()
    npx.get_random_proxy()
