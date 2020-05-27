import datetime
from time import sleep
from os import system
import glob
import os
#sqlalchemy import
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#custome import
from shelper import pgconnstring
from supload.supload import upload_file
from pydocker import config_file

#global variables
jobj = config_file('config.json')
s3_bucket = jobj['s3_bucket_name']
s3_folder = jobj['s3_folder']

total_passed = 0
total_failed = 0

failed_files = list()
success_files = list()

localsession = None
local_engine = None

remotesession = None
remote_engine = None
Base = declarative_base()


#global vars

success_count = 0
old_numbers = 0
hist_dict = dict()


# table local



class upload_table(Base):
    __tablename__ = 'upload'
    link = Column(String,primary_key=True)
    updatedon  = Column(String)

#table remote
connstring_remote = pgconnstring()
class RemoteTable(Base):
    __tablename__ = 'tbl_misc_links_peoplechecker'
    t_link = Column(String,primary_key=True)
    t_status = Column(String)
    awsurl = Column(String)


def create_remote_session():
    #remove engine and session
    global remotesession
    global remote_engine
    conn_string_remote = pgconnstring()
    remote_engine = create_engine(conn_string_remote,echo=False)
    remote_session = sessionmaker(bind=remote_engine)
    table_objects = [Base.metadata.tables['tbl_misc_links_peoplechecker']]
    Base.metadata.create_all(remote_engine,tables=table_objects)
    remotesession = remote_session()





def create_local_session():
    #local engine and session
    global localsession
    global local_engine
    conn_string_local = 'sqlite:///upload_satus.db'
    local_engine = create_engine(conn_string_local,echo=False)
    local_session = sessionmaker(bind=local_engine)
    table_objects =[Base.metadata.tables['upload']]
    Base.metadata.create_all(local_engine,tables=table_objects)
    localsession = local_session()


def update_remote(link,awsurl):
    data = remotesession.query(RemoteTable).filter(RemoteTable.t_link ==link) #pylint: disable=maybe-no-member
    
    for row in data:
        row.t_status ='UPLOADED'
        row.awsurl = awsurl
        remotesession.commit() #pylint: disable=maybe-no-member


def upload_remote(link,local_file,force_upload):
    """
    tries to insert the link to local db, if already present 
    then do nothing but if insert is successufl , update the status
    on remote db
    setting up force upload to true by default becaue this function is not meant to be called
    by user directly

    """
    global total_passed
    global total_failed
    global failed_files
    global success_files
    s3_uploaded_link = None


    #query local db to ask if this link was already uploaded or not
    #if returned 0 it mean it was not uploaded previously and
    #uploading fresh
    query_res_count = len(list(localsession.query(upload_table.link).filter(upload_table.link==link))) #pylint: disable=maybe-no-member

    #force uplod will ignore the local status
    #and uplod to s3 
    
    if (query_res_count == 0)  or (force_upload == True ):
        correct_upload,s3_uploaded_link =  upload_file(local_file,s3_folder,s3_bucket,supress_print=False)  
        if correct_upload:
            total_passed += 1
            #if s3 upload is successful then only add the data to local table 
            #and update remote table
            new_ua = upload_table(link=link,updatedon=datetime.datetime.now())
            localsession.add(new_ua) #pylint: disable=maybe-no-member
            localsession.commit() #pylint: disable=maybe-no-member
            #update the remote db
            update_remote(link=link,awsurl=s3_uploaded_link)
            success_files.append(local_file)
            return True
        else:
            total_failed +=1
            failed_files.append(local_file)
            return False
    else:
        return False


def close_all_sessions():
    localsession.close() #pylint: disable=maybe-no-member
    local_engine.dispose()#pylint: disable=maybe-no-member
    
    remotesession.close()#pylint: disable=maybe-no-member
    remote_engine.dispose()#pylint: disable=maybe-no-member


from bs4 import BeautifulSoup
def get_link_from_html(link):
    with open(link,'r',encoding='utf-8') as f:
        html = f.read()
        soup = BeautifulSoup(html,'html.parser')
        custom_data_tag = soup.find('div',{'id':'custom_data'})
        link_name = custom_data_tag.find('h2',{'id':'current_url'}).text
        return link_name

def watch_folder(force_upload=True):
    global success_count
    global old_numbers
    global hist_dict
    system('clear')
    create_local_session() #open_session
    create_remote_session() #close_session
    sub_directs = glob.glob("*/")
    
    dictdata = dict()
    for directory in sub_directs:
        all_html_files =  glob.glob(os.path.join(directory,'*.html'))
        for html_file in all_html_files:
            link_name = get_link_from_html(link=html_file)
            was_uploaded = upload_remote(link_name,html_file,force_upload)

            #delte file after upload to s3
            if was_uploaded:
                os.remove(html_file)
                

        #keeping the history
        dictdata[directory] = len(all_html_files)
     

    print("{:<30} {:<15}".format('bucket_name','html_count'))
    print('--------------------------------------------------')
    #history of each folder
    for k,v in dictdata.items():
        hist_dict[k] = hist_dict.get(k,0) + int(v)


    for k,v in hist_dict.items():
        print ("{:<30} {:<15}".format(k.replace('/',''), v),flush=True)


    
    print('******************************************************')
    localsession.commit() #pylint: disable=maybe-no-member
    remotesession.commit() #pylint: disable=maybe-no-member
    close_all_sessions() #close session
    
    set_actual_fail_upload = set(failed_files).difference(set(success_files)) 
    print('failed upload')
    print('----------')
    for sq,el in enumerate(set_actual_fail_upload):
        print(f'{sq}.{el}')
    print('******************************************')
    print('success upload')
    print('----------')
    for sq,el in enumerate(success_files):
        print(f'{sq}.{el}')
    success_count = success_count + len(success_files) 
    print(f'total success upload : {success_count} total failed upload: {total_failed}')
    print(f'updated on :{datetime.datetime.now()}')

    success_files.clear()

    


def keep_update_loop():
    while True:
        watch_folder(force_upload=False)
        sleep(10)

def do_force_upload():
    watch_folder(force_upload=True)


if __name__ == "__main__":
    # local_statusfile()
    # insert_local_status()
    keep_update_loop()
    #create_remote_session()