#!/usr/bin/env python
#createSites.py
import os
import csv
import json
import logging
import random
import requests
import click

kpcl = logging.getLogger('createSites')


def main(KENTIK_API_TOKEN,KENTIK_API_EMAIL):
    # Implement quick exit function for standalone invocation. if token=empty, go to login.
    print ("Trying to run standalone. Why not try 'kperform create devices --help'")
    print ("Token: {}\nEmail: {}".format(KENTIK_API_TOKEN,KENTIK_API_EMAIL))
    ##### FUTURE WORK: Implement user prompts to enable standalone execution and call to createSites(args)

def createSites(file):
    kpcl.info("Inside createSites.py")
    fugazy = str(random.randint(200,2000)*5)        #logger only takes strings. 
    kpcl.info ('[Fugazy:{}] Initiating Create Sites'.format(fugazy))
    kpcl.debug ("[Fugazy:{}] File: {}".format(fugazy,file))
    kpcl.info ('[Fugazy:{}] Initializing the account and finding existing sites'.format(fugazy))

    try:
        if os.environ.get('KENTIK_API_EMAIL','')=="" or os.environ.get('KENTIK_API_TOKEN','')=="":
            print("[WARN]: Not logged in. Try 'kkonsole login --help'")
            raise SystemExit(0)             # Necessary to avoid system execution of below. This is better exit handling than import sys; sys.exit(0)
        headers = {
        "Content-Type": "application/json",
        "X-CH-Auth-API-Token": os.environ.get('KENTIK_API_TOKEN',''),
        "X-CH-Auth-Email": os.environ.get('KENTIK_API_EMAIL','')}
        r = requests.get('https://api.kentik.com/api/v5/sites',headers=headers, stream=True)    #stream=True is [optionally] used for accessing raw._connection further below to get remote/local IPs.
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:                # catch from r.raise_for_status call above.
        if err.response.status_code == 401: print('[ERROR]: Invalid Credentials. Please login again.'); print((err.response.text));kpcl.critical('[Fugazy:%s] Invalid Credentials. Please login again.',fugazy)
        elif err.response.status_code == 403: print('[ERROR]: IP Unauthorized.'); print(err.response.text); kpcl.critical('[Fugazy:%s] IP Unauthorized.',fugazy)     #; print(err.response.raw._connection.sock.getpeername())
        else: print(err); kpcl.debug('[Fugazy:%s] Error Text: %s',fugazy,str(err))
    except requests.exceptions.ConnectionError as err:          # Catch DNS failures, refused connections. 
        print(err)
    except requests.exceptions.RequestException as err:         # Bail
        print (err)
    kpcl.info('[Fugazy:%s] Site Built %s',fugazy,str(r.status_code))
    print ('[NOTICE]: Check /var/log/kperform_create.log for more details')
    kpcl.info('[Fugazy:%s] %s',fugazy,str(r.text))
    #print ((json.dumps(r.json(), indent=4)))

    """
    below codeblock checks for existing sites
    """
    current_sites = list()
    for site in r.json()["sites"]:
        current_sites.append(site['site_name'])
    
    with open(file,newline='',encoding="utf-8-sig") as f:
        reader = csv.DictReader(f,dialect='excel')
        #kpcl.info("[Fugazy:%s] %s sites found",fugazy,str(len(list(reader))))     # CAUTION: !!! do not read the 'reader' else the obj pointer will be lost and the below for loop wont execute.
        sites_2add = list()
        i=0
        duplicate_sites=0
        for row in reader:                       # Every row is an orderedDict.
            print (row)
            d = dict()
            i+=1
            #kpcl.debug("[Fugazy:%s_%s] Adding Site_%s with %s",fugazy,str(i),str(i),str(row.items()))
            for item in row.items():            # Every tuple in a row
                if item[0]=='site_name': 
                    print (item[1])
                    print (type(item[1]))
                    duplicate = False
                    if ((item[1])) in current_sites:             #Check if site already exists.
                        kpcl.warning("[Fugazy:%s_%s] Site %s already exists. Not adding.",fugazy,str(i),str([item[1]]))
                        duplicate = True
                        duplicate_sites += 1
                        break
                    else:
                        d[item[0]]=item[1]
                if item[0]=='lat': 
                    if item[1] is not "": 
                        d[item[0]]=(float(item[1]))
                if item[0]=='lon': 
                    if item[1] is not "":
                        d[item[0]]=(float(item[1]))
            if not duplicate: sites_2add.append(d)       # DO NOT TAKE THIS AWAY.
        print (duplicate_sites)
            #print (d)
    print("[NOTICE]: Number of sites found in file: ",format(str(i)))
    print('[NOTICE]: Number of sites will be added: ',format(str(len(sites_2add)),))
    kpcl.debug("[Fugazy:%s] List of %s Sites(s) compiled and ready to go",fugazy,str(len(sites_2add)))
    post_sites(sites_2add,fugazy)


##########################

def post_sites(sites,fugazy):
    """post prepared sites"""
    url="https://api.kentik.com/api/v5/site"
    headers = {
    "Content-Type": "application/json",
    "X-CH-Auth-API-Token": os.environ.get('KENTIK_API_TOKEN',''),
    "X-CH-Auth-Email": os.environ.get('KENTIK_API_EMAIL','')}


    with click.progressbar(sites,label='Adding Populators') as sites:
        i=0; 
        for site in sites:
            d = dict()
            d['site']=site
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