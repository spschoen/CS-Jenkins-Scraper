#Building custom Checkstyle parser since none exist. RIP @me

from xml.dom.minidom import parse
import xml.dom.minidom


DOMTree = xml.dom.minidom.parse('findbugs.xml')  # parse an XML file by name

#root is the first <> element in the XML file.
root = DOMTree.documentElement

if root.hasAttribute("version"):
    print("FindBugs Version : %s" % root.getAttribute("version"))

root = root.getElementsByTagName('BugInstance')[0]

if root.hasAttribute("type"):

# for root in root.childNodes:      Cant get for loop to work. Rip
    line = "Bugtype: "          
    line += root.getAttribute("type") + "\n"
    if root.hasAttribute("priority"):
        line += "Priority: " + root.getAttribute("priority")
        if root.hasAttribute("rank"):
            line += " Rank: " + root.getAttribute("rank") + "\n"
            if root.hasAttribute("abbrev"):
                print()
                line += "Abbrev: " + root.getAttribute("abbrev") + "\n"
            if root.hasAttribute("category"):
                line += "Category: " + root.getAttribute("category")
                print(line)
    node = root.getElementsByTagName('Class')[0]
    if node.hasAttribute("classname"):
        string = node.getAttribute("classname").split(".")
        string = string[len(string) - 1]
        print("Class: " + string)
    node = root.getElementsByTagName('Method')[0]
    if node.hasAttribute("name"):
        print(root.getElementsByTagName("name")) #Prints the brackets, look at xml <Method classname> for deets


    print()

