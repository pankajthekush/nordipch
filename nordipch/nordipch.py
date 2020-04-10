import requests
import json
import sys
from time import sleep
import ipaddress
import subprocess
from subprocess import Popen, PIPE
import json
import os
import time
import csv
import requests
import inspect
import glob
from nordproxy import NProxy
import sys
import telnetlib
from signal import signal, SIGINT
import getpass
import random


sys_platform = sys.platform
current_path = os.path.dirname(os.path.realpath(__file__))
last_run_file = os.path.join(current_path,'LASTRUN.txt')
block_file = os.path.join(os.getcwd(),'BLOCKED.txt')


ovpn_tcp = os.path.join(current_path,'ovpn_tcp')
ovpn_udp = os.path.join(current_path,'ovpn_udp')
vpn_pass_path = os.path.join(current_path,'vpnpass.txt')
nord_api = "https://api.nordvpn.com/server"
current_ip_api = "http://myip.dnsomatic.com"


def signal_handler(signal_received,frame):
    print('\n')
    print('hang on...')
    location,_,isp,status = isconnected()
    print(f'connected to {(location,isp)}')
    user_input = input("terminate current connection ? y/n :")
    if user_input.upper() == 'Y':
        management_console()
        location,ip,isp,status = isconnected()
        
        if status == False:
            print('disconnected')
        else:
            print(f'disconnection request sent')
        sys.exit(0)
       
        sys.exit(0)
    elif user_input.upper() =='N':
        print('bye')
        sys.exit(0)
    exit(0)



def management_console(commandname =b'signal SIGTERM\n' ):
    host = 'localhost'
    port = 7505
    
    if sys_platform == 'linux':
        try:
            session = telnetlib.Telnet(host=host,port=port)
            time.sleep(3) #get the complete connection
            session.write(commandname)
            time.sleep(3)
            session.close()
        except ConnectionRefusedError:
            print("management console not running")
            print("killing openvpn processes , sudo password is required")
            Popen(['sudo','killall','openvpn'])
            Popen(['sudo','ip','link','delete','tun0'])
    elif 'win' in sys_platform:
        try:
            session = telnetlib.Telnet(host=host,port=port)
            time.sleep(3) #get the complete connection
            session.write(commandname)
            time.sleep(3)
            session.close()
            open_vpn_command = 'runas', '/savecreds','/user:Administrator', f"taskkill /f /im openvpn.exe"    
            ps = subprocess.Popen(open_vpn_command)
            print(ps.communicate())

       

        except:
            print('console not running')

def return_server_domain_name(domain_name):
    

    domain_tcp = domain_name + '.tcp.ovpn'
    
    
    domain_udp = domain_name +'.udp.ovpn'
    dict_return_files = dict()

    tcp_files = os.listdir(ovpn_tcp)
    udP_files = os.listdir(ovpn_udp)
    
    if domain_tcp in tcp_files:
        dict_return_files['tcp'] = os.path.join('ovpn_tcp', domain_tcp)
        
    if domain_udp in udP_files:
        dict_return_files['udp'] = os.path.join( 'ovpn_udp', domain_udp)
        
    return dict_return_files


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
    


def connect(serverid=None,serverdomain = os.path.join('ovpn_tcp','al9.nordvpn.com.tcp.ovpn')):
    

    if os.path.exists(vpn_pass_path):
        print('nordvpn password file already exists')
    else:
        print("Credentials file for nordvpn not created")
        uname = input('Nord username :')
        pswd = getpass.getpass()
        with open(vpn_pass_path,'w') as f:
            f.write(uname)
            f.write('\n')
            f.write(pswd)


 
    print(isconnected())
    print("Disconnecting..")
    management_console()
   
    if sys_platform == 'linux':
        ovpn_file_path = os.path.join(current_path,serverdomain)
        open_vpn_command = 'sudo','openvpn','--daemon','--config',ovpn_file_path,'--auth-user-pass',vpn_pass_path
        subprocess.Popen(open_vpn_command)
    elif 'win' in sys.platform:
        ovpn_file_path = os.path.join(current_path,serverdomain)
        open_vpn_command = 'runas', '/savecreds','/user:Administrator', f"openvpn --config {ovpn_file_path} --auth-user-pass {vpn_pass_path}"    
        subprocess.Popen(open_vpn_command)

    #Wait till connected
    location = None
    ip = None
    isp = None
    status = None
    for _ in range(5):
        sleep(5)
        print('Checking for connection')
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




