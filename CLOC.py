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

#Commented out because doesn't work on Windows.
#subprocess.call(["cloc","./", "--by-file-by-lang", \
# "--exclude-ext=xml", "--exclude-dir=gui,reference,output", \
# "--xml", "--out=cloc.xml"])

#Get the parser, set it up to parse cloc.xml
try:
    DOMTree = xml.dom.minidom.parse('cloc.xml')
except:
    print("ERROR: Could not interact with file.  Was it created?  ")
    print("Script exiting.")
    sys.exit()


#Get the elements named 'language' and save the first one as root.
#We do this since CLOC's XML output has a node that wraps a single
#node containing all the languages, so there's no reason to look at that
#original root
root = DOMTree.documentElement.getElementsByTagName('languages')[0]

output = ""
for node in root.childNodes:
    #Nodes have like, 11 types, in Python, and this is a special one that's
    #Called text.  I'm not sure what the TEXT_NODE is but every single
    #Other node in the xml file has a TEXT_NODE.  So we ignore the TEXT_NODEs.
    if node.nodeType == node.TEXT_NODE:
        continue;
    if node.hasAttribute("name") and "Java" in node.getAttribute("name"):
        if node.hasAttribute("files_count") and \
            not node.getAttribute("files_count") == "":
            #print("Files  : " + node.getAttribute("files_count"))
            output += node.getAttribute("files_count") + " "
        else:
            print("ERROR: No file count attribute")
            print("Script exiting.")
            sys.exit()

        if node.hasAttribute("blank") and \
            not node.getAttribute("blank") == "":
            #print("Blank  : " + node.getAttribute("blank"))
            output += node.getAttribute("blank") + " "
        else:
            print("ERROR: No blank line attribute")
            print("Script exiting.")
            sys.exit()

        if node.hasAttribute("comment") and \
            not node.getAttribute("comment") == "":
            #print("Comment: " + node.getAttribute("comment"))
            output += node.getAttribute("comment") + " "
        else:
            print("ERROR: No comment line attribute")
            print("Script exiting.")
            sys.exit()

        if node.hasAttribute("code") and not node.getAttribute("code") == "":
            #print("Code   : " + node.getAttribute("code"))
            output += node.getAttribute("code")
        else:
            print("ERROR: No lines of code attribute")
            print("Script exiting.")
            sys.exit()

print(output)
outFile = open("cloc.stat", "w")
outFile.write(output)
outFile.close()
