import threading
from urllib import urlopen

class WorkerThread(threading.Thread):
  def __init__(self,url_list,url_list_lock):
    super(WorkerThread,self).__init__()
    self.url_list=url_list
    self.url_list_lock=url_list_lock
    
  def run(self):
    while (1):
      nexturl = self.grab_next_url()
      if nexturl==None:break
      self.retrieve_url(nexturl)
        
  def grab_next_url(self):
    self.url_list_lock.acquire(1)
    if len(self.url_list)<1:
      nexturl=None
    else:
      nexturl = self.url_list[0]
      del self.url_list[0]
    self.url_list_lock.release()
    return nexturl  
        
        
  def retrieve_url(self,nexturl):
    text = urlopen(nexturl).read()
    print (text)
    print ('################### %s #######################' % nexturl)
    
url_list=['http://linux.org.ru','http://kernel.org','http://python.org']
url_list_lock = threading.Lock()
workerthreadlist=[]
for x in range(0,3):
  newthread = WorkerThread(url_list,url_list_lock)
  workerthreadlist.append(newthread)
  newthread.start()
for x in range(0,3):
  workerthreadlist[x].join()