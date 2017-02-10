#Building custom Checkstyle parser since none exist. RIP @me

from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os

print(len(sys.argv))
print(str(sys.argv))

EXEC_DIR = os.getcwd()
'''FILE_DIR = os.path.abspath(os.path.join(EXEC_DIR, \
    str(sys.argv[len(sys.argv) - 1].split("/")), "findBugs.xml"))
print(FILE_DIR)'''

FILE_DIR = os.path.abspath(os.path.join(EXEC_DIR))
print(FILE_DIR)
for arg in sys.argv[len(sys.argv) - 1].split("/"):
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    print(FILE_DIR)

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

for node in root.getElementsByTagName("BugInstance"):
    if node.nodeType != node.TEXT_NODE:
        line = "Bugtype: "
        line += node.getAttribute("type") + "\n"
        if node.hasAttribute("priority"):
            line += "Priority: " + node.getAttribute("priority")
        if node.hasAttribute("rank"):
            line += " Rank: " + node.getAttribute("rank") + "\n"
        if node.hasAttribute("abbrev"):
            print()
            line += "Abbrev: " + node.getAttribute("abbrev") + "\n"
        if node.hasAttribute("category"):
            line += "Category: " + node.getAttribute("category")

        print(line)

        classNode = root.getElementsByTagName('Class')[0]
        if classNode.hasAttribute("classname"):
            string = classNode.getAttribute("classname").split(".")
            string = string[len(string) - 1]
            print("Class: " + string)

        #I have no idea what this is looking for.
        methodNode = root.getElementsByTagName('Method')[0]
        if methodNode.hasAttribute("name"):
            print(methodNode.getElementsByTagName("name")) #Prints the brackets, look at xml <Method classname> for deets


    print()
