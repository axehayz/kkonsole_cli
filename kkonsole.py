#!/usr/bin/env python

#kkonsole script
import click
import os
import requests
import json #requests comes with json decoder.
#from pampy import match,_       # not used yet
import logging; logging.basicConfig(filename='/var/log/kkonsole.log',datefmt='%Y/%m/%d %H:%M:%S',level=logging.INFO)



@click.group()
def kkonsole():
    """kentik konsole utility for SEs/CSEs"""
    #login()
    pass

@kkonsole.command()
@click.option('--api-token',prompt=True,default=lambda: os.environ.get('KENTIK_API_TOKEN',''),show_default="from env inside Docker container",help="Enter API Token")
@click.option('--api-email',prompt=True,default=lambda: os.environ.get('KENTIK_API_EMAIL',''),show_default="from env inside Docker container",help="Enter API Email")
# :this Need help -- how to avoid output showing API token. Or maybe its for the good?
# @click.option('--prod/--no-prod', '-p/ ',default=False,help="only use to verify credentials (PROD or explicit) \f No login available on PROD credentials. Only verify credentials")
def login(api_token,api_email):
    """Use to login and validate API Credentials and Access"""
    login_url="https://api.kentik.com/api/v5/users"
    logging.info("Initiate Login")

    # Reading from env variables, if already existing
    TOKEN = os.getenv('KENTIK_API_TOKEN','') if os.getenv('KENTIK_API_TOKEN','') != "" else api_token
    EMAIL = os.getenv('KENTIK_API_EMAIL','') if os.getenv('KENTIK_API_EMAIL','') != "" else api_email
    
    headers = {
    "Content-Type": "application/json",
    "X-CH-Auth-API-Token": TOKEN,
    "X-CH-Auth-Email": EMAIL}
    try:
        r = requests.get(login_url,headers=headers, stream=True)            #stream=True is [optionally] used for accessing raw._connection further below to get remote/local IPs.  
        r.raise_for_status()
        #click.echo(type(json.loads(r.text)['users']))          # Loads to json dictionary
        for user in (json.loads(r.text)['users']):
            if user['user_email'] == EMAIL:
                click.echo("[INFO]: Login successful.\n[INFO]: Welcome {}:[{}]".format(user['user_full_name'],user['id']))
                logging.info("Login Successful. Welcome {}:[{}]".format(user['user_full_name'],user['id']))
                os.environ['KENTIK_API_TOKEN']=TOKEN
                os.environ['KENTIK_API_EMAIL']=EMAIL
            # click.echo("[INFO]: Login successful.\n[INFO]: Welcome {}:[{}]".format(user['user_full_name'],user['id'])) if user['user_email'] == EMAIL else "" #click.echo("User cannot be found. Confirm Credentials.")

        os.system('bash -c \'/bin/bash\'')                       # FUTURE WORK try to fork here to create 2 processes. Use child process(==0) to set .bashrc; and start new shell on parent.
        # logging.debug("Resetting login environment variables first. Exiting...")            
        # os.environ['KENTIK_API_TOKEN']=""
        # os.environ['KENTIK_API_EMAIL']=""
        # click.echo("Exited gracefully.")

        """ # Below code is to avoid indefinite processes created by login. 
            # This is good coding practice, however, realistically in docker implementation
            # it is not harmful.

            # REMEMBER: echo $$ shows the current PID of the executing process.

        if os.getpid()>0:
            #this is parent process. treat as virgin login. 
            # Fork from here. 
            click.echo("test -1")
            child_login = os.fork()                 # os.forkpty() or pty.fork, leads to unclean child process. the if child_login == 0 should be changed as tty outputs nonzero.
            print (child_login)
            if child_login!=0:                       # While still parent, go and create a child 
                click.echo("GOD")
                #os.setsid()
                os.system('bash -c \'/bin/bash\'')
                click.echo("Resetting login environment variables first.\nExiting...")
                os.environ['KENTIK_API_TOKEN']=""
                os.environ['KENTIK_API_EMAIL']=""
                #os._exit(0)                            # Incorrect to exit child here. There is no child to exit.
                child_login = 0                           # Graceful logout can be treated as virgin login. 
                click.echo("Exited gracefully.")
        elif os.getpid()==0:
            # I am in child process.
            # Exit out of child first. 
            click.echo("start of child")
            os._exit(0)                              # Note the _exit(), which exits child, as opposed to os.exit() which exits parent.
            click.echo("Exited child")
            # Cursor back to parent. 
        else:
            print ("unknown")
        """
        
    except requests.exceptions.HTTPError as err:                # catch from r.raise_for_status call above.
        if err.response.status_code == 401: click.echo('[ERROR]: Invalid Credentials. Please login again.'); click.echo((err.response.text))
        elif err.response.status_code == 403: click.echo('[ERROR]: IP Unauthorized.'); click.echo(err.response.text)     #; click.echo(err.response.raw._connection.sock.getpeername())
        else: click.echo(err)
    except requests.exceptions.ConnectionError as err:          # Catch DNS failures, refused connections. 
        click.echo(err)
    except requests.exceptions.RequestException as err:         # Bail
        click.echo (err)

      
    # print(os.environ.get('KENTIK_API_TOKEN',"[CAUTION]: KENTIK_API_TOKEN/EMAIL unset"))
    ########## Work here --- not being able to export environment
    #implement try and exception handling for r = requests.get

@kkonsole.command()
def whoami():
    #display current user [as alternative to showing in .bashrc]
    login_url="https://api.kentik.com/api/v5/users"
    headers = {
    "Content-Type": "application/json",
    "X-CH-Auth-API-Token": os.environ.get('KENTIK_API_TOKEN',''),
    "X-CH-Auth-Email": os.environ.get('KENTIK_API_EMAIL','')}
    try:
        if os.environ.get('KENTIK_API_EMAIL','')=="" or os.environ.get('KENTIK_API_TOKEN','')=="":
            click.echo("[WARN]: Not logged in. Try 'kkonsole login --help'")
            raise SystemExit(0)             # Necessary to avoid system execution of below. This is better exit handling than import sys; sys.exit(0)
        #print(os.environ.get('KENTIK_API_EMAIL',''))
        #print(os.environ.get('KENTIK_API_TOKEN',''))
        r = requests.get(login_url,headers=headers, stream=True)    #stream=True is [optionally] used for accessing raw._connection further below to get remote/local IPs.
        r.raise_for_status()                                # This raises HTTPError and its subcodes. Catch in HTTPError
        for user in (json.loads(r.text)['users']):
            click.echo("[INFO]: Currently logged in as {} UID:{} CID:{}".format(user['user_full_name'],user['id'],user['company_id'])) if user['user_email'] == os.environ.get('KENTIK_API_EMAIL','') else ""  
    except requests.exceptions.HTTPError as err:                # catch from r.raise_for_status call above.
        if err.response.status_code == 401: click.echo('[ERROR]: Invalid Credentials. Please login again.'); click.echo((err.response.text))
        elif err.response.status_code == 403: click.echo('[ERROR]: IP Unauthorized.'); click.echo(err.response.text)     #; click.echo(err.response.raw._connection.sock.getpeername())
        else: click.echo(err)
    except requests.exceptions.ConnectionError as err:          # Catch DNS failures, refused connections. 
        click.echo(err)
    except requests.exceptions.RequestException as err:         # Bail
        click.echo (err)
    pass


if __name__=="__main__":
    kkonsole()
