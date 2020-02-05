import requests
import json
import sys
from time import sleep
import ipaddress
import subprocess
import logging
import os
import time
import csv
import requests

current_path = os.path.dirname(os.path.realpath(__file__))
last_run_file = os.path.join(current_path,'LASTRUN.txt')
block_file = os.path.join(os.getcwd(),'BLOCKED.txt')

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
    current_ip = current_api_text
    if last_digit == 0:
        last_tow_digit = int(current_api_text[-2:])
        last_digit = str(int(last_tow_digit)-1)
        v_ip = current_api_text[:-2] + last_digit
        logging.debug(f"Current IP : {v_ip}")
        return [v_ip,current_ip]

    else:
        last_digit = str(int(last_digit-1))
        v_ip = current_api_text[:-1] + last_digit
        logging.debug(f"Current IP : {v_ip}")
        return [v_ip,current_ip]

def status():
    nord_api_text = return_nord_json()
    if isinstance(nord_api_text,Exception):
        return nord_api_text
    nord_ip_table = json.loads(nord_api_text)
    v_ip = get_current_ip()
    id = None
    for ip_data in nord_ip_table:
        ip_address = ip_data['ip_address'].strip()
        if ip_address in v_ip:
            id = ip_data['id']
            logging.debug(f"CONNECTED, {ip_address},{id}")
            return "CONNECTED", ip_address,id
    logging.debug(f"DISCONNECTED, {ip_address},{id}")
    return "DISCONNECTED" , ip_address,id

def connect(serverid=947373,run_time_limit=10,OVER_RIDE_TIME = False,ip_file = 'ips.csv'):

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
    serverid = return_csv_line(ip_file)
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
    with open(last_run_file,'w') as f:
        f.write(str(time.time()))

def recent_run(time_limit=10):

    current_time = time.time()

    if not os.path.exists(last_run_file):
        write_time()

    with open(last_run_file,'r') as f:
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

def send_response():
    while (os.path.exists('BLOCKED.txt')):
            logging.debug("Waiting IP to be changed")

def scrapy_call(response,ip_file='ips.csv',run_time_limit=10,bad_response = [404,503]):
    
    if os.path.exists('RESPONSE.LOCK') and os.path.exists('BLOCKED.txt'):
        print("COnnection is progress , skipping")
        input("response lock")
        sleep(10)
        return response
    
    if response.status in bad_response:
        r_file = open('RESPONSE.LOCK' ,'w')
        r_file.close()

        is_changed_for_this_link = is_already_done(response.url,response.status)

        b_file = open('BLOCKED.txt' ,'w')
        b_file.close()
        if not is_changed_for_this_link:
            connect(run_time_limit=2,ip_file='ips.csv')
    
            try:
                os.remove('BLOCKED.txt')
            except Exception:
                pass
                
        else:
            try:
                os.remove('BLOCKED.txt')
            except Exception:
                pass

    else:
        try:
            os.remove('BLOCKED.txt')
        except Exception:
            pass
        
    with open('ip_url.csv',mode='a',encoding='utf-8') as iplog:
        iplog.write(f'{response.url},{response.status}\n')
    
    try:
        os.remove('RESPONSE.LOCK')
    except Exception:
        pass
    
    return response

def return_csv_line(in_input_file='ips.csv'):
   
    f =  open(in_input_file,'r',encoding='utf-8-sig',newline='')
    csvfile = csv.DictReader(f)
    link = ''
    lidata = list()

    for row in csvfile:
        status = row['status']
        if status == 'DO' and link == '':
            row['status'] = 'COMPLETE'
            link = row['id']
        lidata.append(row)
    f.close()
    
    with open(in_input_file,'w',newline='',encoding='utf8') as f:
        dictcwriter = csv.DictWriter(f,lidata[0].keys())
        dictcwriter.writeheader()
        dictcwriter.writerows(lidata)
    return link


def is_already_done(in_link,in_status):

    if not os.path.exists('ip_url.csv'):
        return False

    in_link,in_status = str(in_link), str(in_status)
    with open('ip_url.csv',encoding='utf-8',newline='') as f:
        csvfile = csv.reader(f)

        for row in csvfile:
            link = row[0]
            status = row[1]
            if link == in_link and status == in_status:
                return True
           
    return False


def check_file_connect(filename='NEEDCHANGE.LOCK'):
    while True:
        if os.path.exists(filename):
            logging.debug("Will Change the IP")
            connect(run_time_limit=2,ip_file='ips.csv')
            os.remove(filename)
            logging.debug("IP is Changed")
            
        else:
            logging.debug("IP will not be changed")
            sleep(2)



if __name__ == "__main__":
    import requests
    #rs = requests.get("https://www.yelp.com/findfriends")
    #print(scrapy_call(run_time_limit=3000,OVER_RIDE_TIME=False,response=rs,statuscodes=[200]))
    print(return_csv_line('ips.csv'))
