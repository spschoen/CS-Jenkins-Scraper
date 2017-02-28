#Building custom TestFile parser since none exist. RIP @me

from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os


FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
# print(FILE_DIR)
for arg in sys.argv[len(sys.argv) - 1].split("/"):
    if arg == "":
        continue
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(FILE_DIR)

filesListed = os.listdir(FILE_DIR);
count = 0
while (count < len(filesListed)):
    print(filesListed[count])
    if (filesListed[count] != '.DS_Store'):
        try:
            DOMTree = xml.dom.minidom.parse(FILE_DIR + '/' + filesListed[count])
        except:
            print("ERROR: Could not interact with file", FILE_DIR + '/' + filesListed[count] + '.xml')
            print("Script exiting.")
            sys.exit()


        #root is the first <> element in the XML file.
        root = DOMTree.documentElement

        if root.hasAttribute("name"):
            print("\nTest Case: " + root.getAttribute("name").split(".")[-1] + "\n")  

            for node in root.childNodes:
                if node.nodeName == "testcase":
                    if node.hasAttribute("name"):
                        line = "Name: " + node.getAttribute("name")
                    print(line)
                    if len(node.childNodes) != 0:
                        print("Results: FAIL \n")
                    else: 
                        print("Results: PASS \n")
    count += 1

        