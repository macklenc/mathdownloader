#!/usr/bin/python

import tkinter
import urllib3
import re


class simpleapp_tk(tkinter.Tk):
  def __init__(self, parent):
    tkinter.Tk.__init__(self, parent)
    self.parent = parent
    self.initialize()

  def initialize(self):
    self.grid()

    self.entryText = tkinter.StringVar()
    self.entry = tkinter.Entry(self, textvariable=self.entryText)
    self.entry.grid(column=1, row=0, sticky='EW', columnspan=2)
    self.entry.bind("<Return>", self.OnPressEnter)
    self.entry.bind("<Key>", self.update())
    self.entryText.set(u"")

    self.button = tkinter.Button(self, anchor="center", text=u"Download", command=self.OnButtonClick)
    self.button.grid(column=1, row=1)

    self.labelFeedBackName = tkinter.StringVar()
    label = tkinter.Label(self,anchor="w",fg="black", textvariable=self.labelFeedBackName)
    label.grid(column=0, row=2, sticky='E')
    self.labelFeedBackName.set("Status: ")

    self.labelFeedBack = tkinter.StringVar()
    label = tkinter.Label(self,anchor="w",fg="black", textvariable=self.labelFeedBack)
    label.grid(column=1, row=2, columnspan=3, sticky='EW')
    self.labelFeedBack.set("doing nothing right now.")

    self.labelAddress = tkinter.StringVar()
    label = tkinter.Label(self,anchor="w",fg="black", textvariable=self.labelAddress)
    label.grid(column=0, row=0, sticky='W')
    self.labelAddress.set("Address:")

    self.grid_columnconfigure(1, weight=2)
    self.grid_rowconfigure(1, weight=3)
    self.resizable(False, True)
    self.update()
    # self.geometry(self.geometry())
    self.entry.focus_set()
    self.entry.selection_range(0, tkinter.END)


  def OnPressEnter(self, event):
    self.OnButtonClick()


  def OnButtonClick(self):
    self.button.config(state='disabled')
    self.entry.config(state='disabled')
    getMath(self.entryText.get())
    self.button.config(state='normal')
    self.entry.config(state='normal')
    self.entry.focus_set()
    self.entry.selection_range(0, tkinter.END)

def getMath(address):
  app.labelFeedBack.set(address)
  app.update()
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

if __name__ == "__main__":
  app = simpleapp_tk(None)
  app.title('mathDownload')
  app.mainloop()
