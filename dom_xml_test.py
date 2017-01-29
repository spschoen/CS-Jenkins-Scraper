from xml.dom.minidom import parse
import xml.dom.minidom

DOMTree = xml.dom.minidom.parse('Style_Errors.xml')
root = DOMTree.documentElement

if root.hasAttribute("version"):
    print("Checkstyle Version : %s" % root.getAttribute("version"))
    
root = root.getElementsByTagName('file')[0]
if root.hasAttribute("name"):
    string = root.getAttribute("name").split('/')
    string = string[len(string) - 1]
    print("File Checked       : %s" % string)

for node in root.childNodes:
    if node.nodeType != node.TEXT_NODE:
        if node.hasAttribute("message") and "tab" not in node.getAttribute("message"):
            if node.hasAttribute("line"):
                line = node.getAttribute("line")
                if node.hasAttribute("column"):
                    line += ":" + node.getAttribute("column")
                print(line)
            if node.hasAttribute("severity"):
                print(node.getAttribute("severity"))
            if node.hasAttribute("source"): 
                string = node.getAttribute("source").split('.')
                string = string[len(string) - 1]
                print(string)
            if node.hasAttribute("message"):
                print(node.getAttribute("message"))
            print()