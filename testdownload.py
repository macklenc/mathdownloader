from urllib.request import urlopen
from urllib.request import Request
import os
import threading
import time

import pdb

debugStatus = True

class FileDownloader(object):
    def __init__(self):
        self.url = None
        self.progress = None
        self.status = None # {0:"Downloading", 1:"Completed", 2:"Paused", 3:"Error"}
        self.fileName = None
        self.u = None
        self.fileSize = None
        self.szDownloaded = 0
        self.isPaused = threading.Event()
        self.lock = threading.Lock()

    def raw2human(self, value):
        if (value/1000000000) > 1: # Define in GB
            return str("%.2f GB"%(value/1000000000.0))
        if (value/1000000) > 1: # Define in MB
            return str("%.2f MB"%(value/1000000.0))
        if (value/1000) > 1: # Define in KB
            return str("%.2f KB"%(value/1000.0))

    def startDownload(self, url, deleteFile=False, start=None):
        if debugStatus:
            print("Intent to delete file: %r" % deleteFile)
            if start is not None:
                print("Starting download from: %s" % self.raw2human(start))
            else:
                print("Starting download from: 0 Bytes")
        with self.lock:
            self.isPaused.clear()

        if debugStatus:
            print("Starting download thread...")
        download_thread = threading.Thread(target=self.download, args=(url,deleteFile,start))
        download_thread.start()

    def download(self, url, deleteFile=False, start=None):
        if debugStatus:
            print("Download thread started.")
        self.url = url
        self.fileName = url.split("/")[-1]

        if start is not None:
            req = Request(url)
            req.headers["Range"] = "bytes=%s-%s" %(start, self.fileSize)
            self.u = urlopen(req)
        else:
            self.u = urlopen(url)

        if deleteFile is True and os.path.isfile(self.fileName):
            try:
                print('Deleting file')
                os.remove(self.fileName)
            except:
                pass

        f = open(self.fileName, "ab")
        if self.u.getheader("Content-Length") is not None:
            print('Got Content-Length, downloading')
            self.fileSize = int(self.u.getheader("Content-Length"))
        else:
            print('Cannot get Content-Length, blind downloading')

        self.szDownloaded = 0
        if start is not None:
            self.szDownloaded = start
        block_sz = 8192
        while True:
            buffer = self.u.read(block_sz)
            if not buffer:
                self.status = 1
                break
            self.szDownloaded += len(buffer)
            f.write(buffer)
            self.status = 0
            stringLength = len(self.raw2human(self.szDownloaded))
            clearString = " "
            for x in range(stringLength+4):
                clearString+=" "
            print(clearString,end='\r')
            print(self.raw2human(self.szDownloaded),end='\r')

            with self.lock:
                if self.isPaused.isSet() is True:
                    print('pause self.lock')
                    break
        print('')
        f.close()
        return

    def pauseDownload(self):
        with self.lock:
            self.isPaused.set()
        #save a file with the download status, then I'll be able to resume it

    def resumeDownload(self):
        with self.lock:
            self.isPaused.clear()
        self.startDownload(self.url, False, self.szDownloaded)

f = FileDownloader()

f.startDownload("https://github.com/aron-bordin/Tyrant-Sql/archive/master.zip", True)


time.sleep (5);

print('pausing download')
f.pauseDownload()

time.sleep (5);

print('resuming download')
f.resumeDownload()

print("ok")