import requests
import json
import glob
import sys
import socket
import os
from nordipch import config_file
from ipvProxy import IProxy
import random
from signal import signal, SIGINT
from time import sleep
import getpass
import subprocess
import telnetlib
from subprocess import Popen, PIPE
from ilogger import logger


sys_platform = sys.platform
sys_name = socket.gethostname()
current_path = os.path.dirname(os.path.realpath(__file__))
last_run_file = os.path.join(current_path,'LASTRUN.txt')
block_file = os.path.join(os.getcwd(),'BLOCKED.txt')
jobj = config_file()
ovpn_tcp = os.path.join(current_path,'ovpn_ipvanish')

if sys.platform == 'linux':
    vpn_pass_path = 'vpnpass2.txt'
else:
    vpn_pass_path = os.path.join(current_path,'vpnpass2.txt')


def management_console(commandname =b'signal SIGTERM\n' ):
    logger.info('stopping openvpn connection')
    host = 'localhost'
    port = 7505
    
    if sys_platform == 'linux':
        try:
            session = telnetlib.Telnet(host=host,port=port)
            sleep(3) #get the complete connection
            session.write(commandname)
            session.close()
            
            _,_,_,status = isconnected2()
            while status == True:
                Popen('killall openvpn',shell=True,stdout=PIPE,stderr=PIPE)
                logger.info('killed openvpn by force')
                sleep(5)
                _,_,_,status = isconnected2()

        except ConnectionRefusedError:
            logger.info("management console not running, killing openvpn by force")
            Popen('killall openvpn',shell=True,stdout=PIPE,stderr=PIPE)
            _,_,_,status = isconnected2()
            
            while status == True:
                Popen('killall openvpn',shell=True,stdout=PIPE,stderr=PIPE)
                logger.info('killed openvpn by force')

                sleep(5)
                _,_,_,status = isconnected2()

    elif 'win' in sys_platform:
        try:
            session = telnetlib.Telnet(host=host,port=port)
            sleep(3) #get the complete connection
            session.write(commandname)
            sleep(3)
            session.close()
            #do not kill, it takes time
            #open_vpn_command = 'runas', '/savecreds','/user:Administrator', f"taskkill /f /im openvpn.exe"    
            #wait the program to execute itself
            # open_vpn_command = "taskkill /f /im openvpn.exe"    
            # ps = subprocess.Popen(open_vpn_command,stderr=subprocess.DEVNULL)
            #print(ps.communicate())
            logger.info('proxy server disconnected without exception')
        except Exception:
            open_vpn_command = "taskkill /f /im openvpn.exe"   
            ps = subprocess.Popen(open_vpn_command,stderr=subprocess.DEVNULL)
            #print(ps.communicate())
            logger.info('proxy server disconnected  with exception')


def get_current_ip2():
    logger.info('getting current IP')
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
            logger.info(e)
            ip = None
            return ip

        try:
            jobj = json.loads(r.text)
            ip= jobj['ip']
        except Exception as e:
            logger.info(e)
            ip = None
            return ip

        return ip

home_ip = None
while home_ip is None:
    home_ip = get_current_ip2()

def return_server_domain_name(domain_name):
    
    dict_return_files = dict()

    tcp_files = os.listdir(ovpn_tcp)
    
    if domain_name in tcp_files:
        dict_return_files['tcp'] = os.path.join('ovpn_ipvanish', domain_name)
         
    return dict_return_files

def connect(serverid=None,serverdomain = os.path.join('ovpn_tcp','al9.nordvpn.com.tcp.ovpn')):
    
    if os.path.exists(vpn_pass_path):
        logger.info('retrieving proxy credentials...')
    else:
        logger.info("retrieving proxy credentials...")
        uname = input('Ipvanish username :')
        pswd = getpass.getpass()
        with open(vpn_pass_path,'w') as f:
            f.write(uname)
            f.write('\n')
            f.write(pswd)

    management_console()
   
    if sys_platform == 'linux':
        ovpn_file_path = os.path.join(current_path,serverdomain)
        open_vpn_command = 'openvpn','--daemon','--config',ovpn_file_path,'--auth-user-pass',vpn_pass_path
        #input(open_vpn_command)
        subprocess.Popen(open_vpn_command)
        sleep(5)
    elif 'win' in sys.platform:
        ovpn_file_path = os.path.join(current_path,serverdomain)
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

        location,ip,isp,status = isconnected2()
        location = location.split(',')[-1]
        logger.info(f'Current Connection {(location,status)}')
        if status == False: 
            location,ip,isp,status = isconnected2()
        else:
            return (location,ip,isp,status)
    
    location,ip,isp,status = isconnected2()
    logger.info(f'failed to connect to {serverdomain}')
    sleep(20)
    #wait for sometime before trying again
    return (location,ip,isp,status)


