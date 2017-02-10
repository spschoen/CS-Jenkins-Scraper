#Building custom TestFile parser since none exist. RIP @me

from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os


FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
print(FILE_DIR)
for arg in sys.argv[len(sys.argv) - 1].split("/"):
    if arg == "":
        continue
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(FILE_DIR)

try:
    DOMTree = xml.dom.minidom.parse(FILE_DIR + '/findbugs.xml')
except:
    print("ERROR: Could not interact with file", FILE_DIR + '/findbugs.xml')
    print("Script exiting.")
    sys.exit()

#root is the first <> element in the XML file.
root = DOMTree.documentElement

if root.hasAttribute("version"):
    print("FindBugs Version : %s" % root.getAttribute("version"))

for node in root.childNodes:
    if node.nodeName == "BugInstance":
        line = "Bugtype : "
        line += node.getAttribute("type") + "\n"
        if node.hasAttribute("priority"):
            line += "Priority: " + node.getAttribute("priority") + "\n"
        if node.hasAttribute("rank"):
            line += "Rank    : " + node.getAttribute("rank") + "\n"
        if node.hasAttribute("abbrev"):
            print()
            line += "Abbrev  : " + node.getAttribute("abbrev") + "\n"
        if node.hasAttribute("category"):
            line += "Category: " + node.getAttribute("category")

        print(line)
        for classNode in node.childNodes:
            if classNode.nodeName == "Method":
                if classNode.hasAttribute("classname"):
                    string = classNode.getAttribute("classname").split(".")
                    string = string[len(string) - 1]
                    print("Class   : " + string)
                if classNode.hasAttribute("name"):
                    print("Method  : " + classNode.getAttribute("name"))

        #I have no idea what this is looking for.
        methodNode = root.getElementsByTagName('Method')[0]
         #Prints the brackets, look at xml <Method classname> for deets
