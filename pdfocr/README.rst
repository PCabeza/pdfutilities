===========
 pdfocr.py
===========

:author: Pablo Cabeza
:version: 1.0


pdfocr.py is an script that mixes some other utilities to process a pdf
consisting of images through ocr software (optical character recognition) to make the pdf searchable.

I tried to use `pdfocr <https://github.com/gkovacs/pdfocr>`_ ruby script, but the resulting pdf greatly exceeded the original pdf size in most cases, so I created my own version of it.


Dependencies
------------

In my computer it works with these libraries, but it could work with other versions too:

- ghostscript (>= 8.71.dfsg.1-0ubuntu5)

- exactimage (>= 0.7.4-3ubuntu2)

- pdftk (>= 1.41+dfsg-7)

- python (>= 2.7, < 3.0)

- tesseract (>= 3.02.01-2)
	

The script is based on python 2.7 and spawns differents processes to advance in the pdf ocr.



Future features and TODO list
-----------------------------

- **TODO:** error handling overall
- **TODO:** ~~ parameter parsing
- **TODO:** better document code
- **TODO:** ~~ temporary working directory
- **TODO:** clean up
- **TODO:** eliminate the use of pdftk in metadata
- **TODO:** some kind of control code to restart previous work
