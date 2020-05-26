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
from azwmail.azwmail import send_email2
from pathlib import Path
import socket
from supload.supload import upload_file
import random
from pathlib import Path
from shelper import config_file

sys_platform = sys.platform
sys_name = socket.gethostname()
current_path = os.path.dirname(os.path.realpath(__file__))
last_run_file = os.path.join(current_path,'LASTRUN.txt')
block_file = os.path.join(os.getcwd(),'BLOCKED.txt')


ovpn_tcp = os.path.join(current_path,'ovpn_tcp')
ovpn_udp = os.path.join(current_path,'ovpn_udp')

if sys.platform == 'linux':
    vpn_pass_path = 'vpnpass.txt'
else:
    vpn_pass_path = os.path.join(current_path,'vpnpass.txt')
nord_api = "https://api.nordvpn.com/server"
current_ip_api = "http://myip.dnsomatic.com"




jobj = config_file()



def signal_handler(signal_received,frame):
    management_console()
    sys.exit(1)

def management_console(commandname =b'signal SIGTERM\n' ):
    host = 'localhost'
    port = 7505
    
    if sys_platform == 'linux':
        try:
            session = telnetlib.Telnet(host=host,port=port)
            time.sleep(3) #get the complete connection
            session.write(commandname)
            drun = Popen('killall openvpn',shell=True,stdout=PIPE,stderr=PIPE)
            # stdout,strerr = drun.communicate()
            # print(stdout)
            # print(strerr)
            time.sleep(3)
            session.close()
        except ConnectionRefusedError:
            print("management console not running")
            Popen(['killall','openvpn'])

    elif 'win' in sys_platform:
        try:
            session = telnetlib.Telnet(host=host,port=port)
            time.sleep(3) #get the complete connection
            session.write(commandname)
            time.sleep(3)
            session.close()
            #do not kill, it takes time
            #open_vpn_command = 'runas', '/savecreds','/user:Administrator', f"taskkill /f /im openvpn.exe"    
            #wait the program to execute itself
            # open_vpn_command = "taskkill /f /im openvpn.exe"    
            # ps = subprocess.Popen(open_vpn_command,stderr=subprocess.DEVNULL)
            #print(ps.communicate())
            print('proxy server disconnected without exception')
        except Exception:
            open_vpn_command = "taskkill /f /im openvpn.exe"   
            ps = subprocess.Popen(open_vpn_command,stderr=subprocess.DEVNULL)
            #print(ps.communicate())
            print('proxy server disconnected  with exception')
    
    # notify_email = jobj['notify_email']
    # subject = f'nipchanger:{sys_name}:openvpn killed'
    # send_email2(send_to=notify_email,body='openvpn.exe killed',subject=subject)


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

    while True:
        try:
            r = requests.get(statuslink,headers=headers,timeout=10)
        except Exception as e:
            print(e)
            location,ip,isp,status = 'notfound','notfound','notfound',False
            #sleeping because if timeout error occurs
            #that means connection is in progress
            sleep(10)

            return location,ip,isp,status
            
        jobj = json.loads(r.text)
        location,ip,isp,status = jobj['location'],jobj['ip'],jobj['isp'],jobj['status']
        if location == 'notfound':
            pass
            sleep(10)
            #try again and get the location
        else:
            return location,ip,isp,status
    

