#!/usr/bin/env python
from __future__ import print_function, absolute_import, division
from pwd import getpwnam 
import grp
import logging
import io
from errno import EACCES
from os.path import realpath
from sys import argv, exit
from threading import Lock
from datetime import datetime
import os
from stat import S_IFMT, S_IMODE, S_IFDIR, S_IFREG, S_IRWXU
from fuse import FUSE, FuseOSError, Operations
from data_manager import get_or_create_metadata_database

# crear lista de archivos segun db


class LoggingMixIn:
    log = logging.getLogger('fuse.log-mixin')

    def __call__(self, op, path, *args):
        self.log.debug('-> %s %s ', op, path)
        ret = '[Unhandled Exception]'
        try:
            ret = getattr(self, op)(path, *args)
            return ret
        except OSError as e:
            ret = str(e)
            raise
        finally:
            #self.log.debug('<- %s %s', op, repr(ret))
            pass

class Virtual_Library(LoggingMixIn, Operations):
    def __init__(self):
        self.root = realpath('/home/aferral/Escritorio/Datos_torre_central')
        print("Path base {0}".format(self.root))
        self.rwlock = Lock()

        self.library_rows = ['Queen0','Queen1','Queen2']
        self.content = ['contenidoA','ContenidoB','ContenidoC']

        self.fd=0


    chmod = os.chmod
    chown = os.chown
    mkdir = os.mkdir
    mknod = os.mknod
    
    listxattr = None
    getxattr = None
    readlink = os.readlink
    rmdir = os.rmdir
    unlink = os.unlink
    utimens = os.utime


    def __call__(self, op, path, *args):
        return super(Virtual_Library, self).__call__(op, self.root + path, *args)
        
        ret = ''
        path_r = os.path.join(self.root,path)
        print("Op: {0} path: {1}".format(op,path_r))
        try:
            ret = getattr(self, op)(path_r, *args)
            return ret
        except OSError as e:
            ret = str(e)
            raise
        finally:
            print(ret)
        return super(Loopback, self).__call__(op, self.root + path, *args)



    def opendir(self,path):
        print('OPEN DIR {0}'.format(path))
        res=super().opendir(path)
        return res


    def access(self, path, mode):
        if not os.access(path, mode):
            raise FuseOSError(EACCES)

    def create(self, path, mode):
        return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)



    def fsync(self, path, datasync, fh):
        if datasync != 0:
          return os.fdatasync(fh)
        else:
          return os.fsync(fh)


    def getattr(self, path, fh=None):
        def dummy_descrp():
            out = {}
            out['st_atime'] = datetime.now().timestamp()*1.0
            out['st_ctime'] = datetime.now().timestamp()*1.0
            out['st_mtime'] = datetime.now().timestamp()*1.0
            out['st_gid'] = grp.getgrnam('aferral').gr_gid
            out['st_mode']= S_IFREG | S_IRWXU#IS_IFREG
            out['st_nlink']=1
            out['st_size']=1000
            out['st_uid']= getpwnam('aferral').pw_uid
            return out 

        print("pt: {0}".format(path))
        def parse_real(path):
            st = os.lstat(path)
            print(st)
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

        resto=os.path.split(path)[-1]
        if path in self.root:
            return parse_real(path)
        elif resto in self.library_rows:
            print("Special path: {0}".format(resto))
            return dummy_descrp()
        else:
            x=parse_real(path)
            print('Returning REAL {0}'.format(x))
            return x



    def link(self, target, source):
        return os.link(source, target)

    def open(self, path, flags):

        resto=os.path.split(path)[-1]
        if resto in self.library_rows:
            print("Special path: {0} ".format(resto))
            self.fd+=1
            return self.fd
        else:
            os.open(path)
            return 0
    def flush(self, path, fh):
        
        resto=os.path.split(path)[-1]
        if resto in self.library_rows:
            print("Special path: {0} ".format(resto))
            return
        else:
            return os.fsync(fh)

    def read(self, path, size, offset, fh):

        resto=os.path.split(path)[-1]
        if resto in self.library_rows:
            print("Special path: {0} params: {1}".format(resto,(size,offset,fh)))
            return b"some initial text datadasfadsffadsdfs"
        else:
            with self.rwlock:
                os.lseek(fh, offset, 0)
                return os.read(fh, size)




    def readdir(self, path, fh):
        out=['.','..'] + self.library_rows # ['.', '..'] + os.listdir(path)
        return out 
        return 



    def release(self, path, fh):

        resto=os.path.split(path)[-1]
        if resto in self.library_rows:
            print("Special path: {0} params: {1}".format(resto,fh))
            return 
        else:
            return os.close(fh)

        

    def rename(self, old, new):
        return os.rename(old, self.root + new)



    def statfs(self, path):
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def symlink(self, target, source):
        return os.symlink(source, target)

    def truncate(self, path, length, fh=None):
        with open(path, 'r+') as f:
            f.truncate(length)



    def write(self, path, data, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            return os.write(fh, data)


if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)

    vl = Virtual_Library()

    fuse = FUSE(vl, argv[1], foreground=True)

