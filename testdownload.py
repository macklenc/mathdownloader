from urllib.request import urlopen
from urllib.request import Request
import os
import threading
import time

isPaused = threading.Event()
lock = threading.Lock()
    
class FileDownloader(object):
    def __init__(self):
        self.url = None
        self.progress = None
        self.status = None # {0:"Downloading", 1:"Completed", 2:"Paused", 3:"Error"}
        self.fileName = None
        self.u = None
        self.fileSize = None
        self.szDownloaded = 0

 
    def startDownload(self, url, deleteFile=False, start=None):
        with lock:
            isPaused.clear()
        download_thread = threading.Thread(target=f.download, args=(url,deleteFile,start))
        download_thread.start()

    def download(self, url, deleteFile=False, start=None):
        self.url = url
        self.fileName = url.split("/")[-1]
 
        if start is not None:
            req = Request(url)
            req.headers["Range"] = "bytes=%s-%s" %(start, self.fileSize)
            self.u = urlopen(req)
        else:
            self.u = urlopen(url)

        if deleteFile is True:
            print('Deleting file')
            os.remove(self.fileName)
 
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
            print(self.szDownloaded)
            with lock:
                if isPaused.isSet() is True:
                    print('pause lock')
                    break
 
        f.close()
        return
 
    def pauseDownload(self):
        with lock:
            isPaused.set()
        #save a file with the download status, then I'll be able to resume it
 
    def resumeDownload(self):
        with lock:
            isPaused.clear()
        self.startDownload(self.url, False, self.szDownloaded)
 
f = FileDownloader()

f.startDownload("https://github.com/aron-bordin/Tyrant-Sql/archive/master.zip", True)


time.sleep (10);
print('pausing download')
time.sleep (10);
f.pauseDownload()
print('resuming download')
time.sleep (10)
f.resumeDownload()
print("ok")