def connect(serverid=None,serverdomain = os.path.join('ovpn_tcp','al9.nordvpn.com.tcp.ovpn')):
    
    if os.path.exists(vpn_pass_path):
        print('retrieving proxy credentials...')
    else:
        print("retrieving proxy credentials...")
        uname = input('Nord username :')
        pswd = getpass.getpass()
        with open(vpn_pass_path,'w') as f:
            f.write(uname)
            f.write('\n')
            f.write(pswd)

    print("Disconnecting..")
    management_console()
   
    if sys_platform == 'linux':
        ovpn_file_path = os.path.join(current_path,serverdomain)
        open_vpn_command = 'openvpn','--daemon','--config',ovpn_file_path,'--auth-user-pass',vpn_pass_path
        subprocess.Popen(open_vpn_command)
        sleep(5)
    elif 'win' in sys.platform:
        ovpn_file_path = os.path.join(current_path,serverdomain)
        time.sleep(5)
        open_vpn_command = 'runas', '/savecreds','/user:Administrator', f"openvpn --config {ovpn_file_path} --auth-user-pass {vpn_pass_path}"
        subprocess.Popen(open_vpn_command,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
        sleep(5)
        

    #Wait till connected
    location = None
    ip = None
    isp = None
    status = None
    #Try 5 times to change the ip with 5s delay
    #if not then exit stating  connected to bad ip
    #need to respawn

    for i in range(5):
        sleep(5)

        location,ip,isp,status = isconnected()
        location = location.split(',')[-1]
        print(f'Current Connection {(location,status)}')
        if status == False: 
            location,ip,isp,status = isconnected()
        else:
            return (location,ip,isp,status)
    
    location,ip,isp,status = isconnected()
    print(f'failed to connect to {serverdomain}')
    return (location,ip,isp,status)


def upload_disconnect(configdata):
    total_upload = 0
  
    s3_bucket = configdata['s3_bucket_name']
    s3_folder = configdata['s3_folder']
 

    upload_log= 'uploaded_log.csv'
 
    management_console()
    all_htmls = glob.glob('*.html')
    to_upload_list = list()
    if os.path.exists(upload_log):
        #get previous upload data , and compare it with current html files
        #in on filesystem, compare the files , if file exists in csv it means its been uploded already
        #if not then uplaod it
        f = open(upload_log,'r',encoding='utf-8')
        all_files_uploaded = f.read().splitlines()
        f.close()
        for file in all_htmls:

            if file in all_files_uploaded:
                pass
            else:
                to_upload_list.append(file)
        f.close()
        #If upload list
        if len(to_upload_list) > 0:
            
            f = open(upload_log,'a',encoding='utf-8')
            for html in to_upload_list:
                f.write(html)
                f.write('\n')
                upload_file(file_name=html,in_sub_folder=s3_folder,
                                                bucket_name=s3_bucket)
                print(f'uploadd {html}')
            f.close()
            #get count of uploaded html
            return len(to_upload_list)
        else:
            return total_upload


    elif not os.path.exists(upload_log):
        f = open(upload_log,'a',encoding='utf-8')
        for html in all_htmls:
            f.write(html)
            f.write('\n')
            to_upload_list.append(html)
            upload_file(file_name=html,in_sub_folder=s3_folder,
                                            bucket_name=s3_bucket)
            print(f'uploadd {html} as new')
        f.close()
        return len(all_htmls)


def reurn_ovpn_file(npx:NProxy,update_proxy_bucket):
    #return valid ovpn file
    _,norddomain = npx.get_random_proxy(auto_update=update_proxy_bucket)
    dict_config_files = return_server_domain_name(norddomain)
    while len(dict_config_files.keys()) == 0:
        print("invalid proxy found, getting new one")
        _,norddomain = npx.get_random_proxy(auto_update=update_proxy_bucket)
        dict_config_files = return_server_domain_name(norddomain)

    tcp_config,_ =  dict_config_files['tcp'],dict_config_files['udp']
    return tcp_config


def change_ip(max_robot=1,notify_email='',inline=False):

    #This is standalone method to be called from console when code integration is not possible
    #This method is in entry point is nipchanger
    
    #max_robot = int(input("Enter Number of instances you are running : "))
    #when ipchanger starts change the current ip before proceeding
    #close connections is already

    if sys_platform == 'linux':
        euid = os.geteuid()
        if euid != 0:
            raise PermissionError('nipchanger to be run as root')
            sys.exit(0)
        
    management_console()

    update_proxy_bucket = (jobj['recycle_proxy'])


    #read config file

    if os.path.exists('NSUCCESS.txt'):
        try:
            os.remove('NSUCCESS.txt')
        except Exception:
            print('unable to remove NSUCCESS.txt')
    ipchaner_started = False
    if inline == False:
        max_robot = int(jobj['num_instances'])
        notify_email = jobj['notify_email']
    else:
        #method is being called pythonacly , call should provide the paramters
        #for max_robot and notify_email
        pass


    robo_files = glob.glob(os.path.join(os.getcwd(),'*.LOCK'))
   
    for file in robo_files:
        os.remove(file)
    robot_count = len(robo_files)
    npx = NProxy(production=False)
    location,ip,isp,status = isconnected()
    print((location,status))
    print('initial connect seqence started')
    print('creating local .LOCK file')
    
    for _ in range(max_robot):
        sys_lock_file  = os.path.join(os.getcwd(),('SYS'+str(random.random()).replace('.','') +'.LOCK'))
        with open(sys_lock_file,'w') as _:
            pass
    
    current_config_file = None
    while(True):
        signal(SIGINT, signal_handler)

        location = location.split(',')[-1]
        print(f"{max_robot}:{robot_count},proxy: {(current_config_file)}")        
        sleep(3)
        if robot_count >= max_robot:
            tcp_config =  reurn_ovpn_file(npx=npx,update_proxy_bucket=update_proxy_bucket)
            status = False
            
          #Try for 5 times by changing new IPs, if ,
             #   if did not connect withing 5 tries ,send email and exit
      
            max_server_tried = 0
            print(f'connecting to {tcp_config}')
            for i in range(1000):
                location,ip,isp,status = connect(serverdomain=tcp_config)
                if status == True:
                    break
                elif status == False:
                    print(f'failed to connect to {tcp_config}')
                    tcp_config =  reurn_ovpn_file(npx=npx,update_proxy_bucket=update_proxy_bucket)
                    print(f'retrying {tcp_config}')
                    

                max_server_tried += 1
                
                if max_server_tried >= 950:
                    print(f'tried {i} ips , could not connect ,exiting')
                    send_email2(send_to=notify_email,body='disconnected from vpn',subject='max retires meet')
                    sys.exit(1)
                
               
            
             
            #to notify that ipchanger has begun
            #write current ip to a file
            location,ip,isp,status = isconnected()
            current_config_file = tcp_config
            with open('current_ip','w',encoding='utf-8') as f:
                f.write(' '.join(str(s) for s in (location,ip,isp,tcp_config)))

            if ipchaner_started == False:
                with open('NSUCCESS.txt','w',encoding='utf-8') as _:
                    ipchaner_started = True

            robo_files = glob.glob(os.path.join(os.getcwd(),'*.LOCK'))
            for file in robo_files:
                try:
                    os.remove(file)
                except Exception:
                    print(f'unable to remove file {file}')
        
        robo_files = glob.glob(os.path.join(os.getcwd(),'*.LOCK'))
        robot_count = len(robo_files)



if __name__ == "__main__":
    change_ip()
    #npx =NProxy(production=False)
    #input('ds')
    #print(npx.get_random_proxy())
    # print(npx.get_random_proxy())
    #connect()
    #management_console()
    #print(return_server_domain_name())
    #connect()
    #management_console()