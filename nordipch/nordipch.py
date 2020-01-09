import requests
import json
import sys
from time import sleep
import ipaddress
import subprocess
import logging
import os
import time

logging.basicConfig(filename='nordipch.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s:%(lineno)d')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s:%(lineno)d')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

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

def connect(serverid=947373,run_time_limit=10,OVER_RIDE_TIME = False):


    is_recent_run = recent_run(run_time_limit)

    #If run recently , then do  return and exit
    if is_recent_run and OVER_RIDE_TIME == False:
        return ("RECENT","RECENT","RECENT") 
    else:
        pass

    if os.path.exists('CONN.LOCK'):
        logging.debug("Connection still in progress , Aborting...")
        return ("INPROGRESS","INPROGRESS","INPROGRESS")

    with open("CONN.LOCK",'w') as f:
        f.write("CONNINPROGRESS")

    #Disconnect First
    logging.debug("Disconnecting..")
    subprocess.Popen("nordvpn -d",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    #wait 5 Seconds for disconnection
    time.sleep(5)
    logging.debug("Start Connect..")
    win_cmd = f'nordvpn -c -i {serverid}'
    subprocess.Popen(win_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    #Wait till connected
    for i in range(10):
        try:
            state,_,_ = status()
        except TypeError as error:
            logging.debug("Could Not Connect , re-tries exceeded {}".format(error))
            return ("ERROR",'ERROR','ERROR')

        if state == 'DISCONNECTED':
            logging.debug(f'Trying Connection : {i}...')
            sleep(3)
            write_time()
            state,_,_ = status()
        else:
            retstatus = status()
            logging.debug(retstatus)
            try:
                os.remove('CONN.LOCK')
            except:
                pass
            write_time()
            return retstatus
    
    retstatus = status()
    logging.debug(retstatus)

    try:
        os.remove('CONN.LOCK')
    except:
        pass
    write_time()
    return retstatus



def write_time():
    with open("LASTRUN.txt",'w') as f:
        f.write(str(time.time()))

def recent_run(time_limit=10):
    current_time = time.time()
    with open('LASTRUN.txt','r') as f:
        last_time_run = float(f.readline())
        difference_in_time = current_time -last_time_run
        total_time = int(difference_in_time)
        if total_time > time_limit:
            return False
        else:
            logging.debug(f"Recent Run last run {total_time}s ago , Threshold time {time_limit}s")
            return True

def disconnect():
    subprocess.Popen('nordvpn -d',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    retstatus = status()
    logging.debug(retstatus)
    return retstatus

def scrapy_call(response,statuscodes = None,run_time_limit=10,OVER_RIDE_TIME=False):
    response_code = response.status
    if response_code in statuscodes:
        logging.debug(f"Bad response :{response_code}")
        
        if os.path.exists('BLOCKED.txt'):
            logging.debug("Bocked file already exists , skipping IP Change")
            time.sleep(10)
            return("BLOCKEDFILE","BLOCKEDFILE","BLOCKEDFILE")

        else:
            with open('BLOCKED.txt' ,'w') as f:
                f.write('BLOCKED')
                logging.debug("Calling connect method of Nord IP Changer")
                status = connect(run_time_limit=run_time_limit,OVER_RIDE_TIME=False)
                return status
    else:
        try:
            os.remove('BLOCKED.txt')
        except Exception as error:
            logging.debug(error)
        return("GOODREQ","GOODREQ","GOODREQ")


if __name__ == "__main__":
    import requests
    rs = requests.get("https://www.yelp.com/findfriends")
    print(scrapy_call(run_time_limit=3000,OVER_RIDE_TIME=False,response=rs,statuscodes=[404]))
