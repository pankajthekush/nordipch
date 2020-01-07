import requests
import json
import sys
from time import sleep
import ipaddress
import subprocess
import logging


logging.basicConfig(filename='nordipch.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s:%(lineno)d')

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
            logging.debug(f"{error}, Retrying : {retry_count}...")
            retry_count += 1
            if retry_count >= max_retry_count:
                logging.debug(error)
                logging.debug("Nord API JSON request : Fail")
                return error
    logging.debug("Nord API JSON request : Success")
    return nord_api_text
    
def  get_current_ip():
    current_api_text = None
    retry_count = 1
    max_retry_count = 30

    while (current_api_text is None and retry_count < max_retry_count) or len(current_api_text) == 0:
        try:
            current_api_text =requests.get(current_ip_api).text.strip()
            ipaddress.ip_address(current_api_text)  #This validates the IP returned
        except Exception as error:
            sleep(3)
            logging.debug(f"Error {error}.Retrying {retry_count}...")
            retry_count += 1
            if retry_count >= max_retry_count:
                logging.debug(error)
                return error
    
    last_digit=  int(current_api_text[-1:])
    if last_digit == 0:
        last_tow_digit = int(current_api_text[-2:])
        last_digit = str(int(last_tow_digit)-1)
        v_ip = current_api_text[:-2] + last_digit
        logging.debug(f"Current IP : {v_ip}")
        return v_ip

    else:
        last_digit = str(int(last_digit-1))
        v_ip = current_api_text[:-1] + last_digit
        logging.debug(f"Current IP : {v_ip}")
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
            logging.debug(f"CONNECTED, {v_ip},{id}")
            return "CONNECTED", v_ip,id
    logging.debug(f"DISCONNECTED, {v_ip},{id}")
    return "DISCONNECTED" , v_ip,id

def connect(serverid=947373):
    win_cmd = f'nordvpn -c -i {serverid}'
    subprocess.Popen(win_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    #Wait till connected
    for i in range(10):
        try:
            state,_,_ = status()
        except TypeError as error:
            logging.debug("Could Not Connect , re-tries exceeded {}".format(error))
            return ("Could Not Connect , re-tries exceeded {}".format(error))

        if state == 'DISCONNECTED':
            logging.debug(f'Trying Connection : {i}...')
            sleep(3)
            state,_,_ = status()
        else:
            retstatus = status()
            logging.debug(retstatus)
            return retstatus
    retstatus = status()
    logging.debug(retstatus)
    return retstatus



def disconnect():
    subprocess.Popen('nordvpn -d',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    retstatus = status()
    logging.debug(retstatus)
    return retstatus
    
if __name__ == "__main__":
    print(disconnect())
