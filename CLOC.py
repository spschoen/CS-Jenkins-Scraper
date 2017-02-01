# Parsing CLOC with Python's Built-in DOM
# Document Object Model.  It's a lot easier than Element Tree.
# Documentation at: https://docs.python.org/3.6/library/xml.dom.minidom.html

#Uses Python 3.6

#Import the actual DOM Processors/parsers
from xml.dom.minidom import parse
import xml.dom.minidom
import shutil
import sys
import os
import subprocess

#Verifying the CLOC is installed
#Commented out because doesn't work on Windows.
#if shutil.which("cloc") == None:
    #print("ERROR: CLOC utility is required to be installed.")
    #print("Script exiting.")
    #sys.exit()

subprocess.call(["cloc","./", "--by-file-by-lang", "--exclude-ext=xml", "--exclude-dir=gui,reference,output", "--xml", "--out=cloc.xml"])

#Get the parser, set it up to parse cloc.xml
try:
    DOMTree = xml.dom.minidom.parse('cloc.xml')
except:
    print("ERROR: Could not interact with file.  Was it created?  ")
    print("Script exiting.")
    sys.exit()

#root is the first node in the XML file.
root = DOMTree.documentElement

#Get the elements named 'language' and save the first one as root.
#We do this since checkstyle XML output has a node that wraps a single
#node containing all the errors, so there's no reason to look at that
#original root beyond making sure the version is correct.
root = root.getElementsByTagName('languages')[0]

#A basic for loop, to look at all the nodes (nodes) inside the file node
#(which is now the root node) and print out their information.
#.childNodes is a list of nodes that the root has as children.  I hate E 115.
for node in root.childNodes:
    #Nodes have like, 11 types, in Python, and this is a special one that's
    #Called text.  I'm not sure what the TEXT_NODE is but every single
    #Other node in the xml file has a TEXT_NODE.  So we ignore the TEXT_NODEs.
    if node.nodeType == node.TEXT_NODE:
        continue;
    if node.hasAttribute("name") and "Java" in node.getAttribute("name"):
        if node.hasAttribute("files_count"):
            print("Files  : " + node.getAttribute("files_count"))
        if node.hasAttribute("blank"):
            print("Blank  : " + node.getAttribute("blank"))
        if node.hasAttribute("comment"):
            print("Comment: " + node.getAttribute("comment"))
        if node.hasAttribute("code"):
            print("Code   : " + node.getAttribute("code"))
