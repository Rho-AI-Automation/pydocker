import docker
from subprocess import Popen,PIPE
from time import sleep

client = docker.from_env()

def is_running(in_container_name):
    all_containers = client.containers.list()
    for container in all_containers:
        container_name = container.name
        
        if in_container_name == container_name:
            return True
    return False
        
def stop_instance(container_name):
    all_containers = client.containers.list()
    for container in all_containers:
        if str(container.name) == container_name:
            container.stop()
            return True
    return False


def stop_all_splash():
    splash_names = ['splash_8050','splash_8051','splash_8052','splash_8053','splash_8054']
    for sname in splash_names:
        run_state = is_running(sname)
        
        if run_state == True:
            stop_instance(sname)
        else:
            print(f'container {sname} not running')



def keep_splash_running():
    stop_all_splash()
    splash_names = ['splash_8050','splash_8051','splash_8052','splash_8053','splash_8054']
    while True:
        for instance_name in splash_names:

            is_run = is_running(instance_name)

            if is_run == True:
                print(f'{instance_name} is running')
            else:
                print(f'{instance_name} is dead')
                print('executing script')
                port = int(instance_name.split('_')[1])
                f_splash_string = f'screen -S splash_{str(port)} -d -m docker run --name {instance_name} -it --rm -p {port}:8050 scrapinghub/splash  --max-timeout 300'
                Popen(f_splash_string,shell=True,stdout=PIPE,stderr=PIPE)
                is_run = is_running(instance_name)
                print(f'current status of {instance_name} : {is_run}')
        sleep(300)






if __name__ == "__main__":
    # keep_splash_running()
    # print(stop_instance('splash_8055'))
    stop_all_splash()

    