This project aims to build an utility for managing pdf metadata,
labeling and bookmarks through an xml interface. The main reason for
it is to have an easy way to handle metadata for my ebook.

Current features:

* add metadata information to pdf
* add bookmarks to pdf
* set page labeling of pdf


Future features:

* Export information from pdf to xml format
* make an installer
* make documentation


Note: Currently it uses ghostscript with pdfwrite device, setting
PDFSETTING to /prepress. This means that pdf might get compressed if
they have high quality images to 300 dpi (the default behavior with
/prepress).


* [xml format](doc/xml-format.rnc) in relax NG compact syntax
* [development information](doc/Developer.md)
