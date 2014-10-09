import urllib3
import re
import mathDownloadGui

print("Example URL: http://cmes.uccs.edu/Fall2012/Math135/archive.php\n")

urlpath = input("Please input the URL: ")
videourl = urlpath.replace("archive.php","Videos/")
notesurl = urlpath.replace("archive.php","Notes/")

http = urllib3.PoolManager()
r1 = http.request('GET', videourl)
r2 = http.request('GET', notesurl)

m1=re.findall('\"[Mm]ath.*\.mov\"',r1.data.decode("utf-8")) #Get video list
vidlist=[x.replace('\"','') for x in m1]
filelist=[x.replace('.mov','') for x in vidlist]

print("Going to download the following files: \n")
print(filelist)

m2=re.findall('href=\".*\.pdf\"',r2.data.decode("utf-8")) #Get video list
notelisttemp=[x.replace('href=','') for x in m2]
notelist=[x.replace('\"','') for x in notelisttemp]

for i in range(len(filelist)):
	print("Starting to download " + filelist[i])
	remotevidfile = http.request('GET',videourl + vidlist[i])
	remotenotefile = http.request('GET',notesurl + notelist[i])
	print("Finished downloading " + filelist[i])
	localvidfile = open(vidlist[i],'wb')
	localnotefile = open(filelist[i]+".pdf",'wb')
	localvidfile.write(remotevidfile.data)
	localnotefile.write(remotenotefile.data)
	localvidfile.close()
	localnotefile.close()
