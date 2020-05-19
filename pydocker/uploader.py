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

#global variables
localsession = None
local_engine = None

remotesession = None
remote_engine = None
Base = declarative_base()

# table local

class upload_table(Base):
    __tablename__ = 'upload'
    link = Column(String,primary_key=True)
    updatedon  = Column(String)

#table remote
connstring_remote = pgconnstring()
class RemoteTable(Base):
    __tablename__ = 'tbl_misc_links_peoplechecker'
    pkeyserial = Column(Integer,primary_key=True)
    t_link = Column(String)
    t_status = Column(String)


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


def update_remote(link):
    data = remotesession.query(RemoteTable).filter(RemoteTable.t_link ==link) #pylint: disable=maybe-no-member
    
    for row in data:
        row.t_status ='UPLOADED2'
        remotesession.commit() #pylint: disable=maybe-no-member


def upload_remote(link):
    """
    tries to insert the link to local db, if already present 
    then do nothing but if insert is successufl , update the status
    on remote db

    """
    query_res_count = len(list(localsession.query(upload_table.link).filter(upload_table.link==link))) #pylint: disable=maybe-no-member
    
    if query_res_count == 0:
        new_ua = upload_table(link=link,updatedon=datetime.datetime.now())
        localsession.add(new_ua) #pylint: disable=maybe-no-member
        localsession.commit() #pylint: disable=maybe-no-member
        #update the remote db
        update_remote(link=link)
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
        soup = BeautifulSoup(f.read(),'html.parser')
        custom_data_tag = soup.find('div',{'id':'custom_data'})
        link_name = custom_data_tag.find('h2',{'id':'current_url'}).text
        return link_name

def watch_folder():    
    system('clear')
    create_local_session() #open_session
    create_remote_session() #close_session
    sub_directs = glob.glob("*/")
    dictdata = dict()
    for directory in sub_directs:
        all_html_files =    glob.glob(os.path.join(directory,'*.html'))
        for html_file in all_html_files:
            link_name = get_link_from_html(link=html_file)
            upload_remote(link_name)


        dictdata[directory] = len(all_html_files)

    print("{:<30} {:<15}".format('bucket_name','html_count'))
    print('--------------------------------------------------')

    for k,v in dictdata.items():
        print ("{:<30} {:<15}".format(k.replace('/',''), v),flush=True)
    print(f'updated on :{datetime.datetime.now()}')
    localsession.commit()
    remotesession.commit()
    close_all_sessions() #close session
    


def keep_update_loop():
    while True:
        watch_folder()
        sleep(10)




if __name__ == "__main__":
    # local_statusfile()
    # insert_local_status()
    keep_update_loop()
    #create_remote_session()