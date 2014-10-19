from urllib.request import urlopen
from urllib.request import Request
import os
import threading
import time

import pdb

debugStatus = True

class ResumeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# Interface:
# startDownload(url,deleteFile) -> url is self explanitory, set deleteFile to true to delete any existing
# files with equivalent names, since the downloader appends to the file, you always want to do this on a 
# fresh start.
# PauseDownload()
# resumeDownload()
# getFilename()
# raw2human(value) -> This will take a download value and make it easily readible, i.e. KB, MB, GB.
# getProgress() -> This has lots of data, returned in order: current amount downloaded, total required, percentage complete
# approxamate download rate and estimated completion time. -- not implimented

# Note: To recover a download after a possible app crash, run loadStatus() followed by resumeDownload().

class FileDownloader(object):
    def __init__(self):
        self.url = None # URL to file
        self.progress = None # %complete
        self.status = None # {0:"Downloading", 1:"Completed", 2:"Paused", 3:"Error"}
        self.fileName = None
        self.u = None
        self.fileSize = None
        self.szDownloaded = 0
        self.szDownloadedLog = 0
        self.urlLog = None
        self.block_sz = 8192
        self.isPaused = threading.Event()
        self.lock = threading.Lock()
        self.start = 0
        self.velocity = list()
        self.elapsedNumber = 0
        self.averageVelocity = 0

    def getFilename(self):
        return fileName

    def downloadRate(self):
        if self.elapsedNumber < 10:
            self.velocity.append(time.time()-self.start)
            self.elapsedNumber = self.elapsedNumber + 1
        else:
            self.velocity[self.elapsedNumber%10]=(time.time()-self.start)
        self.start = time.time()
        self.averageVelocity = sum(self.velocity)/len(self.velocity)

    # def getProgress(self):


    def raw2human(self, value):
        if (value/1000000000) > 1: # Define in GB
            return str("%.2f GB"%(value/1000000000.0))
        if (value/1000000) > 1: # Define in MB
            return str("%.2f MB"%(value/1000000.0))
        if (value/1000) > 1: # Define in KB
            return str("%.2f KB"%(value/1000.0))

    def requestFileLength(self):
        header = self.u.getheader("Content-Length")
        if header is not None:
            self.fileSize = int(header)
        else:
            i = 0
            while i < 10 and header is None:
                header = self.u.getheader("Content-Length")
                if header is not None:
                    self.fileSize = int(header)
                i = i + 1
                if debugStatus and header is not None:
                    print("Retrieved Content-Length after %d attempts." % i)
            
        if debugStatus:
            if self.fileSize is not None:
                print('Got Content-Length, downloading')
            else:
                print('Cannot get Content-Length, blind downloading')

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
            if debugStatus:
                print("Requesting download headers for custom start...")
            req = Request(url)
            req.headers["Range"] = "bytes=%s-%s" %(start, self.fileSize)
            self.u = urlopen(req)
            if debugStatus:
                print("SUCCESS.")
        else:
            if debugStatus:
                print("Requesting URL...")
            self.u = urlopen(url)
            if debugStatus:
                print("SUCCESS.")

        if deleteFile is True and os.path.isfile(self.fileName):
            try:
                print('Deleting file...')
                os.remove(self.fileName)
                print('SUCCESS.')
            except:
                pass

        f = open(self.fileName, "ab")

        self.requestFileLength()

        self.szDownloaded = 0
        if start is not None:
            self.szDownloaded = start
        
        self.start = time.time()
        while True:
            buffer = self.u.read(self.block_sz)
            if not buffer:
                self.status = 1
                break
            self.szDownloaded += len(buffer)
            f.write(buffer)
            self.status = 0

            # Print current download status
            stringLength = len(self.raw2human(self.szDownloaded))
            clearString = " "
            for x in range(stringLength+4):
                clearString+=" "
            print(clearString,end='\r')
            print('Current rate: ' + str(self.raw2human(self.averageVelocity)))
            print(self.raw2human(self.szDownloaded),end='\r')

            self.saveStatus()
            self.downloadRate()
            with self.lock:
                if self.isPaused.isSet() is True:
                    print('Exiting download thread.')
                    break
        print('')
        f.close()
        return

    def saveStatus(self):
        # if debugStatus:
        #     print('Saving download status...')
        f = open("download.status", "w")
        f.write("%s %d" % (str(self.url), int(self.szDownloaded)))
        f.close()
        # if debugStatus:
        #     print('SUCCESS.')

    def loadStatus(self):
        if debugStatus:
            print('Loading download status...')
        try:
            f = open("download.status", "r")
            status = f.read()
            statusList = status.split()
            self.urlLog = str(statusList[0])
            self.szDownloadedLog = int(statusList[1])
            f.close()
            if debugStatus:
                print('SUCCESS.')
        except:
            self.urlLog = None
            self.szDownloadedLog = None

    def pauseDownload(self):
        if debugStatus:
            print('Pausing download...')
        self.status = 2
        with self.lock:
            self.isPaused.set()
        # self.saveStatus()
        #save a file with the download status, then I'll be able to resume it

    def resumeDownload(self):
        if debugStatus:
            print('Resuming download...')
        with self.lock:
            self.isPaused.clear()
        self.loadStatus()
        if self.urlLog is not None and self.szDownloadedLog is not None:
            self.startDownload(self.urlLog, False, self.szDownloadedLog)
        else:
            self.status = 3
            raise ResumeError('Cannot resume download, no download status available.')

f = FileDownloader()

f.startDownload("https://github.com/aron-bordin/Tyrant-Sql/archive/master.zip", True)
# f.resumeDownload()



if f.status is not 3:
    time.sleep (5);
    f.pauseDownload()
    time.sleep (5);
    f.resumeDownload()