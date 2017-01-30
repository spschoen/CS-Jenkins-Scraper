#sudo /etc/init.d/mysql start
#Command ot start the mysql server on Unix.

#Commands have been commented out in this file, kept as reminders as what
#to do for insertion/deletion.

#Import the driver
import MySQLdb

#Python 2.7 compatibility.
from future_builtins import *

#The DB conection
#Logs into the MySQL DB at localhost using the root username and p@55w0rd
#password, then uses the WTP Table.
cnx = MySQLdb.connect("localhost","root","p@55w0rd","WTP")

#Because this is how we connect
#The cursor is used to perform queries in the DB.
cur = cnx.cursor()

#Example of Insertion and deletion queries in the MySQL DB
#insert = """INSERT INTO potluck(id, name, food, confirmed, signup_date) \
#            VALUES (NULL, "Name", "Foodstuffs", "Y", '2012-04-13')"""
#remove = "DELETE FROM potluck WHERE food = 'Foodstuffs'"

#Because you can't be too safe.
#Wrapped in a try/except so that, incase the commit fails,
#the changes will be rolled back and the DB won't be affected.
try:
    #cur.execute(insert)
    #cur.execute(remove)

    #Commit actually sends the comand.
    cnx.commit()
except:
    #If, for whatever reason, the command fails, we undo running it.
    cnx.rollback()

#Debug below: selects all from the table, and then prints it.
cur.execute("SELECT * FROM potluck")

#and print what we got.
for row in cur.fetchall():
    print(row)

#Close the connection.
cnx.close()
