import os
from subprocess import Popen,PIPE


def verify_root():
    euid = os.geteuid()
    if euid != 0:
        raise PermissionError('docker needs to run as root')
        sys.exit(0)

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
    image_name = input('enter image name: ')
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



if __name__ == "__main__":
    docrun()