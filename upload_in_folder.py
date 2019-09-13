from drive_utils import valid_types,  folder_out
import os
from datetime import datetime
from data_manager import get_metadata 
import uuid
import json
import shutil

import argparse
import random
from data_manager import get_or_create_metadata_database, add_metadata, default_sql_lite
from config_parse import drive_metadata_id
from drive_utils import download_and_decript, folder_out,folder_in, encript_and_upload, encript_update_file




def get_new_name():
    name = "{0}__{1}.enc".format(datetime.now().strftime("%H-%M-%S-%d-%b-%Y"),str(uuid.uuid4()))
    return name 


def full_process(file_path):
    print('Processing : {0}'.format(file_path))
    # generate name
    new_name = get_new_name() 

    # upload
    new_id = encript_and_upload(file_path,new_name)

    # get size, ext
    size=os.stat(file_path).st_size 
    ext = file_path.split('.')[-1]

    # add metadata to DB
    add_metadata(file_path,new_id,size,ext)

    # move to out_path
    out_path = os.path.join(folder_out, file_path.replace(os.path.sep,'_') )
    shutil.move(file_path, out_path)
    print('Just finished: {0}'.format(file_path))

def scan_folder(path): # generate metadata from folder
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames]
    data_list = []
    n=len(files)
    for ind,elem in enumerate(files):
        ext = elem.split('.')[-1]
        if ext in valid_types:
            print("Processing {0} {1}/{2}".format(elem,ind,n))
            full_process(elem)
        else:
            print("Skiping {0} -- {1} --  not in valid types".format(elem,ext.capitalize()))
    
    # update metadata in drive
    x=get_or_create_metadata_database()
    new_name = 'meta.enc'
    encript_update_file(drive_metadata_id, default_sql_lite, new_name)

    return data_list


if __name__ == "__main__":

    scan_folder(folder_in)




