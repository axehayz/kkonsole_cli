#!/usr/env/bin python
#createUsers.py
import os
import csv
import json
import logging
import random
import requests
import click

# logging.basicConfig(filename='/var/log/kperform_create.log',datefmt='%Y/%m/%d %H:%M:%S',level=logging.DEBUG)  #Not necessary, as this is always called by kperform.py
# :this same log file or logname, will append to log

# kpcl is also defined in kperform.py, which is supposed to be different logger. 
# Using the same name 'kpcl' here, but with different logger. This is done so I dont have to retype other loggers.
# Also this logger is initiated in the respective method under kperform, so the logger user is 'createUsers', not 'createAny'
kpcl = logging.getLogger('createUsers')


def main(KENTIK_API_TOKEN,KENTIK_API_EMAIL):
    # Implement quick exit function for standalone invocation. if token=empty, go to login.
    print ("Trying to run standalone. Why not try 'kperform create devices --help'")
    print ("Token: {}\nEmail: {}".format(KENTIK_API_TOKEN,KENTIK_API_EMAIL))
    ##### FUTURE WORK: Implement user prompts to enable standalone execution and call to createUsers(args)

def createUsers(file):
    """Create Users"""

    # Logging needs (random fugazy number for tracking and loggers)
    fugazy = str(random.randint(200,2000)*5)        #logger only takes strings. 
    kpcl.info ('[Fugazy:{}] Initiating Create Users'.format(fugazy))
    kpcl.debug ("[Fugazy:{}] File: {}".format(fugazy,file))

    # Open and read file. 
    with open(file,newline='',encoding="utf-8-sig") as f:
        reader = csv.DictReader(f,dialect='excel')
        users_2add = list()
        for row in reader:          # Every row is an orderedDict.
            d = dict()
            for item in row.items():  # Analyze each tuple in a row individually
                if item[0]=='user_email':
                    d[item[0]]=str(item[1])
                elif item[0]=='user_full_name':
                    d[item[0]]=str(item[1])
                elif item[0]=='role':
                    d[item[0]]=str(item[1])
                elif item[0]=='email_product':
                    d[item[0]]=bool(item[1])
                elif item[0]=='email_service':
                    d[item[0]]=bool(item[1])
            users_2add.append(d)
        kpcl.info ('[Fugazy:{}] Read {} users from the file'.format(fugazy,len(users_2add)))
        print ('[Fugazy:{}] Read {} users from the file.\nProceeding to adding users.'.format(fugazy,len(users_2add)))
    post_users(users_2add,fugazy)

##########################

def post_users(users,fugazy):
    """post prepared users"""
    url="https://api.kentik.com/api/v5/user"
    headers = {
    "Content-Type": "application/json",
    "X-CH-Auth-API-Token": os.environ.get('KENTIK_API_TOKEN',''),
    "X-CH-Auth-Email": os.environ.get('KENTIK_API_EMAIL','')}
    
    with click.progressbar(users,label='Adding Populators') as users:
        i=0; 
        for user in users:
            d = dict()
            d['user']=user
            #print (json.dumps(p,indent=4))
            i+=1
            kpcl.info('[Fugazy:{}_{}] Adding user as {}'.format(fugazy,i,d))

            try:
                if os.environ.get('KENTIK_API_EMAIL','')=="" or os.environ.get('KENTIK_API_TOKEN','')=="":
                    print("[WARN]: Not logged in. Try 'kkonsole login --help'")
                    raise SystemExit(0)             # Necessary to avoid system execution of below. This is better exit handling than import sys; sys.exit(0)
                r = requests.post(url,headers=headers, data=json.dumps(d))    #stream=True is [optionally] used for accessing raw._connection further below to get remote/local IPs.
                r.raise_for_status()
                kpcl.info('[Fugazy:{}_{}] Status Code {}'.format(fugazy,i,str(r.status_code)))
                kpcl.info('[Fugazy:%s_%d] %s',fugazy,i,str(r.text))

            except requests.exceptions.HTTPError as err:                # catch from r.raise_for_status call above.
                if err.response.status_code == 401: print('[ERROR]: Invalid Credentials. Please login again.'); print((err.response.text));kpcl.critical('[Fugazy:%s] Invalid Credentials. Please login again.',fugazy)
                elif err.response.status_code == 403: print('[ERROR]: IP Unauthorized.'); print(err.response.text); kpcl.critical('[Fugazy:%s] IP Unauthorized.',fugazy)     #; print(err.response.raw._connection.sock.getpeername())
                else: print(err); kpcl.debug('[Fugazy:%s_%d] Error Text: %s',fugazy,i,str(err))
            except requests.exceptions.ConnectionError as err:          # Catch DNS failures, refused connections. 
                print(err)
            except requests.exceptions.RequestException as err:         # Bail
                print (err)
            finally:
                #sleep(float(os.environ.get('API_RATE_LIMITER',0.1)))
                pass
        kpcl.debug('[Fugazy:%s_%d] Status Code %s',fugazy,i,str(r.status_code))
        kpcl.debug('[Fugazy:%s_%d] %s',fugazy,i,str(r.text))
    print ('[NOTICE]: Check /var/log/kperform_create.log for more details with fugazy {}'.format(fugazy))

        
if __name__=="__main__": main(os.getenv('KENTIK_API_TOKEN',''),os.getenv('KENTIK_API_EMAIL',''))