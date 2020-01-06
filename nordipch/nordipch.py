import requests
import json
import sys
from time import sleep
import ipaddress
import subprocess


nord_api = "https://api.nordvpn.com/server"
current_ip_api = "http://myip.dnsomatic.com"

def return_nord_json():
    nord_api_text = None
    retry_count = 1
    max_retry_count = 30

    while nord_api_text is None and retry_count < max_retry_count:
        try:
            nord_api_text = requests.get(nord_api).text
        except Exception as error:
            sleep(3)
            print(f"Server Not Found.Retrying {retry_count}...")
            retry_count += 1
            if retry_count >= max_retry_count:
                return error
    return nord_api_text
    
def  get_current_ip():
    current_api_text = None
    retry_count = 1
    max_retry_count = 30

    while current_api_text is None and retry_count < max_retry_count:
        try:
            current_api_text =requests.get(current_ip_api).text.strip()
            ipaddress.ip_address(current_api_text)  #This validates the IP returned
        except Exception as error:
            sleep(3)
            print(f"Current IP  Not Determined.Retrying {retry_count}...")
            retry_count += 1
            if retry_count >= max_retry_count:
                return error
    
    last_digit=  int(current_api_text[-1:])
    if last_digit == 0:
        last_tow_digit = int(current_api_text[-2:])
        last_digit = str(int(last_tow_digit)-1)
        v_ip = current_api_text[:-2] + last_digit
        return v_ip

    else:
        last_digit = str(int(last_digit-1))
        v_ip = current_api_text[:-1] + last_digit
        return v_ip


    


def status():
    nord_api_text = return_nord_json()
    if isinstance(nord_api_text,Exception):
        return nord_api_text
    nord_ip_table = json.loads(nord_api_text)
    v_ip = get_current_ip()
    id = None
    for ip_data in nord_ip_table:
        ip_address = ip_data['ip_address'].strip()
        if v_ip == ip_address:
            id = ip_data['id']
            return "CONNECTED", v_ip,id
    return "DISCONNECTED" , v_ip,id

def connect(serverid=947373,disconnect_current = True):
    win_cmd = f'nordvpn -c -i {serverid}'
    subprocess.Popen(win_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    #Wait till connected
    for i in range(10):
        state,_,_ = status()
        if state == 'DISCONNECTED':
            print(f'Waiting for connection {i}')
            sleep(3)
            state,_,_ = status()
        else:
            return status()
    return status()



def disconnect():
    subprocess.Popen('nordvpn -d',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    return status()
    
if __name__ == "__main__":
    print(connect())
