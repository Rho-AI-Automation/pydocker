import os
from subprocess import Popen,PIPE
from pathlib import Path
import sys
import json


def custom_print(printstring):
    pass

def create_db_file(dbdata_file_path):
    d_list = ['dbname','user','host','password','ApplicationName']
    jobj = None
    config_file_path = dbdata_file_path

    if os.path.exists(config_file_path):
        with open(config_file_path,'r',encoding='utf-8') as f:
            jobj = json.load(f)
            all_keys = jobj.keys()
            for element in d_list:
                if not element in all_keys:
                    jobj[element] = input(f'enter value for {element} :')

        #put the new data in config file
        with open(config_file_path,'w',encoding='utf-8') as fp:
            json.dump(jobj,fp)
        return jobj
    else:
        #if file does not exists
        jobj = dict()
        all_keys = jobj.keys()
        for element in d_list:
            if not element in all_keys:
                jobj[element] = input(f'enter value for {element} :')
        with open(config_file_path,'w',encoding='utf-8') as fp:       
            json.dump(jobj,fp)
        return jobj


def config_file(config_file_path):
    d_list = ['num_instances','notify_email','recycle_proxy','min_load','max_load','list_country_flags',
    'num_instances','notify_email','db_table_name','s3_bucket_name','s3_folder','max_req_per_ip',
    'blocked_text_list','min_time_bet_request','max_time_between_req','is_testing']

    jobj = None
    config_file_path = config_file_path
    
    if os.path.exists(config_file_path):
        with open(config_file_path,'r',encoding='utf-8') as f:
            jobj = json.load(f)
            all_keys = jobj.keys()
            for element in d_list:
                if not element in all_keys:
                    if 'list' in element:
                        #if list is expected
                        jobj[element] = input(f'list for {element} :' ).split(',')
                    else:
                        jobj[element] = input(f'enter value for {element} :')

        #put the new data in config file
        with open(config_file_path,'w',encoding='utf-8') as fp:
            json.dump(jobj,fp)
        return jobj
    else:
        jobj = dict()
        all_keys = jobj.keys()
        for element in d_list:
            if not element in all_keys:
                if 'list' in element:
                        #if list is expected
                        jobj[element] = input(f'list for {element} :' ).split(',')
                else:
                    jobj[element] = input(f'enter value for {element} :')
        with open(config_file_path,'w',encoding='utf-8') as fp:
            json.dump(jobj,fp)
        return jobj


def verify_root():
    euid = os.geteuid()
    if euid != 0:
        raise PermissionError('docker needs to run as root')

def docreate():
    verify_root()

    impage_name = input('enter image name: ')
    image_string = None

    image_string = f'docker build -t {impage_name} --build-arg device=/dev/net/tun --build-arg sysctl=net.ipv6.conf.all.disable_ipv6=0 .'

    irun = Popen(image_string,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = irun.communicate()
    
    if strerr:
        print(strerr)
    if stdout:
        print(stdout)


def list_images():
    verify_root()
    container_string =  'docker images --format "{{.Repository}}"'
    drun = Popen(container_string,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = drun.communicate()
    
    if strerr:
        print(strerr)
    if stdout:
        print('images found')
        print('------------')
        stdout = stdout.decode("utf-8")
        all_images = str(stdout).split('\\')
        for im in all_images:
            print(im.strip())
        

def docrun():
    verify_root()
    list_images()

    image_name = input('enter image name :')
    container_name = input('enter container name :')
    container_string = f'docker run -it -d --rm --name {container_name}  --cap-add=NET_ADMIN --device /dev/net/tun --dns 8.8.8.8 --sysctl net.ipv6.conf.all.disable_ipv6=0 -v $PWD:$PWD -w $PWD {image_name} bash'
    drun = Popen(container_string,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = drun.communicate()
    
    if strerr:
        print(strerr)
    if stdout:
        print('image id')
        print('---------')
        print(stdout.decode('utf-8'))



def docexec_gscrape(buckt_name):
    
    bucket_path = os.path.join(os.getcwd(),buckt_name)
    nipchanger_command = f'docker exec {buckt_name} screen -S vpn -d -m nipchanger'
    gscraper_command = f"docker exec -w {bucket_path} {buckt_name} screen -S scraper -d -m gscrape"

    nrun = Popen(nipchanger_command,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = nrun.communicate()
    print('nipchanger executed ,wait 10s to execute gscraper')
    if strerr:
        print(strerr)
    if stdout:
        print(stdout.decode('utf-8'))

    grun = Popen(gscraper_command,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = grun.communicate()
   
    
    if strerr:
        print(strerr)
    if stdout:
        print(stdout.decode('utf-8'))


def create_files_gscrape(container_name='bucket1'):
    
    #create bucket folder
    bucket_folder = os.path.join(os.getcwd(),container_name)
    if not os.path.exists(bucket_folder):
        os.mkdir(bucket_folder)
    
    #create openvpn login files
    vpn_pass_path = os.path.join(bucket_folder,'vpnpass.txt')
    if not os.path.exists(vpn_pass_path):
        uname = input('Nord username :')
        pswd = input('Nord password :')
        with open(vpn_pass_path,'w') as f:
            f.write(uname)
            f.write('\n')
            f.write(pswd)

    #create dbdata.json
    dbdatajson = os.path.join(bucket_folder,'dbdata.json')
    if not os.path.exists(dbdatajson):
        create_db_file(dbdatajson)
    
    #create config file
    configfile = os.path.join(bucket_folder,'config.json')
    if not os.path.exists(configfile):
        config_file(config_file_path=configfile)

    #create username password for robot
    ufilename = os.path.join(bucket_folder,'uname.txt')
    pfilename = os.path.join(bucket_folder,'paswd.txt')

    if not os.path.exists(ufilename):
        with open(ufilename,'w') as f:
            email = input("Please enter robot email id : ")
            f.write(email)
    if not os.path.exists(pfilename):
        with open(pfilename,'w') as f:
            password = input("Please enter robot password, this will be stored in plain text : ")
            f.write(password)


def gscraper_run():
    
    verify_root()
    container_name = input('enter bucket name :')
    bucket_folder = os.path.join(os.getcwd(),container_name)
    container_string = f'docker run -it -d --rm --name {container_name}  --cap-add=NET_ADMIN --device /dev/net/tun --dns 8.8.8.8 --sysctl net.ipv6.conf.all.disable_ipv6=0 -v {bucket_folder}:{bucket_folder} -w {bucket_folder} rho-ubuntu bash'
    drun = Popen(container_string,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = drun.communicate()

    if strerr:
        print(strerr)
        print('\n')
        print('bucket already created, you must run commands manually inside it or stop bucket')
        raise ValueError('error while creating container')
    if stdout:
        print('image id')
        print('---------')
        print(stdout.decode('utf-8'))


   
    create_files_gscrape(container_name=container_name)
    print('file olders created')
    docexec_gscrape(buckt_name=container_name)
  

def watch_folder():
    sub_directs = [x[0] for x in os.walk('.')]


if __name__ == "__main__":
    docrun()
