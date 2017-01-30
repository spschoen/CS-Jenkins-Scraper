#Element Tree XML parser - the first XML Parser I found and used.
#It was col but it's just awkward to use and doesn't have the methods and
#security I wanted, so I abandonned it later.
#This can be ignored, but is being saved in the Repo just because it could
#Be useful in the future.  Never delete obselete code, just remove it from
#Production!

#Reminder to self: research Blue/Green deployment.

#This file can pretty much be ignored, since XML_Parser_ElementTree.py
#Shows off the methods better and with useful application.

import xml.etree.ElementTree as ET  #Grab that XML Parsing.
tree = ET.parse('Style_Errors.xml') #Get the XML File.
root = tree.getroot()               #Get the root of the XML.
root = root[0]                      #Since this is checkstyle, set root to root's child
                                    #As that's actual data.
print(root.tag, ": ", root.attrib)

i = 0

for error in root.iter('error'):
    # print(error.attrib)
    # <message="Line contains a tab character." source="com.puppycrawl.tools.checkstyle.checks.whitespace.FileTabCharacterCheck"/>
    print('Error', i)
    print(' |-->     Line:', error.get('line'))
    print(' |-->   Column:', error.get('column'))
    print(' |--> Severity:', error.get('severity'))
    print(' |-->  Message:', error.get('message'))
    print()
    #print(error.items())
    i += 1