def change_ip2(max_robot=1):

    #this method is to be called within the application
    #when ipchanger starts change the current ip before proceeding

    robo_files = glob.glob(os.path.join(os.getcwd(),'*.LOCK'))
   
    for file in robo_files:
        os.remove(file)
    robot_count = len(robo_files)
    npx = NProxy(production=False)
    location,ip,isp,status = isconnected()
    print((location,ip,isp,status))
    print('initial connect seqence started')
    print('creating local .LOCK file')
    
    for _ in range(max_robot):
        sys_lock_file  = os.path.join(os.getcwd(),('SYS'+str(random.random()).replace('.','') +'.LOCK'))
        with open(sys_lock_file,'w') as f:
            pass
    
    
    while(True):
        signal(SIGINT, signal_handler)
        print(f"looking:{max_robot} lock(s) found:{robot_count},at {os.getcwd()} Current Connection {(location,ip,isp,status)}")        
        sleep(3)
        if robot_count >= max_robot:
            nordip,norddomain = npx.get_random_proxy()
            dict_config_files = return_server_domain_name(norddomain)
            while len(dict_config_files.keys()) == 0:
                print("invlaid proxy found, getting new one")
                #get the proxy till matching file with proxy is found
                nordip,norddomain = npx.get_random_proxy()
                dict_config_files = return_server_domain_name(norddomain)

            tcp_config,_ =  dict_config_files['tcp'],dict_config_files['udp']
            status = False
            re_try_time = 0
            while not status == True:
                location,ip,isp,status = connect(serverdomain=tcp_config)
               
                re_try_time += 1
                if re_try_time >= 5:
                    re_try_time = 0
                    print(f"Could not connect with ID {nordip}, retrying with new id")
                    nordip = npx.get_random_proxy()
            print("Ip Has been changed")
            
            for file in robo_files:
                os.remove(file)
        
        robo_files = glob.glob(os.path.join(os.getcwd(),'*.LOCK'))
        robot_count = len(robo_files)



def change_ip(max_robot=1):

    #This is standalone method to be called from console when code integration is not possible
    #This method is in entry point is nipchanger
    max_robot = int(input("Enter Number of instances you are running : "))
    #when ipchanger starts change the current ip before proceeding



    robo_files = glob.glob(os.path.join(os.getcwd(),'*.LOCK'))
   
    for file in robo_files:
        os.remove(file)
    robot_count = len(robo_files)
    npx = NProxy(production=False)
    location,ip,isp,status = isconnected()
    print((location,ip,isp,status))
    print('initial connect seqence started')
    print('creating local .LOCK file')
    
    for _ in range(max_robot):
        sys_lock_file  = os.path.join(os.getcwd(),('SYS'+str(random.random()).replace('.','') +'.LOCK'))
        with open(sys_lock_file,'w') as f:
            pass
    
    
    while(True):
        signal(SIGINT, signal_handler)
        print(f"looking:{max_robot} lock(s) found:{robot_count},at {os.getcwd()} Current Connection {(location,ip,isp,status)}")        
        sleep(3)
        if robot_count >= max_robot:
            nordip,norddomain = npx.get_random_proxy()
            dict_config_files = return_server_domain_name(norddomain)
            while len(dict_config_files.keys()) == 0:
                print("invlaid proxy found, getting new one")
                #get the proxy till matching file with proxy is found
                nordip,norddomain = npx.get_random_proxy()
                dict_config_files = return_server_domain_name(norddomain)

            tcp_config,_ =  dict_config_files['tcp'],dict_config_files['udp']
            status = False
            re_try_time = 0
            while not status == True:
                location,ip,isp,status = connect(serverdomain=tcp_config)
               
                re_try_time += 1
                if re_try_time >= 5:
                    re_try_time = 0
                    print(f"Could not connect with ID {nordip}, retrying with new id")
                    nordip = npx.get_random_proxy()
            print("Ip Has been changed")
            
            for file in robo_files:
                os.remove(file)
        
        robo_files = glob.glob(os.path.join(os.getcwd(),'*.LOCK'))
        robot_count = len(robo_files)



if __name__ == "__main__":
    change_ip2()
    #npx =NProxy(production=False)
    #input('ds')
    #print(npx.get_random_proxy())
    # print(npx.get_random_proxy())
    #connect()
    #management_console()
    #print(return_server_domain_name())
    #connect()
    #management_console()