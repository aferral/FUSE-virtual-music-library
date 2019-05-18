#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging

from errno import EACCES
from os.path import realpath
from sys import argv, exit
from threading import Lock

import os

from fuse import FUSE, FuseOSError, Operations

#


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

class Loopback(LoggingMixIn, Operations):
    def __init__(self, root):
        self.root = realpath(root)
        print("Path base {0}".format(self.root))
        self.rwlock = Lock()


    chmod = os.chmod
    chown = os.chown
    mkdir = os.mkdir
    mknod = os.mknod
    open = os.open
    listxattr = None
    getxattr = None
    readlink = os.readlink
    rmdir = os.rmdir
    unlink = os.unlink
    utimens = os.utime


    def __call__(self, op, path, *args):
        return super(Loopback, self).__call__(op, self.root + path, *args)
        
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

    # def __call__(self, op, path, *args):
    #     return super(Loopback, self).__call__(op, self.root + path, *args)
    
    def access(self, path, mode):
        if not os.access(path, mode):
            raise FuseOSError(EACCES)

    def create(self, path, mode):
        return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)

    def flush(self, path, fh):
        return os.fsync(fh)

    def fsync(self, path, datasync, fh):
        if datasync != 0:
          return os.fdatasync(fh)
        else:
          return os.fsync(fh)

    def getattr(self, path, fh=None):
        st = os.lstat(path)
        res = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

        print('GETATTR {0} {1}'.format(path,res))
        return res



    def link(self, target, source):
        return os.link(source, target)




    def read(self, path, size, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            return os.read(fh, size)

    def readdir(self, path, fh):
        return ['.', '..'] + os.listdir(path)



    def release(self, path, fh):
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
    if len(argv) != 3:
        print('usage: %s <root> <mountpoint>' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)

    fuse = FUSE(Loopback(argv[1]), argv[2], foreground=True)

