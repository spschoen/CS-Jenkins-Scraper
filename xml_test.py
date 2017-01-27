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