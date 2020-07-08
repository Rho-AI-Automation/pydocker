import os
from subprocess import Popen,PIPE
from pathlib import Path
import sys
import json
from time import sleep
import click
import subprocess


def progress_bar(bar_for=30):
    done = 0
    full_bar = 90
    for idx in range(bar_for):
        done += int(full_bar/bar_for)
        not_done = ' ' * (full_bar - done)
       
        sys.stdout.write("\r[{}{}]".format('=' * done,not_done))
        sys.stdout.flush()
        sleep(1)
    print('\n')


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
    d_list = ['s3_bucket_name','s3_folder']

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

    impage_name = input('enter image name:[pkumdev/rho-ubuntu]')
    image_string = None

    image_string = f'docker build --no-cache -t {impage_name} --build-arg device=/dev/net/tun --build-arg sysctl=net.ipv6.conf.all.disable_ipv6=0 .'

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


def docexec_gscrape(buckt_name,vpnserver):
    bucket_path = os.path.join(os.getcwd(),buckt_name)
    nipchanger_command = f'docker exec {buckt_name} screen -S vpn -d -m {vpnserver}'
    gscraper_command = f"docker exec -w {bucket_path} {buckt_name} screen -S scraper -d -m gscrape"

    nrun = Popen(nipchanger_command,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = nrun.communicate()
    if strerr:
        print(strerr)
    if stdout:
        print(stdout.decode('utf-8'))
    print(f'{vpnserver} executed ,executing gscraper')
    progress_bar()
    # print('support for insline gscraper due to threads disabled')
    # print('please run gscrape inside screen in docker manualy')

    grun = Popen(gscraper_command,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = grun.communicate()
   
    
    if strerr:
        print(strerr)
    if stdout:
        print(stdout.decode('utf-8'))

    print(f'docker exec -it {buckt_name} bash')


def doc_exec_sel_run(buckt_name):
    #all_ports = [54420,54421,54422,54423,54424]
    all_ports = [54420]

    for port in all_ports:
        print(f'selenium on port {port}')
        selenium_command = f'docker exec {buckt_name} screen -S  runsel -d -m runselbucket'
        nrun = Popen(selenium_command,shell=True,stdout=PIPE,stderr=PIPE)
        stdout,strerr = nrun.communicate()
        if strerr:
            print(strerr)
        if stdout:
            print(stdout.decode('utf-8'))


def doc_exec_splash_run(buckt_name):
    selenium_command = f'docker exec {buckt_name} screen -S  runsplash -d -m runsplash'
    nrun = Popen(selenium_command,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = nrun.communicate()
    if strerr:
        print(strerr)
    if stdout:
        print(stdout.decode('utf-8'))


def doc_exec_single_run(buckt_name):
    selenium_command = f'docker exec {buckt_name} screen -S  runsingle -d -m runsinglebuckt'
    nrun = Popen(selenium_command,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = nrun.communicate()
    if strerr:
        print(strerr)
    if stdout:
        print(stdout.decode('utf-8'))




def docexec_ucheck(buckt_name,vpnserver):
    
    bucket_path = os.path.join(os.getcwd(),buckt_name)
    nipchanger_command = f'docker exec {buckt_name} screen -S vpn -d -m {vpnserver}'
    gscraper_command = f"docker exec -w {bucket_path} {buckt_name} screen -S scraper -d -m ucheck"

    nrun = Popen(nipchanger_command,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = nrun.communicate()
    if strerr:
        print(strerr)
    if stdout:
        print(stdout.decode('utf-8'))
    print(f'{vpnserver} executed ,executing url checker')
    progress_bar()
    # print('support for insline gscraper due to threads disabled')
    # print('please run gscrape inside screen in docker manualy')

    grun = Popen(gscraper_command,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = grun.communicate()
   
    
    if strerr:
        print(strerr)
    if stdout:
        print(stdout.decode('utf-8'))


    print(f'docker exec -it {buckt_name} bash')




def run_command(buckt_name,command_name,screen_name):
    
    command_exec = f'docker exec {buckt_name} screen -dmS {screen_name} sh -c "{command_name};exec bash"'
    nrun = Popen(command_exec,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = nrun.communicate()
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



def gscraper_run_google(image_name,vpn,container_name):

    if container_name is None:
        container_name = input('Enter Container Name : ')

    verify_root()
    bucket_folder = os.path.join(os.getcwd(),container_name)
    container_string = f'docker run -it -d --rm --name {container_name}  --cap-add=NET_ADMIN --device /dev/net/tun --dns 8.8.8.8 --sysctl net.ipv6.conf.all.disable_ipv6=0 -v {bucket_folder}:{bucket_folder} -w {bucket_folder} {image_name} bash'
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
    docexec_gscrape(buckt_name=container_name,vpnserver=vpn)


def gscraper_run_jsdom(image_name,vpn,container_name):

    if container_name is None:
        container_name = input('Enter Container Name : ')

    verify_root()
    bucket_folder = os.path.join(os.getcwd(),container_name)
    container_string = f'docker run -it -d --rm --name {container_name}  --cap-add=NET_ADMIN --device /dev/net/tun --dns 8.8.8.8 --sysctl net.ipv6.conf.all.disable_ipv6=0 -v {bucket_folder}:{bucket_folder} -w {bucket_folder} {image_name} bash'
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
    run_command(buckt_name=container_name,screen_name='vpn',command_name='vipchanger')
    progress_bar()
    print('vpn fired')

    print('file olders created')
    print('jsdom rendering engine fired')
    run_command(buckt_name=container_name,screen_name='jsdom',command_name='singlejsdom')
    print('jsdom rendering engine fired')
    run_command(buckt_name=container_name,screen_name='killer',command_name='pkiller')
    print('process killer fired')

def gscraper_run_chdriver(image_name,vpn,container_name):

    if container_name is None:
        container_name = input('Enter Container Name : ')

    verify_root()
    bucket_folder = os.path.join(os.getcwd(),container_name)
    container_string = f'docker run -it -d --rm --name {container_name}  --cap-add=NET_ADMIN --device /dev/net/tun --dns 8.8.8.8 --sysctl net.ipv6.conf.all.disable_ipv6=0 -v {bucket_folder}:{bucket_folder} -w {bucket_folder} {image_name} bash'
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
    run_command(buckt_name=container_name,screen_name='vpn',command_name='vipchanger')
    progress_bar()
    print('vpn fired')
    run_command(buckt_name=container_name,screen_name='chdriver',command_name='singlechdriver')
    print('chromedriver rendering engine fired')
    run_command(buckt_name=container_name,screen_name='killer',command_name='pkiller')
    print('process killer fired')


def uchecker_run(vpn,container_name,image_name):
    
    verify_root()
    bucket_folder = os.path.join(os.getcwd(),container_name)
    container_string = f'docker run -it -d --rm --name {container_name}  --cap-add=NET_ADMIN --device /dev/net/tun --dns 8.8.8.8 --sysctl net.ipv6.conf.all.disable_ipv6=0 -v {bucket_folder}:{bucket_folder} -w {bucket_folder} {image_name} bash'
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
    docexec_ucheck(buckt_name=container_name,vpnserver=vpn)
    print('urlchecker with CURL only executed')
    
    # run_command(buckt_name=container_name,screen_name='chdriver',command_name='singlechdriver')
    # print('chromedriver rendering engine fired')
    # run_command(buckt_name=container_name,screen_name='jsdom',command_name='singlejsdom')
    # print('jsdom rendering engine fired')


    
    # print('running selenium')
    # doc_exec_sel_run(container_name)
    # print('running splash')
    # doc_exec_splash_run(container_name)




@click.command()
@click.option('--vpn', default='nipchanger', help='vpn server ,nipchanger or vipchanger')
@click.option('--image_name',default='pkumdev/rho-ubuntu',prompt=True, help='vpn server ,nipchanger or vipchanger')
def bulk_ucheck(vpn,image_name):
    num_ins = int(input('number of containers you want to run: '))
    for i in range(1,num_ins+1):
        base_bucket = 'bucket_uc_'+str(i)
        uchecker_run(vpn=vpn,container_name=base_bucket,image_name=image_name)

    #rendering engline



@click.command()
@click.option('--vpn', default='vipchanger', help='vpn server ,nipchanger or vipchanger')
@click.option('--image_name',default='pkumdev/rho-ubuntu',prompt=True, help='vpn server ,nipchanger or vipchanger')
def bulk_gscrape_google(vpn,image_name):
    bucket_count = int(input('Enter bucket count: '))
    
    for i in range(1,bucket_count+1):
        base_bucket = 'bucket'+str(i)
        gscraper_run_google(container_name=base_bucket,vpn=vpn,image_name=image_name)
    

@click.command()
@click.option('--vpn', default='vipchanger', help='vpn server ,nipchanger or vipchanger')
@click.option('--image_name',default='pkumdev/rho-ubuntu',prompt=True, help='vpn server ,nipchanger or vipchanger')
def bulk_gscrape_jsdom(vpn,image_name):
    bucket_count = int(input('Enter bucket count: '))
    
    for i in range(1,bucket_count+1):
        base_bucket = 'bucket_jsdom'+str(i)
        gscraper_run_jsdom(container_name=base_bucket,vpn=vpn,image_name=image_name)


@click.command()
@click.option('--vpn', default='vipchanger', help='vpn server ,nipchanger or vipchanger')
@click.option('--image_name',default='pkumdev/rho-ubuntu',prompt=True, help='vpn server ,nipchanger or vipchanger')
def bulk_gscrape_chdriver(vpn,image_name):
    bucket_count = int(input('Enter bucket count: '))
    
    for i in range(1,bucket_count+1):
        base_bucket = 'bucket_chdr'+str(i)
        gscraper_run_chdriver(container_name=base_bucket,vpn=vpn,image_name=image_name)


if __name__ == "__main__":
    bulk_ucheck()
    # bulk_gscrape()
    # doc_exec_sel_run('bucket1')
    # bulk_ucheck()
    pass
