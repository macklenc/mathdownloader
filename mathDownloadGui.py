#!/usr/bin/python

import tkinter
import urllib3
import re
import tkinter.filedialog
import getpass
from os.path import expanduser
from urllib.request import urlopen
from urllib.request import Request



class simpleapp_tk(tkinter.Tk):
  def __init__(self, parent):
    tkinter.Tk.__init__(self, parent)
    self.parent = parent
    self.initialize()

  def initialize(self):
    self.grid()

    self.entryText = tkinter.StringVar()
    self.entry = tkinter.Entry(self, textvariable=self.entryText)
    self.entry.grid(column=1, row=0, sticky='EW', columnspan=99)
    self.entry.bind("<Return>", self.OnPressEnter)
    self.entry.bind("<Key>", self.update())
    self.entryText.set(u"")

    self.downloadButton = tkinter.Button(self, anchor="center", text=u"Download", command=self.OnButtonClick)
    self.downloadButton.grid(column=1, row=1)

    self.file = home = expanduser("~")
    print(self.file)
    self.dirButton = tkinter.Button(self, anchor="e", text=u"Save Location", command=self.getFile)
    self.dirButton.grid(column=2, row=1)

    self.listDialogButton = tkinter.Button(self, anchor="center", text=u"List Downloads", command=self.listClasses)
    self.listDialogButton.grid(column=3, row=1)

    self.exitButton = tkinter.Button(self, anchor="center", text=u"Exit", command=self.quit)
    self.exitButton.grid(column=99, row=99)

    self.labelFeedBackName = tkinter.StringVar()
    label = tkinter.Label(self,anchor="w",fg="black", textvariable=self.labelFeedBackName)
    label.grid(column=0, row=2, sticky='E')
    self.labelFeedBackName.set("Status: ")

    self.labelFeedBack = tkinter.StringVar()
    label = tkinter.Label(self,anchor="w",fg="black", textvariable=self.labelFeedBack)
    label.grid(column=1, row=2, columnspan=99, sticky='EW')
    self.labelFeedBack.set("doing nothing right now.")

    self.labelAddress = tkinter.StringVar()
    label = tkinter.Label(self,anchor="w",fg="black", textvariable=self.labelAddress)
    label.grid(column=0, row=0, sticky='W')
    self.labelAddress.set("Address:")

    self.grid_columnconfigure(1, weight=2)
    self.grid_rowconfigure(1, weight=3)
    self.resizable(True, True)
    self.update()
    # self.geometry(self.geometry())
    self.entry.focus_set()
    self.entry.selection_range(0, tkinter.END)


  def getFile(self):
    self.file = tkinter.filedialog.askdirectory()
    print("will now save to: \"" + self.file +"\"")
    self.labelFeedBack.set("will now save to: \"" + self.file +"\"")


  def listClasses(self):
    self.listDialog = listDialogClass(None)
    self.listDialog.title('Math Downloader List')
    self.listDialog.mainloop()


  def OnPressEnter(self, event):
    self.OnButtonClick()


  def OnButtonClick(self):
    self.downloadButton.config(state='disabled')
    self.entry.config(state='disabled')
    courses.DownloadMath(self.entryText.get(), self.file)
    self.downloadButton.config(state='normal')
    self.entry.config(state='normal')
    self.entry.focus_set()
    self.entry.selection_range(0, tkinter.END)


  def quit(self):
    print("die, jedi die.")
    self.destroy()

# end class simpleapp_tk



class listDialogClass(tkinter.Tk):
  def __init__(self, parent):
    tkinter.Tk.__init__(self, parent)
    self.parent = parent
    self.initialize()


  def initialize(self):
    self.grid()

    self.listing = tkinter.Listbox(self)
    self.listing.grid(column=2, row=2)

    for item in ["one", "two", "three", "four"]:
      self.listing.insert(tkinter.END, item)

    self.exitButton = tkinter.Button(self, anchor="center", text=u"Exit", command=self.quit)
    self.exitButton.grid(column=99, row=99)



  def quit(self):
    print("die, jedi die.")
    self.destroy()

# end class listdialog

