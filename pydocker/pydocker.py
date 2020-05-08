import os
from subprocess import Popen,PIPE


def verify_root():
    euid = os.geteuid()
    if euid != 0:
        raise PermissionError('docker needs to run as root')
        sys.exit(0)


def docrun():
    verify_root()
    container_name = input('enter container name :')
    container_string = f'docker run -it -d --rm --name {container_name}  --cap-add=NET_ADMIN --device /dev/net/tun --dns 8.8.8.8 --sysctl net.ipv6.conf.all.disable_ipv6=0 -v $PWD:$PWD -w $PWD rho-ubuntu bash'
    drun = Popen(container_string,shell=True,stdout=PIPE,stderr=PIPE)
    stdout,strerr = drun.communicate()
    
    if strerr:
        print(strerr)
    if stdout:
        print(stdout)



if __name__ == "__main__":
    docrun()