# Parsing XML files with Python's Built-in DOM
# Document Object Model.  It's a lot easier than Element Tree.
# Documentation at: https://docs.python.org/3.6/library/xml.dom.minidom.html

#Uses Python 3.6

#Import the actual DOM Processors/parsers
from xml.dom.minidom import parse
import xml.dom.minidom

#Get the parser, set it up to parse Style_Errors.xml
DOMTree = xml.dom.minidom.parse('Style_Errors.xml')

#root is the first <> element in the XML file.
root = DOMTree.documentElement

#Grabbing basic information from the xml file - an element from the root.
if root.hasAttribute("version"):
    print("Checkstyle Version : %s" % root.getAttribute("version"))

#Get the elements named 'file' and save the first one as root.
#We do this since checkstyle XML output has a <> element that wraps a single
#<> element containing all the errors, so there's no reason to look at that
#original root beyond making sure the version is correct.
root = root.getElementsByTagName('file')[0]

#Of course, checking that this worked
if root.hasAttribute("name"):
    #This gets the name of the file checked, and since it's got the full path
    #of it too, we have to split and then take the last element from the split
    #Which would be the file name.
    string = root.getAttribute("name").split('/')[-1]
    print("File Checked       : %s" % string)

#A basic for loop, to look at all the nodes (<> elements) inside the file node
#(which is now the root node) and print out their information.
#.childNodes is a list of nodes that the root has as children.  I hate E 115. (lol rz)
for node in root.childNodes:
    #Nodes have like, 11 types, in Python, and this is a special one that's
    #Called text.  I'm not sure what the TEXT_NODE is but every single
    #Other node in the xml file has a TEXT_NODE.  So we ignore the TEXT_NODEs.
    if node.nodeType != node.TEXT_NODE:
        #Ignore messages about tabs - we should probably log these in the future
        #But for now, they're just clogging it up.  Shows how easy it is
        #to ignore certain errors.
        if node.hasAttribute("message") and "tab" not in node.getAttribute("message"):
            if node.hasAttribute("line"):
                line = node.getAttribute("line")
                if node.hasAttribute("column"):
                    line += ":" + node.getAttribute("column")
                print(line)
            if node.hasAttribute("severity"):
                print(node.getAttribute("severity"))
            if node.hasAttribute("source"):
                string = node.getAttribute("source").split('.')[-1]
                print(string)
            if node.hasAttribute("message"):
                print(node.getAttribute("message"))
            print()
