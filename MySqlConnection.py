import mysql.connector
from mysql.connector import errorcode
from app import app

try:
  mydb = mysql.connector.connect(
    host="127.0.0.1",
    port= "3306",
    user="root",
    passwd="Bhoj!1996",
    database="crm"
  )

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
    print("MySql connected successfully")
    #mydb.close()