class courses():
	def __init__(self):
		self.urlpath="http://www.uccs.edu/math/student-resources/video-course-archive.html"
		self.http = urllib3.PoolManager()
		self.itemlist=list()

	def UpdateCourseList():
		knowncoursenames=[]
		r1=http.request('GET', urlpath) # generic data

		genericcourse=re.findall('http://cmes.uccs.edu/.*/archive.php.*[<br />]?</span></li>',r1.data.decode("utf-8")) # Yuck
		names=[re.findall('>(?:\*| |&nbsp;|) ?-(?:&nbsp;| |)[a-zA-Z. ]*(?:&nbsp;| |)<',x)[0] for x in genericcourse] # Extract list of professor names
		names=[re.sub('(?:>|<|-|\*|&nbsp;)',r"",x) for x in names] # Remove special characters
		names=[re.sub('(?:^ *| *$)',r"",x) for x in names] # Finally, we have the proffs names

		# coursurls=re.findall('http://cmes.uccs.edu/.*/archive.php^((?!\"></a>).)',r1.data.decode("utf-8")) # Used to parse course info
		strip=[x.replace('http://cmes.uccs.edu/','') for x in genericcourse]	# Strip off primary URL
		strip=[re.sub('/archive\.php.*', '', x) for x in strip] 	# Strip file
		timetmp=[re.sub('/.*$',r"", x) for x in strip] # Remove the last / and everything after it
		time=[re.sub('([a-zA-Z])([0-9])',r"\1 \2",x) for x in timetmp]	# Put a space between words and numbers (Semester and year)
		coursetmp=[re.sub('^.*/',r"",x) for x in strip]	# Remove everythin up to and including the first /
		course=[re.sub('([a-zA-Z])([0-9])',r"\1 \2",x) for x in coursetmp]	# Put space between words and numbers (Math and course)

		# Test code
		# print(str(time[x]) + " " + str(course[x]) + " " + str(names[x])) for x in range(len(course))

		item=[(time[x] + " " + course[x]) for x in range(len(coursetmp))]
		courselist=list()
		[courselist.append(list(x.split())) for x in item]
		[courselist[x].append(names[x]) for x in range(len(names))]
		itemlist=list()
		[itemlist.append([x[0],int(float(x[1])),x[2],int(float(x[3])),x[4]]) for x in courselist]

		itemlist=sorted(itemlist, key=lambda itemlist: itemlist[0], reverse=True)
		itemlist=sorted(itemlist, key=lambda itemlist: itemlist[1])
		itemlist=sorted(itemlist, key=lambda itemlist: itemlist[3])

	def DownloadMath(address, fileName):
		app.labelFeedBack.set(address)
		app.update()
		print(fileName)
		print(address)
		videourl = address.replace("archive.php","Videos/")
		notesurl = address.replace("archive.php","Notes/")

		http = urllib3.PoolManager()
		r1 = http.request('GET', videourl)
		r2 = http.request('GET', notesurl)

		m1=re.findall('\"[Mm]ath.*\.mov\"',r1.data.decode("utf-8")) #Get video list
		vidlist=[x.replace('\"','') for x in m1]
		filelist=[x.replace('.mov','') for x in vidlist]

		m2=re.findall('href=\".*\.pdf\"',r2.data.decode("utf-8")) #Get video list
		notelisttemp=[x.replace('href=','') for x in m2]
		notelist=[x.replace('\"','') for x in notelisttemp]

		app.labelFeedBack.set("Beginning download")
		print("Beginning download")
		for i in range(len(filelist)):
		    app.labelFeedBack.set("Starting to download " + filelist[i])
		    app.update()
		    print("Starting to download " + filelist[i])
		    remotevidfile = http.request('GET',videourl + vidlist[i])
		    remotenotefile = http.request('GET',notesurl + notelist[i])
		    app.labelFeedBack.set("Finished downloading " + filelist[i])
		    app.update()
		    print("Finished downloading " + filelist[i])
		    localvidfile = open(vidlist[i],'wb')
		    localnotefile = open(filelist[i]+".pdf",'wb')
		    localvidfile.write(remotevidfile.data)
		    localnotefile.write(remotenotefile.data)
		    localvidfile.close()
		    localnotefile.close()
		# end getMath()

class FileDownloader(object):
	def progress(total, existing, upload_t, upload_d):
		existing = existing + os.path.getsize(filename)
		try:
			frac = float(existing)/float(total)
		except:
			frac = 0
		sys.stdout.write("\r%s %3i%%" % ("File downloaded - ", frac*50))

	def test(self, debug_type, debug_msg):
		print ("debug(%d): %s" % (debug_type, debug_msg))

	def download(self, url, deleteFile=False):
		filename = url.split("/")[-1].strip()

		if deleteFile is True:
			print('Deleting file')
			os.remove(self.fileName)

		c = pycurl.Curl()
		c.setopt(pycurl.URL, url)
		c.setopt(pycurl.FOLLOWLOCATION, 1)
		c.setopt(pycurl.MAXREDIRS, 5)

		# Setup writing
		if os.path.exists(filename):
		    f = open(filename, "ab")
		    c.setopt(pycurl.RESUME_FROM, os.path.getsize(filename))
		else:
		    f = open(filename, "wb")

		c.setopt(pycurl.WRITEDATA, f)

		#c.setopt(pycurl.VERBOSE, 1) 
		c.setopt(pycurl.DEBUGFUNCTION, test)
		c.setopt(pycurl.NOPROGRESS, 0)
		c.setopt(pycurl.PROGRESSFUNCTION, progress)
		try:
		    c.perform()
		except:
		    pass

if __name__ == "__main__":
  app = simpleapp_tk(None)
  app.title('Math Downloader')
  app.mainloop()
