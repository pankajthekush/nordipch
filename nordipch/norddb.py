
import psycopg2
from psycopg2 import sql
import requests
import json
import logging
import os

import tkinter as tk
from tkinter import filedialog



logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s')
current_path = os.path.dirname(os.path.realpath(__file__))



def browse_file_path(title_text="Choose File"):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes =(("Exe Files", "*.exe"),("All Files","*.*")),
                           title = title_text)
    return file_path


def copy_file_to(copyto,replace_file = False,title_text = 'Choose File'):
    already_exist = os.path.exists(copyto)
    if already_exist and not replace_file:
        print("File already exists")
    else:
        c_driver = browse_file_path(title_text=title_text)
        cdriver = None
        with open(c_driver,'rb') as f:
            cdriver = f.read()
        with open(copyto,'wb') as f:
            f.write(cdriver)
        print(f'copied {c_driver} to {copyto}')
     






def return_db_conn():
        db_json_file = os.path.join(current_path,'dbdata.json')
        copy_file_to(db_json_file,title_text='json for db connectivity')
        
        with open( os.path.join(current_path,'dbdata.json'),'r') as f:
            db_data = json.load(f)[0]
            
            dbname=db_data['dbname']
            user=db_data['user']
            host=db_data['host']
            password=db_data['password']
            ApplicationName = db_data['ApplicationName']
        
        logging.debug("Creating new connection")
        conn = None
        try:
            conn = psycopg2.connect(f"dbname={dbname} user={user} host={host} password={password} application_name={ApplicationName}")
        except Exception as exception:
            logging.debug(exception)        
        return conn

def return_nord_id(nord_table_name=None,lang=None,region=None):
    
    #BELOW IS VERY SHITTY CODE ,AND I KNOW PLEASE IMPORVE and notify me @pankajthekush@gmail.com if you could imporve it
    if lang and not region:
        qry_str = sql.SQL("select * from {} where lang={} order by random() limit 1").format(sql.Identifier(nord_table_name),sql.Literal(lang))
    if not lang and region:
        qry_str = sql.SQL("select * from {} where flag={} order by random() limit 1").format(sql.Identifier(nord_table_name),sql.Literal(region))
    if lang and region:
        qry_str = sql.SQL("select * from {} where flag={} and lang = {} order by random() limit 1").format(sql.Identifier(nord_table_name),sql.Literal(region),sql.Literal(lang))
    if not lang and not region:
        qry_str = sql.SQL("select * from {} order by random() limit 1").format(sql.Identifier(nord_table_name))
    
    conn = return_db_conn()
    nord_id = ''
    cur = conn.cursor()

    cur.execute(qry_str,(lang))
    rows = cur.fetchall()
    for row in rows:
        nord_id = row[0]
    conn.close() 
    return nord_id


def update_nord_tbl(table_name = None):
    conn = return_db_conn()
    curser = conn.cursor()
    r = requests.get('https://api.nordvpn.com/server')
    js = json.loads(r.text)
    

    for item in js:
        #sql = """INSERT INTO tbl_nord_ip(nid,nip) VALUES (%s,%s) on conflict (nid) do nothing;"""
        record_to_insert = [item['id'],item['ip_address'],item['name'],item['domain'],item['flag'],item['country']]
        
        curser.execute(sql.SQL("INSERT INTO {} VALUES (%s,%s,%s,%s,%s,%s) on conflict(id) do Nothing")
                                .format(sql.Identifier(table_name)),record_to_insert)
        
        affected_row = curser.rowcount
        if affected_row >= 1:
            conn.commit()
            logging.debug(f'Inserted {record_to_insert}')
        else:
            logging.debug(f'{record_to_insert} : Already Exists')
    curser.close()
    conn.close()



if __name__ == "__main__":
#    update_link_tbl(update_link='https://www.google.com/search?q=site:rjami.com Aurelia de La Maléne',
#    status='COMPLETE')
    # print(update_link_tbl(update_link='https://www.google.com/search?q=site:madrague.se Lars Frånstedt',
    pass
