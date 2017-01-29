from future_builtins import *
import xml.etree.ElementTree as ET  #Grab that XML Parsing.
import MySQLdb
import os

tree = ET.parse('Style_Errors.xml') #Get the XML File.
root = tree.getroot()               #Get the root of the XML.
root = root[0]                      #Since this is checkstyle, set root to root's child
                                    #As that's actual data.

#The DB conection
dbConnect = MySQLdb.connect("localhost","root","p@55w0rd","WTP")

#Because this is how we connect
cur = dbConnect.cursor()

for error in root.iter('error'):
    col = int(error.get('column', -1))
    line = int(error.get('line'))
    if col == -1:
        insert = "INSERT INTO style (id, severity, message, line, col) VALUES \
        (NULL, '%s', '%s', '%d', NULL)" % \
        (error.get('severity'), \
        error.get('message').replace('\n','').replace('\'','\\\'')[:50], line)
    else:
        insert = "INSERT INTO style (id, severity, message, line, col) VALUES \
        (NULL, '%s', '%s', '%d', '%d')" % \
        (error.get('severity'), \
        error.get('message').replace('\n','').replace('\'','\\\'')[:50], \
        line, col)


    try:
        cur.execute(insert)
        dbConnect.commit()
    except:
        print("Unable to execute NULL, '%s', '%s', '%d', '%d'") % \
        (NULL, error.get('severity'), \
        error.get('message').replace('\n','').replace('\'','\\\'')[:50], \
        error.get('line'), col)
        dbConnect.rollback()

#Close the connection.
dbConnect.close()
