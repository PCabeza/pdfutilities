#! /usr/bin/python -O
'''

:version: 1.0
:author: Pablo Cabeza

todo list:
    TODO: error handling overall
    TODO: parameter parsing
    TODO: better document code
    TODO: temporary working directory
    TODO: clean up
    TODO: eliminate the use of pdftk in metadata
    TODO: some kind of control code to restart previous work
'''
import os,re,sys
from subprocess import Popen as _, PIPE
from threading import Thread,Lock
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile,mkdtemp,gettempdir

## Default configuration ##
RESOLUTION=200
THREADS=4
OUTPUT="output.pdf"
INPUT=None
CURDIR=os.getcwd()
TMPDIR=CURDIR
WORKDIR=None

def create_tiffs(pdf):
    '''
    Split pdf into images for each page of the pdf. The images are
    output in tiff format and named "image<page-number>.tiff".
    
    .. note:: The images are generated in the current directory.
    .. note:: ghostscript with tiffg4 device is used.
    
    :param pdf: the path to the pdf file.
    '''
    args=["gs","-dNOPAUSE","-sDEVICE=tiffg4",
          "-dNumRenderingThreads=%d"%THREADS,
          "-dFirstPage=1",
          "-sOutputFile=image%d.tiff",
          "-r%d"%RESOLUTION,"-q",
          "-c","30000000 setvmthreshold",
          "-f",pdf,"-c","quit"]
    p=_(args); p.communicate()



def call_tesseract(file):
    '''
    Calls tesseract to generate the hocr of a page. The output pdf
    file name is the image filename plus ".pdf" extension.
    
    :param file: the path to the page image
    '''
    args=["tesseract",file,file,"hocr"]
    p=_(args); p.communicate()



def call_hocr(pdffile,imagefile,hocrfile):
    '''
    calls hocr2pdf and generates a pdf from a single page pdf file.
    
    :param pdffile: the output pdf filename
    :param imagefile: the input image filename
    :param hocrfile: the input hocr filename
    '''
    
    args=["hocr2pdf","-i",imagefile,"-o",pdffile]
    p=_(args,stdin=PIPE)
    with open(hocrfile,"r") as hocr:
        p.communicate(input=hocr.read())


def merge_pdfs(pdflist,output):
    '''
    Merge the pdf files into a single one. The page order is the
    same as the order of the list. 
    
    .. note:: ghostscript with pdfwrite is used for this process.
    :param pdflist: list of pdf filenames
    :param output: the name of the output pdf
    '''
    args=["gs","-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite",
          "-dNumRenderingThreads=%d"%THREADS,
          "-sOutputFile="+output,
          "-c","30000000 setvmthreshold",
          "-f"]+pdflist
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
    '''
    Sets the metadata of dst to the metadata of src pdf files.
    
    .. note:: pdftk is used for extracting and updating the metadata.
    '''
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
    method each element using the lock for syncronizing. This way the
    processors can be used more efficiently for spawning a set number
    processes.
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
    '''
    Auxiliary class to be used for synchronizing when there is 
    just 1 thread in use, its methods does nothing.
    '''
    def acquire(self): pass
    def release(self): pass
    def __exit__(self,*args,**kwargs): pass
    def __enter__(self,*args,**kwargs): pass



####################
##  MAIN PROGRAM  ##
####################

if __name__=="__main__":
    
    ## Parse arguments ##
    parser=ArgumentParser(prog="pdfocr.py",
                          description="Script that uses some standard tools to "+
                          "generate a searchable pdf file. It depends on "+
                          "gs, pdftk and hocr2pdf utilities.")
    
    parser.add_argument("input",type=str,default=INPUT,nargs="?",
                        help="input pdf file to be processed.")
    parser.add_argument("output",type=str,default=OUTPUT,nargs="?",
                        help="output pdf filename.")
    parser.add_argument("-T","--threads",dest="nthr",type=int,default=THREADS,
                        help="Specify the number of threads to use while processing the pdf.")
    parser.add_argument("-R","--resolution",dest="res",type=int,default=RESOLUTION,
                        help="resolution for intermediate images, those images will be then "+
                        "renderered together to generate the pdf file.")
    parser.add_argument("-t","--temp",dest="temp",action="store_true",default=False,
                        help="if specified use system temporary directory.")
    args=parser.parse_args()
    
    # Set variables to parsed argument values
    INPUT=args.input
    OUTPUT=args.output
    THREADS=args.nthr
    RESOLUTION=args.res
    TMPDIR= gettempdir() if args.temp else TMPDIR
    
    # Set input and output to absolute paths
    INPUT=os.path.join(CURDIR,INPUT)
    OUTPUT=os.path.join(CURDIR,OUTPUT)
    WORKDIR=mkdtemp(dir=TMPDIR) # create working folder
    
    os.chdir(WORKDIR) # change to the working directory
    
#     os.rmdir(WORKDIR)
    
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
    
