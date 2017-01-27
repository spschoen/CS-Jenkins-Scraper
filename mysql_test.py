#sudo /etc/init.d/mysql start

#Import the driver
import MySQLdb

#Because urghhhh
from future_builtins import *

#The DB conection
cnx = MySQLdb.connect("localhost","root","p@55w0rd","WTP")

#Because this is how we connect
cur = cnx.cursor()

#insert = """INSERT INTO potluck(id, name, food, confirmed, signup_date)
#            VALUES (NULL, "Name", "Foodstuffs", "Y", '2012-04-13')"""
#remove = "DELETE FROM potluck WHERE food = 'Foodstuffs'"

#Because you can't be too safe.
#Wrapped in a try/except so that, incase the commit fails,
#the changes will be rolled back and the DB won't be
#affected.
try:
    #cur.execute(insert)
    #cur.execute(remove)
    cnx.commit()
except:
    cnx.rollback()

#Debug below: selects all from the table, and then prints it.
cur.execute("SELECT * FROM potluck")

for row in cur.fetchall():
    print(row)

#Close the connection.
cnx.close()
