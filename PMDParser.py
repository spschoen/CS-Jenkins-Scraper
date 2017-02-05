# Parsing XML files with Python's Built-in DOM
# Document Object Model.  It's a lot easier than Element Tree.
# Documentation at: https://docs.python.org/3.6/library/xml.dom.minidom.html

#Uses Python 3.6

#Import the actual DOM Processors/parsers
from xml.dom.minidom import parse
import xml.dom.minidom

DOMTree = xml.dom.minidom.parse('pmd.xml')

root = DOMTree.documentElement

if root.hasAttribute("version"):
    print("Checkstyle Version : %s" % root.getAttribute("version"))

root = root.getElementsByTagName('file')[0]

#Of course, checking that this worked
if root.hasAttribute("name"):
    string = root.getAttribute("name").split('/')
    string = string[len(string) - 1]
    print("File Checked       : %s" % string)

node = root.getElementsByTagName('violation')[0]
print("\n")


# for node in root.childNodes:
    # if node.nodeType != node.TEXT_NODE:
    #     if node.hasAttribute("message") and "tab" not in node.getAttribute("message"):
if node.hasAttribute("beginline"):
    line = "Begin line: " + node.getAttribute("beginline")
    if node.hasAttribute("endline"):
        line += " End line: " + node.getAttribute("endline")
    print(line)
if node.hasAttribute("begincolumn"):
    line = "Begin column: " + node.getAttribute("begincolumn")
    if node.hasAttribute("endcolumn"):
        line += " End column: " + node.getAttribute("endcolumn")
        print(line)
if node.hasAttribute("rule"):
    print("Rule" + node.getAttribute("rule"))
    if node.hasAttribute("ruleset"):
        print("Ruleset: " + node.getAttribute("ruleset"))
if node.hasAttribute("class"):
    print("Class: " + node.getAttribute("class"))
if node.hasAttribute("method"):
    print("Method: " + node.getAttribute("method"))
print()

