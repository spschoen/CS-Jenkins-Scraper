#sudo /etc/init.d/mysql start

import MySQLdb
from future_builtins import *

cnx = MySQLdb.connect("localhost","root","p@55w0rd","WTP")

cur = cnx.cursor()

#insert = """INSERT INTO potluck(id, name, food, confirmed, signup_date)
#            VALUES (NULL, "Name", "Foodstuffs", "Y", '2012-04-13')"""
#remove = "DELETE FROM potluck WHERE food = 'Foodstuffs'"

try:
    #cur.execute(insert)
    #cur.execute(remove)
    cnx.commit()
except:
    cnx.rollback()

cur.execute("SELECT * FROM potluck")

for row in cur.fetchall():
    print(row)

cnx.close()
