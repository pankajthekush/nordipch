from ipvProxy import IProxy
from requests import session
import zipfile
import glob

import os,shutil,sys
current_path = os.path.dirname(os.path.realpath(__file__))
opvn_zip_path = os.path.join(current_path,'ovpn.zip')
ovpn_tcp = os.path.join(current_path,'ovpn_ipvanish')
certificate_path = os.path.join(current_path,'ovpn_ipvanish','ca.ipvanish.com.crt')


Session = session()
def download_file(link='https://www.ipvanish.com/software/configs/configs.zip',filename = opvn_zip_path):
    print('\n')
    print(f'Downloading...')
    print(filename)

    resp = Session.get(link,stream=True)
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
     

def download_ovpn_files():
    tcp_exists = os.path.exists(ovpn_tcp)
    if tcp_exists:
        return 0

    if os.path.exists(opvn_zip_path):
        os.remove(opvn_zip_path)
    
    if os.path.exists(ovpn_tcp):
        shutil.rmtree(ovpn_tcp)

    download_file('https://www.ipvanish.com/software/configs/configs.zip',opvn_zip_path)

    with zipfile.ZipFile(opvn_zip_path, 'r') as zip_ref:
        zip_path = os.path.join(current_path,'ovpn_ipvanish')
        zip_ref.extractall(zip_path)
    tcp_files = glob.glob(os.path.join(ovpn_tcp,'*.ovpn'))

    certificate_text = None
    with open(certificate_path,'r',encoding='utf-8') as f:
        certificate_text = f.read()
    new_line = '\n'
    certificate_text = f'<ca>{new_line}{certificate_text}{new_line  }</ca>{new_line}'
    
    for file in tcp_files:
        ovpn_txt = None
        if 'ca.ipvanish.com.crt' in str(file):
            #donot process certificate file
            continue

        with open(file,'a') as f:
            f.write('management localhost 7505\n')
            if sys.platform == 'linux':
                #in case of linux
                f.write(certificate_text)
                f.write('script-security 2\n')
                f.write('up /etc/openvpn/update-resolv-conf\n')
                f.write('down /etc/openvpn/update-resolv-conf')
            else:
                f.write(certificate_text)
                #windows support
        #read ovpn file text ,and replace certificate string
        with open(file,'r') as f:
            ovpn_txt = f.read()    
            ovpn_txt = ovpn_txt.replace('ca ca.ipvanish.com.crt','')
        
        with open(file,'w') as f:
            f.write(ovpn_txt)

    os.remove(opvn_zip_path)

if __name__ == "__main__":
    download_ovpn_files()
