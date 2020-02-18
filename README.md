# Nordipch Nord IP Changer

<h2> install </h2>
<i>pip install --upgrade git+https://github.com/pankajthekush/nordipch.git </i>

<h2> Integrating with other application </h2>
<i>from nordipch.nordipch iport status,connect,get_current_ip</i>

<h3>status()</h3>

Takes no parameters and Will return the current status of network
status,ip,id = status()

status = either will be 'CONNECTED' or 'DISCONNECTED'
ip = Current ip returned by http://myip.dnsomatic.com
id = if connected to nord server will return the id of that server

<h3>connect()</h3>
have below signature
<i>connect(serverid=None,run_time_limit=10,OVER_RIDE_TIME = False,nord_table_name=None,lang=None,region=None,ignore_current_conn=False,keep_blockd=False)</i>

<b>serverid (string)</b>
if server id is provided connect to the provided server id , default is None and will take server ID from database

<b>run_time(Integer in seconds)</b>
Run time is the minimum time connect() will ignore the next calls , for example if run time set to 20 then next 20 seconds all calls to connect will be ignored , default value is 10s

<b>OVER_RIDE_TIM (Boolean , default is False)</b>
If set True this will ignore the run_time flag and call connect() regardless of the last run

<b>nord_table_name (string ,Default is None)</n>
If provided , will get the nord id to connect from given table ,if not then will connect to random server from nord if serverid is not provided

<b>lang (String, Default is None) </b>
This flag gets the id of the countries where given language is spokenn

<b>region (String, Default is None</b>
Get server id from given region

<b>ignore_current_conn (Boolean, default is false)<b>
<strong>NOT RECOMMENDED TO CHANGE THE DEFAULT VALUE<strong>
This keeps connect() from being called multiple times if connect method is in mid of chaning IP

<b>keep_blockd (Boolean, default = False)<b>
This paramter is used to get only server ids which are not ever used

<h3>disconnect()</h3>
Disconnects from nord server

<h1>Entry Points</h1>
<b>nipchanger</b>
Options:
  --max-robot INTEGER  --> Use this flag to change IP based on file in C:/temp
  --update-block BOOLEAN --> To get the serverid from nord which are not used up
  --help                  Show this message and exit.