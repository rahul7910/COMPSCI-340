#!/usr/bin/env python

from __future__ import print_function, absolute_import, division

import logging
from collections import defaultdict
import os
import sys
import errno
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREGa
from sys import argv, exit
from time import time


from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from passthrough import Passthrough
#Note if not in then do pass through else do memory 
#Rahul Issar 
#riss899 
#588382864 

if not hasattr(__builtins__, 'bytes'):
	bytes = str

class A2Fuse2(LoggingMixIn, Passthrough):
	def __init__(self, root):
		self.root = root  
		self.files = {}
        	self.data = defaultdict(bytes)
        	self.fd = 0
        	now = time()
        	self.files['/'] = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
	
	def getattr(self, path, fh=None):
        	if path not in self.files:
			full_path = self._full_path(path)
        		st = os.lstat(full_path)
        		return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
            	else:
			
	        	return self.files[path]

#passthrough 
#def getattr(self, path, fh=None):
 #       full_path = self._full_path(path)
  #      st = os.lstat(full_path)
   #     return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
    #                 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))



#memory
#def getattr(self, path, fh=None):
 #       if path not in self.files:
  #          raise FuseOSError(ENOENT)

   #     return self.files[path]




	def readdir(self, path, fh):
		full_path = self._full_path(path)
		dirents = ['.', '..']
		for files in self.files: 
			if files != '/':
				dirents += [files[1:]]
        	if os.path.isdir(full_path):
            		dirents.extend(os.listdir(full_path))
        	for r in dirents:
           		yield r
		#for x in self.files: 
		#	if x != ['/']:
		#		yield x[1:]


	def open(self, path, flags):
		if path not in self.files: 
			full_path = self._full_path(path)
			return os.open(full_path, flags) 
		else:
			self.fd += 1
			return self.fd
	

	
    	def create(self, path, mode, fi=None):
		self.files[path] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time(), st_uid = os.getuid(), st_gid = os.getgid())
		self.fd += 1
        	return self.fd
			


	def unlink(self, path):
		if path not in self.files: 
			return os.unlink(self._full_path(path))
		else: 
			self.files.pop(path) 

	#def write(self, path, buf, offset, fh):
        #os.lseek(fh, offset, os.SEEK_SET)
        #return os.write(fh, buf)

	def write(self, path, data, offset, fh = None):
		if path not in self.files: 
			os.lseek(fh, offset, os.SEEK_SET) 
			return os.write(fh,data) 
		else: 
        		self.data[path] = self.data[path][:offset] + data
        		self.files[path]['st_size'] = len(self.data[path])
        		return len(data)

	def flush(self, path, fh):
		if path not in self.files: 
	        	return os.fsync(fh)

	def read(self, path, length, offset, fh = None):
		if path not in self.files: 
			os.lseek(fh, offset, os.SEEK_SET) 
			return os.read(fh,length) 
		else: 
			return self.data[path][offset:offset + size]


def main(mountpoint, root):
    FUSE(A2Fuse2(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[2], sys.argv[1])	
