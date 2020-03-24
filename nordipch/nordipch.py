import requests
import json
import sys
from time import sleep
import ipaddress
import subprocess

import os
import time
import csv
import requests
import click
import inspect
import glob

cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

from norddb import return_nord_id
current_path = os.path.dirname(os.path.realpath(__file__))
last_run_file = os.path.join(current_path,'LASTRUN.txt')
block_file = os.path.join(os.getcwd(),'BLOCKED.txt')


nord_api = "https://api.nordvpn.com/server"
current_ip_api = "http://myip.dnsomatic.com"

def return_nord_json():
    f = open(os.path.join(current_path,'nordip.json'),'rb')
    f_content = f.read()
    f_content = f_content.decode("utf-8")
    return f_content
    
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
            print(f"Error {error}.Retrying {retry_count}...")
            retry_count += 1
            if retry_count >= max_retry_count:
                print(error)
                return error
    
  
    current_ip = current_api_text
    
    last_suffix = current_ip.split(".")[-1:][0]
    first_suffix = current_ip.split(".")[:-1]
    
    suffix_succ = int(last_suffix)+1
    suffix_pred = int(last_suffix) - 1

    base_ip = ".".join(ip for ip in first_suffix)
    next_ip = base_ip +"." + str(suffix_succ)
    prev_ip = base_ip + "."+ str(suffix_pred)
    

    return [prev_ip,current_ip,next_ip]

   
def status():

    nord_api_text = return_nord_json()
    if isinstance(nord_api_text,Exception):
        return nord_api_text
    
    nord_ip_table = json.loads(nord_api_text)
    v_ip = get_current_ip()
    id = None
    for ip_data in nord_ip_table:
        
        ip_address = str(ip_data['ip_address'].strip())
        if ip_address in v_ip:
            id = ip_data['id']
            print(f"CONNECTED, {ip_address},{id}")
            return "CONNECTED", ip_address,id
        else:
            for ip in v_ip:
                id = ip_data['id']
                first_suffix_ip = ip.split(".")[:-1]
                base_ip = ".".join(ip for ip in first_suffix_ip)
                if base_ip in ip_address:
                    return "CONNECTED", ip_address,id


    print(f"DISCONNECTED, {ip_address},{id}")
    return "DISCONNECTED" , ip_address,id

def connect(serverid=None,run_time_limit=10,OVER_RIDE_TIME = False,nord_table_name=None,lang=None,region=None,ignore_current_conn=False,keep_blockd=False):
    
    is_recent_run = recent_run(run_time_limit)
    #If run recently , then do  return and exit
    if is_recent_run and OVER_RIDE_TIME == False:
        return ("RECENT","RECENT","RECENT") 
    else:
        pass

    if os.path.exists('CONN.LOCK') and ignore_current_conn == False:
        print("Connection still in progress , Aborting..., You may want to delete CONN.LOCK if needed")
        return ("INPROGRESS","INPROGRESS","INPROGRESS")

    with open("CONN.LOCK",'w') as f:
        f.write("CONNINPROGRESS")
    #Disconnect First
    nord_api_text = return_nord_json()
    if isinstance(nord_api_text,Exception):
        return 'ERROR','ERROR','ERROR'

    print("Start Connect..")
    if serverid is None and not nord_table_name is None :
        serverid = return_nord_id(nord_table_name= nord_table_name,lang=lang,region=region,keep_blockd=keep_blockd)
    elif not serverid is None and nord_table_name is None:
        pass
    else:
        pass

    print("Disconnecting..")
    subprocess.Popen("nordvpn -d",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True) 
    sleep(2)

    if not serverid is None:
        win_cmd = f'nordvpn -c -i {serverid}'
    else:
        #if server Id not found , get the best server and connect
        win_cmd = f'nordvpn -c'

    subprocess.run(win_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    #Wait till connected
    state = None
    nid = None
    nip = None

    for i in range(10):
        try:
            state,nip,nid = status()
        except TypeError as error:
            print("Could Not Connect , re-tries exceeded {}".format(error))
            return ("ERROR",'ERROR','ERROR')

        if state == 'DISCONNECTED':
            print(f'Trying Connection : {i}...')
            sleep(3)
            write_time()
            state,nid,nip = status()
        else:
        
            #retstatus = status()
      
            try:
                os.remove('CONN.LOCK')
            except:
                pass
            write_time()
            return (state,nid,nip)
    
    retstatus = status()
    print(retstatus)

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
            print(f"Recent Run last run {total_time}s ago , Threshold time {time_limit}s")
            return True

def disconnect():
    subprocess.Popen('nordvpn -d',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    retstatus = status()
    print(retstatus)
    return retstatus

def wait_send_response(filename='NEEDCHANGE.LOCK'):
    while (os.path.exists(filename)):
            print("Waiting IP to be changed")


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
            print("Will Change the IP")
            connect(run_time_limit=10)
            try:
                os.remove(filename)
            except:
                pass
            print("IP is Changed")
            sleep(5)
            
        else:
            print("IP will not be changed")
            sleep(2)


def create_lock_file(filename='NEEDCHANGE.LOCK'):

    if os.path.exists(filename):
        pass
    else:
        f = open(filename,'w')
        f.close()
    

from nordproxy import NProxy
def change_ip2():
    max_robot = int(input('How Many Instances you are running : '))
    robo_files = glob.glob(r'C:\temp\*.LOCK')
    robot_count = len(robo_files)
    npx = NProxy()

    while(True):
        print("Will not change the IP")
        sleep(3)

        if robot_count >= max_robot:
            nordip = npx.get_random_proxy()
            with open('C:\\temp\\IPCHANGE.IPCH','w') as f:
                f.write("CHANGINGIP")

            print("IP will bechanged")        
            status = 'disconnected'
            re_try_time = 0
            while status != 'CONNECTED':
                try:
                    status,_,_ = connect(serverid=nordip,ignore_current_conn=True,OVER_RIDE_TIME=True)
                except Exception:
                    status = 'disconnected'
                re_try_time += 1
                if re_try_time >= 5:
                    re_try_time = 0
            print("Ip Has been changed")
            
            for file in robo_files:
                os.remove(file)
        
        if os.path.exists('C:\\temp\\IPCHANGE.IPCH'):
            os.remove('C:\\temp\\IPCHANGE.IPCH')

        robo_files = glob.glob(r'C:\temp\*.LOCK')
        robot_count = len(robo_files)
        



if __name__ == "__main__":
    change_ip2()