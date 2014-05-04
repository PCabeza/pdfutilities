pdfocr.py is an script that mixes some other utilities to process a pdf
consisting of images through ocr software (optical character recognisition) to make the pdf searchable.

It depends on:
	ghostscript (>= 8.71.dfsg.1-0ubuntu5)
 	exactimage (>= 0.7.4-3ubuntu2)
	pdftk (>= 1.41+dfsg-7)
	python
	tesseract

The script is based on python 2.7 and spawns differents processes to advance in the pdf ocr.
