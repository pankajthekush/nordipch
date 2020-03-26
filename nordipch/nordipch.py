import requests
import json
import sys
from time import sleep
import ipaddress
import subprocess
import json
import os
import time
import csv
import requests
import click
import inspect
import glob
from nordproxy import NProxy

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


def isconnected():
    statuslink = 'https://nordvpn.com/wp-admin/admin-ajax.php?action=get_user_info_data'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nordvpn.com/servers',
    'Cache-Control': 'max-age=0' }
    try:
        r = requests.get(statuslink,headers=headers)
    except:
        location,ip,isp,status = 'notfound','notfound','notfound',False
        return location,ip,isp,status


    jobj = json.loads(r.text)
    location,ip,isp,status = jobj['location'],jobj['ip'],jobj['isp'],jobj['status']
    return location,ip,isp,status
    


   
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

def connect(serverid=None):    
    print(isconnected())
    print("Start Connect..")
    
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
    location = None
    ip = None
    isp = None
    status = None
    for i in range(5):
        sleep(5)
        location,ip,isp,status = isconnected()
        print(f'Current Connection {(location,ip,isp,status)} with ID= {serverid}')
        if status == False:  
            location,ip,isp,status = isconnected()
        else:
            return (location,ip,isp,status)
           

    
    location,ip,isp,status = isconnected()
    return (location,ip,isp,status)


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

def change_ip(max_robot=1):
    max_robot = int(input("Enter Number of instances you are running : "))
    robo_files = glob.glob(r'C:\temp\*.LOCK')
    robot_count = len(robo_files)
    npx = NProxy()
    location,ip,isp,status = isconnected()
    while(True):
        print(f"Asking for {max_robot} lock(s) found {robot_count}, Current Connection {(location,ip,isp,status)}")        
        sleep(3)
        if robot_count >= max_robot:
            nordip = npx.get_random_proxy()
            status = False
            re_try_time = 0
            while not status == True:
                location,ip,isp,status = connect(serverid=nordip)
                print(location,ip,isp,status)
                re_try_time += 1
                if re_try_time >= 5:
                    re_try_time = 0
                    print(f"Could not connect with ID {nordip}, retrying with new id")
                    nordip = npx.get_random_proxy()
            print("Ip Has been changed")
            
            for file in robo_files:
                os.remove(file)
        
        robo_files = glob.glob(r'C:\temp\*.LOCK')
        robot_count = len(robo_files)
        

def change_ip2(max_robot=1):
    robo_files = glob.glob(r'C:\temp\*.LOCK')
    robot_count = len(robo_files)
    npx = NProxy()
    location,ip,isp,status = isconnected()
    while(True):
        print(f"Asking for {max_robot} lock(s) found {robot_count}, Current Connection {(location,ip,isp,status)}")        
        sleep(3)
        if robot_count >= max_robot:
            nordip = npx.get_random_proxy()
            status = False
            re_try_time = 0
            while not status == True:
                location,ip,isp,status = connect(serverid=nordip)
                print(location,ip,isp,status)
                re_try_time += 1
                if re_try_time >= 5:
                    re_try_time = 0
                    print(f"Could not connect with ID {nordip}, retrying with new id")
                    nordip = npx.get_random_proxy()
            print("Ip Has been changed")
            
            for file in robo_files:
                os.remove(file)
        
        robo_files = glob.glob(r'C:\temp\*.LOCK')
        robot_count = len(robo_files)
        



if __name__ == "__main__":
    npx =NProxy()
    #print(npx.get_random_proxy())
    print(npx.get_random_proxy())