def reurn_ovpn_file(npx:IProxy,update_proxy_bucket):
    #return valid ovpn file
    norddomain = npx.get_random_proxy(auto_update=update_proxy_bucket)
    dict_config_files = return_server_domain_name(norddomain)
    while len(dict_config_files.keys()) == 0:
        logger.info("invalid proxy found, getting new one")
        norddomain = npx.get_random_proxy(auto_update=update_proxy_bucket)
        dict_config_files = return_server_domain_name(norddomain)
    
    tcp_config =  dict_config_files['tcp']
    return tcp_config


def isconnected2():
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
            logger.info(e)
            location,ip,isp,status = 'notfound','notfound','notfound',False
            #sleeping because if timeout error occurs
            #that means connection is in progress
            sleep(10)
            return location,ip,isp,False

        try:           
            jobj = json.loads(r.text)
        except Exception as e:
            logger.info(e)
            location,ip,isp,status = 'notfound','notfound','notfound',False
            sleep(10)
            return location,ip,isp,False

        location,ip,isp,status = jobj['location'],jobj['ip'],jobj['isp'],jobj['status']
        if location == 'notfound':
            pass
            sleep(10)
            #try again and get the location
        else:
            if str(ip).strip() == str(str(home_ip).strip()):
                logger.info(f'homeip:{home_ip},currentip: {ip},setting status false')
                status = False
            else:
                logger.info(f'homeip:{home_ip},currentip: {ip},setting status true')
                status = True
            return location,ip,isp,status



def signal_handler(signal_received,frame):
    management_console()
    sys.exit(1)


def change_ip(max_robot=1,notify_email='',inline=False):

    region = os.getenv('ip_country')
    if region == 'localip':
        logger.info('loal ip has been requested by docker , exiting')
        with open('NSUCCESS.txt','w',encoding='utf-8') as _:
            pass
        sys.exit(0)



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
        

    update_proxy_bucket = (jobj['recycle_proxy'])


    #read config file

    if os.path.exists('NSUCCESS.txt'):
        try:
            os.remove('NSUCCESS.txt')
        except Exception:
            logger.info('unable to remove NSUCCESS.txt')
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
    npx = IProxy(production=False)
    location,ip,isp,status = isconnected2()
    logger.info('initial connect seqence started')
    logger.info('creating local .LOCK file')
    
    for _ in range(max_robot):
        sys_lock_file  = os.path.join(os.getcwd(),('SYS'+str(random.random()).replace('.','') +'.LOCK'))
        with open(sys_lock_file,'w') as _:
            pass
    
    current_config_file = None
    while(True):
        signal(SIGINT, signal_handler)
        location = location.split(',')[-1]
        sleep(30)
        if robot_count >= max_robot:
            tcp_config =  reurn_ovpn_file(npx=npx,update_proxy_bucket=update_proxy_bucket)
            status = False
            
          #Try for 5 times by changing new IPs, if ,
             #   if did not connect withing 5 tries ,send email and exit
      
            max_server_tried = 0
            logger.info(f'connecting to {tcp_config}')
            for i in range(1000):
                location,ip,isp,status = connect(serverdomain=tcp_config)
                if status == True:
                    break
                elif status == False:
                    logger.info(f'failed to connect to {tcp_config}')
                    tcp_config =  reurn_ovpn_file(npx=npx,update_proxy_bucket=update_proxy_bucket)
                    logger.info(f'retrying {tcp_config}')
                    

                max_server_tried += 1
                
                if max_server_tried >= 950:
                    logger.info(f'tried {i} ips , could not connect ,exiting')
                    send_email2(send_to=notify_email,body='disconnected from vpn',subject='max retires meet')
                    sys.exit(1)
                
               
            
             
            #to notify that ipchanger has begun
            #write current ip to a file
            location,ip,isp,status = isconnected2()
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
                    logger.info(f'unable to remove file {file}')
        
        robo_files = glob.glob(os.path.join(os.getcwd(),'*.LOCK'))
        robot_count = len(robo_files)



if __name__ == "__main__":
    change_ip()