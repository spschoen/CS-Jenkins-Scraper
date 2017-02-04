#Building custom Checkstyle parser since none exist. RIP @me

from xml.dom.minidom import parse
import xml.dom.minidom


DOMTree = xml.dom.minidom.parse('findbugs.xml')  # parse an XML file by name

#root is the first <> element in the XML file.
root = DOMTree.documentElement

if root.hasAttribute("version"):
    print("FindBugs Version : %s" % root.getAttribute("version"))

root = root.getElementsByTagName('BugInstance')[0]   #This is wrong and I know it, but 
                                                        #I'm putting it here for a dummy variable
if root.hasAttribute("type"):
    string = root.getAttribute("type").split('/')  
    string = string[len(string) - 1]
    print("File Checked       : %s" % string)           #Struggling with grabbing the 
                                                            # file name, pobs not that important rn
for node in root.childNodes:

   # if node.nodeType != node.TEXT_NODE:
        if node.hasAttribute("type"):
            if node.hasAttribute("priority"):
                line = node.getAttribute("priority")
                if node.hasAttribute("rank"):
                    line += ":" + node.getAttribute("rank")
                print(line)
            if node.hasAttribute("type"):
                print(node.getAttribute("type"))
            if node.hasAttribute("category"):
                print(node.getAttribute("category"))
            print()

