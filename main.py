from drive_utils import valid_types, upload_list_and_move
import os
from datetime import datetime
from data_manager import get_metadata, add_to_default_db
import uuid
import json
# incorporar en pipeline https://github.com/ytdl-org/youtube-dl
# incorporar https://github.com/beetbox/beets


# TODO guardar en DB formato de archivo ???
# TODO store db in drive
# TODO batch file upload ??
# Escribir archivo es destino con mismo nombre??
# todo escribir archivos a archivo texto antes de pasar en caso de errores
# todo listar archivos que no estan en DB para borrar y limpiar
# todo colocar listas de reproduccion
# todo oepn by artis, open by etc

# incorporar metadata estandarization https://musicbrainz.org/doc/FreeDB_Gateway


# watch -n0 "python cmd.py --random 1 | xargs cvlc --play-and-exit"
# python cmd.py --list | dmenu -f | awk 'BEGIN {FS=" ,, ";}{print $2}' | xargs -r python cmd.py --play | xargs -r cvlc --play-and-exit



def scan_folder(path): # generate metadata from folder
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames]
    data_list = []
    for elem in files:
        ext = elem.split('.')[-1]
        if ext in valid_types:

            # generate name
            name = "{0}__{1}.enc".format(datetime.now().strftime("%H-%M-%S-%d-%b-%Y"),str(uuid.uuid4()))
            t={'nombre_obj' : name,'nombre_old' : elem}
            data_list.append(t)

        else:
            print("Skiping {0} -- {1} --  not in valid types".format(elem,ext.capitalize()))

    return data_list

def now_string():
    import datetime
    return datetime.datetime.now().strftime("%Y-%b-%d_%H:%M")

import argparse
import random
from data_manager import get_or_create_metadata_database
from drive_utils import download_and_decript, folder_out

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--resume')
    
    args = parser.parse_args()
    if not args.resume:
        name = 'list_to_upload_{0}.json'.format(now_string())
        # scan folder reading metadata
        x=scan_folder('files_to_upload')

        # generar archivo intermedio para resume
        with open(name,'w') as f:
            json.dump(x,f, indent=4, sort_keys=True)
    else:
        name = args.resume
        print("Resuming upload from file {0}".format(name))
        with open(name,'r') as f:
            x=json.load(f)

    # upload files
    upload_list_and_move(x)


    # generate metadata database
    add_to_default_db(folder_out)





