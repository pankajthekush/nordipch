import logging 

#https://www.geeksforgeeks.org/logging-in-python/
#Create and configure logger 

logging.basicConfig(filename="/var/log/vpn/vpn.log",format='%(asctime)s %(message)s',filemode='w')
logger=logging.getLogger() 
logger.setLevel(logging.INFO) 