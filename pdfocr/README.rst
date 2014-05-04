pdfocr.py is an script that mixes some other utilities to process a pdf
consisting of images through ocr software (optical character recognisition) to make the pdf searchable.

It depends on:

	- ghostscript (>= 8.71.dfsg.1-0ubuntu5)

 	- exactimage (>= 0.7.4-3ubuntu2)

	- pdftk (>= 1.41+dfsg-7)

	- python

	- tesseract (>= 3.02.01-2)


The script is based on python 2.7 and spawns differents processes to advance in the pdf ocr.

List of things to do:
	- *TODO:* error handling overall
	- *TODO:* ~~ parameter parsing
	- *TODO:* better document code
	- *TODO:* ~~ temporary working directory
	- *TODO:* clean up
	- *TODO:* eliminate the use of pdftk in metadata
	- *TODO:* some kind of control code to restart previous work
