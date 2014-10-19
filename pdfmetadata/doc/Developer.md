The structure is as follows:

* metadata internal data structure

* XML-metadata module that transforms from xml to internal metadata
  data structure and viceversa
  
* metadata-gs module that gets the actual ghostscript commands to
  process the pdf

* gs module to feed ghostscript with commands from the previous module


- TODO maybe create a c++ wrapper for the actual xml-metadata in python
