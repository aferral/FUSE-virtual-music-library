from drive_utils import valid_types, upload_list_and_move, folder_out
import os
from datetime import datetime
from data_manager import get_metadata, add_to_default_db
import uuid
import json
import shutil

import argparse
import random
from data_manager import get_or_create_metadata_database
from drive_utils import download_and_decript, folder_out,folder_in

# incorporar en pipeline https://github.com/ytdl-org/youtube-dl
# incorporar https://github.com/beetbox/beets (O algo similar)


# TODO guardar en DB formato de archivo ???
# TODO store db in drive
# TODO batch file upload ??
# todo listar archivos que no estan en DB para borrar y limpiar
# todo colocar listas de reproduccion
# todo oepn by artis, open by etc

# generar jerarquia artista-> albums -> songs

# incorporar metadata estandarization https://musicbrainz.org/doc/FreeDB_Gateway


# watch -n0 "python cmd.py --random 1 | xargs cvlc --play-and-exit"
# python cmd.py --list | dmenu -f | awk 'BEGIN {FS=" ,, ";}{print $2}' | xargs -r python cmd.py --play | xargs -r cvlc --play-and-exit


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
    add_metadata(file_path,id_file,size,ext)

    # move to out_path
    out_path = os.path.join(folder_out, file_path.replace(os.path.sep,'_') )
    shutil.move(file_path, out_path)
    print('Just finished: {0}'.format(file_path))

def scan_folder(path): # generate metadata from folder
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames]
    data_list = []
    for elem in files:
        ext = elem.split('.')[-1]
        if ext in valid_types:
            full_process(elem)
        else:
            print("Skiping {0} -- {1} --  not in valid types".format(elem,ext.capitalize()))

    return data_list


if __name__ == "__main__":

    scan_folder(folder_in)




