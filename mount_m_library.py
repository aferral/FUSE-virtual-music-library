#!/usr/bin/env python
from getpass import getuser
from pwd import getpwnam 
import grp
import logging
import io
import errno
from errno import EACCES
from os.path import realpath
from sys import argv, exit
from threading import Lock
from datetime import datetime
import os
from stat import S_IFMT, S_IMODE, S_IFDIR, S_IFREG, S_IRWXU, S_IRGRP, S_IROTH
from fuse import FUSE, FuseOSError, Operations
import mutagen
import io
from data_manager import get_or_create_metadata_database
from drive_utils import download_and_decript
from fuse import FuseOSError



log = logging.getLogger('fuse')

class LoggingMixIn:

    def __call__(self, op, path, *args):
        log.debug('-> %s %s ', op, path)
        try:
            ret = getattr(self, op)(path, *args)
            return ret
        except OSError as e:
            ret = str(e)
            log.exception(ret)
            raise e
class Virtual_Library(LoggingMixIn, Operations):

    def __init__(self,modo_dummy=True):

        self.root = ''
        print(self.root)

        self.rwlock = Lock()

        self.metadata_obj = get_or_create_metadata_database()
        lista = self.metadata_obj.list(as_dict=True) 

        self.dummy=modo_dummy


        all_dict = {}

        # agrupa todos los discos por artista / album
        for elem in lista:
            artista=elem['Band'] if elem['Band'] != '' else 'No_info' 
            album=elem['Album'] if elem['Album'] != '' else 'No_info'
            all_dict.setdefault(artista,{}).setdefault(album,[]).append(elem)

        file_dict={}
        folder_dict={}

        def c_name(d):
            return "{0}_{1}_{2}.{3}".format(d['Song'],d['Album'],d['Band'],d['ext'])
            pass

        file_dict={}
        folder_dict={}

        def add(d,current_path):
            for k in d:
                if type(k) == dict:
                    f_path = os.path.join(current_path,c_name(k))
                    folder_dict.setdefault(current_path,[]).append(f_path)
                    file_dict[f_path] = k
                else:
                    path_c = os.path.join(current_path,k)
                    folder_dict.setdefault(current_path,[]).append(path_c)
                    add(d[k],path_c)
            return
        add(all_dict,'/')

        self.file_dict = file_dict
        self.folder_dict = folder_dict


        self.lista = self.metadata_obj.list(as_dict=True) # {'Band':b, 'Album':alb, 'Song' : s,'id_drive' : idd, 'size' , 'ext'}
        self.data_dict = {}
        self.library_rows = []
        for d in self.lista:
            file_name = c_name(d)
            self.data_dict[file_name] = d    
            self.library_rows.append(file_name)

        # Prepare dummy files
        folder_with_dummys = 'dummy_files'
        self.dummy_dict = {}
        for d_path in os.listdir(folder_with_dummys):
            ext = d_path.split('.')[-1]
            f_path = os.path.join(folder_with_dummys,d_path)
            # prepare dummy file for metadata
            with open(f_path,'rb') as f:
                b_buffer=io.BytesIO(f.read())
            data_dummy = b_buffer.read()

            self.dummy_dict[ext] = {'buffer' : b_buffer, 'data' : data_dummy} 

    listxattr = None
    getxattr = None
    utimens = os.utime

    def convert_to_full(self,path):
        return os.path.join(self.root,path[1:] if path[0] == os.path.sep else path)


    def create_dumm_file(self,metadata):
        ext = metadata['ext']
        d = self.dummy_dict[ext]
        t_buffer = d['buffer']
        t_data = d['data']

        t_buffer.seek(0)
        org=mutagen.File(t_buffer,easy=True)
        org['artist'] = metadata['Band']
        org['title'] = metadata['Song']
        org['album'] = metadata['Album']

        xb = io.BytesIO(t_data)
        xb.seek(0)
        org.save(xb)
        xb.seek(0)
        return xb

    def is_virtual_path(self,path):
        is_folder = path in self.folder_dict
        is_file = path in self.file_dict
        return is_folder,is_file

    def access(self, path, mode):
        access = any(self.is_virtual_path(path)) 
        if access:
            return

        full_path = self.convert_to_full(path)
        log.info('Access {0} , {1}'.format(path,full_path))
        if not os.access(full_path, mode):
            print("DOESNT HAVE PERMISSIONS {0} {1}".format(full_path,mode))
            raise FuseOSError(EACCES)



    def getattr(self, path, fh=None):
        def dummy_descrp():
            current_user=getuser()
            out = {}

            out['st_atime'] = datetime.now().timestamp()*1.0
            out['st_ctime'] = datetime.now().timestamp()*1.0
            out['st_mtime'] = datetime.now().timestamp()*1.0
            out['st_gid'] = grp.getgrnam(current_user).gr_gid
            out['st_mode']= S_IFREG | S_IRWXU | S_IRGRP | S_IROTH
            out['st_nlink']= 1
            out['st_size']= 1
            out['st_uid']= getpwnam(current_user).pw_uid
            return out

        def parse_real(x):
            st = os.lstat(x)
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))


        is_folder,is_file=self.is_virtual_path(path)
        log.info('Path {0} isfol {1} isf {2}'.format(path,is_folder,is_file))

        if is_folder:
            data_descp = dummy_descrp()
            data_descp['st_size'] = 4096
            data_descp['st_mode']= S_IFDIR | S_IRWXU | S_IRGRP | S_IROTH
            data_descp['st_nlink'] = len(self.folder_dict[path])
            return data_descp
        elif is_file:

            data = self.file_dict[path]
            data_descp = dummy_descrp()
            if not self.dummy:
                size = data['size']
            else:
                ext=data['ext']
                temp_buffer = self.create_dumm_file(data)
                size = len(temp_buffer.read())
            data_descp['st_size'] = size

            return data_descp


        else:
            full_path = self.convert_to_full(path)

            return parse_real(full_path)



    def read(self, path, size, offset, fh):

        is_folder,is_file=self.is_virtual_path(path) 

        with self.rwlock:


            if is_file:
                metadata = self.file_dict[path]

                if self.dummy:
                    temp_buffer = self.create_dumm_file(metadata)
                    temp_buffer.seek(offset)
                    return temp_buffer.read(size)

                else:
                    id_file = metadata['id_drive']
                    temp_io = io.BytesIO()
                    download_and_decript(id_file, temp_io)
                    temp_io.seek(offset)
                    return temp_io.read(size)
            else:
                full_path = self.convert_to_full(path)
                return os.open(full_path).seek(offset).read(size)

    def opendir(self,path):
        is_folder,is_file=self.is_virtual_path(path) 
        if is_folder:
            return 0

        res=super().opendir(path)
        return res

    def readdir(self, path, fh):
        is_folder,is_file=self.is_virtual_path(path) 

        dirents = ['.', '..']

        if is_folder:
            to_return = list(map(lambda x : x[1:] if x[0] == os.path.sep else x ,self.folder_dict[path]))
            to_return = list(map(lambda x : os.path.split(x)[-1] ,self.folder_dict[path]))
            dirents += to_return

        else:
            full_path = self.convert_to_full(path)
            if os.path.isdir(full_path):
                dirents.extend(os.listdir(full_path))
        return dirents 




import argparse
from config_parse import mountpoint

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start the virtual filesystem')
    parser.add_argument('--dummy', action='store_true',help='Dont download the files just create dummy files with the metadata')
    parser.add_argument('--verbose','-v',help='Show debug information',action='store_true'),
    args = parser.parse_args()

    # Make mountpoint folder 
    os.makedirs(mountpoint,exist_ok=True)

    dummy = args.dummy
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    vl = Virtual_Library(modo_dummy=dummy)

    fuse = FUSE(vl, mountpoint, foreground=True, nothreads=True)
