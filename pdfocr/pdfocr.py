#! /usr/bin/python -O
'''
todo list:
    TODO: error handling overall
    TODO: parameter parsing
    TODO: better document code
    TODO: temporary working directory
    TODO: clean up
    TODO: eliminate the use of pdftk in metadata
'''
import os,re,sys
from subprocess import Popen as _, PIPE
from threading import Thread,Lock
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile

## Default configuration ##
RESOLUTION=200
THREADS=4
OUTPUT="output.pdf"
INPUT="input.pdf"

def create_tiffs(pdf):
    args=["gs","-dNOPAUSE","-sDEVICE=tiffg4","-dFirstPage=1","-sOutputFile=image%d.tiff",
     "-r%d"%RESOLUTION,"-q",pdf,"-c","quit"]
    p=_(args); p.communicate()


def call_tesseract(file):
    args=["tesseract",file,file,"hocr"]
    p=_(args); p.communicate()


##
# @file: tiff file to process
def call_hocr(pdffile,imagefile,hocrfile):
    args=["hocr2pdf","-i",imagefile,"-o",pdffile]
    p=_(args,stdin=PIPE)
    with open(hocrfile,"r") as hocr:
        p.communicate(input=hocr.read())


def merge_pdfs(pdflist,output):
    args=["gs","-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite","-sOutputFile="+output]+pdflist
    p=_(args); p.communicate()

    
def list_files():
    dir=os.listdir(".")
    html=filter(lambda x: x.endswith(".html"),dir)
    tiff2hocr=[v for v in dir if v.endswith(".tiff") and not (v+".html" in html)]
    pdfs=filter(lambda x: x.endswith(".pdf"),dir)
    tiff2pdf=[v for v in dir if v.endswith(".tiff") and not (v+".pdf" in pdfs)]

    pdfs=sorted([v for v in pdfs if re.match("image\d+\.tiff\.pdf",v)],
      key=lambda x: int(re.match("image(\d+)\.tiff\.pdf",x).group(1)))

    return (tiff2hocr,pdfs,tiff2pdf)

def merge_metadata(src,dst):
    tmp=NamedTemporaryFile(dir=".",delete=False)
    srcm=_(["pdftk",src,"dump_data"],stdout=PIPE)
    dstm=_(["pdftk",dst,"update_info","-","output",tmp.name],stdin=srcm.stdout)
    srcm.stdout.close() # for pipe to work correctly (SIGPIPE) 
    dstm.communicate()
    
    # move temporary file to the actual file
    os.rename(tmp.name, dst)
    

class worker(Thread):
    '''
    General worker class to be used in various concurrent functions.
    The way it works is by iterating a list and passing the callback
    method each element using the lock for syncronizing.
    '''
    
    def __init__(self,queue,lock,callback):
        super(worker,self).__init__()
        self.queue = queue
        self.lock = lock
        self.callback=callback

    def run(self):
        actual=True
        while actual:
            self.lock.acquire()
            actual=self.queue.pop(0) if self.queue else None
            self.lock.release()
            if actual: self.callback(actual)
    
    
class DummyLock():
    def acquire(self): pass
    def release(self): pass
    def __exit__(self,*args,**kwargs): pass
    def __enter__(self,*args,**kwargs): pass



    
if __name__=="__main__":
    if len(sys.argv)>1: INPUT=sys.argv[1]
    
    ## Start by getting the current process state, ## 
    ## in case of continuing previous work         ##
    tiff2hocr,pdfs,tiff2pdf=list_files()
    
    ## if no tiff image, produce them from the pdf ##
    if not tiff2hocr and not pdfs and not tiff2pdf:
        create_tiffs(INPUT)
        tiff2hocr,pdfs,tiff2pdf=list_files()
    
    
    
    ## produce the hocr files from the tiff images ##
    
    # if THREADS==1 then use a "dummy" lock
    # clousure array to pass variables to callback function 
    l=[0,Lock() if THREADS-1 else DummyLock()]
    lock=Lock() if THREADS-1 else DummyLock()
    def callback(x): # method that threads will execute
        with l[1]: local=l[0]
        print "still %d to end..."%local
        call_tesseract(x)
        with l[1]: l[0]+=-1
    
    th=[worker(tiff2hocr,lock,callback ) for v in range(0,THREADS)]
    while tiff2hocr:
        l[0]=len(tiff2hocr)
        if THREADS==1: th[0].run()
        else: 
            for t in th: t.start()
            for t in th: t.join()
        tiff2hocr,pdfs,tiff2pdf=list_files()
        


    ## use hocr data to generate pdf from each page tiff ##
    if tiff2pdf:
        lock=Lock() if THREADS-1 else DummyLock()        
        th=[worker(tiff2pdf,lock,lambda f: call_hocr(f+".pdf", f, f+".html")) for v in range(0,THREADS)]
        while tiff2pdf:
            if THREADS==1: th[0].run()
            else: 
                for t in th: t.start()
                for t in th: t.join()
            tiff2hocr,pdfs,tiff2pdf=list_files()
    
    
    
    ## merge all generated pdfs into a single pdf file ##
    if not tiff2pdf and not tiff2hocr and pdfs and not os.path.exists(OUTPUT):
        merge_pdfs(pdfs, OUTPUT)
        merge_metadata(INPUT, OUTPUT)
    
