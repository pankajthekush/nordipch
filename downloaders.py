import requests, os, sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
current_path = os.path.dirname(os.path.realpath(__file__))


if os.path.exists(os.path.join(current_path,'ovpn_ipvanish')):
    print('folder already created')
else:
    print('folder will be created')
    os.mkdir(os.path.join(current_path,'ovpn_ipvanish'))

file_path = os.path.join(current_path,'ovpn_ipvanish')

def fetch_url(ipvnaish_url):

    base_name = os.path.basename(ipvnaish_url) 
    if not base_name.endswith('.ovpn'):
        print(f'{ipvnaish_url} not a ipvanish file , exiting')
        return 0
    import pdb;pdb.set_trace()
    
    resp = requests.get(ipvnaish_url,stream=True)
    handle = open(file_path,'wb')
    for chunk in resp.iter_content(chunk_size=512):
        if chunk:
            handle.write(chunk)
            sys.stdout.write('\r.')
            sys.stdout.flush()
            sys.stdout.write('\r..')
            sys.stdout.flush()
            sys.stdout.write('\r...')
        handle.close()



def download_ipvanish_ovpn(url='https://configs.ipvanish.com/configs/'):
    res = requests.get(url)
    soup = BeautifulSoup(res.text,'lxml')
    all_anchors = soup.find_all('a')
    list_urls = list()
    
    for anchor in all_anchors:
        config_url = urljoin(url,anchor['href'])
        list_urls.append(config_url)

    for url in list_urls:
        fetch_url(url)
    

if __name__ == '__main__':
    download_ipvanish_ovpn()
    
