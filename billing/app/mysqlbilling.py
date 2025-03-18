import mysql.connector
import os

def connect():
  connection = None
  try:
    connection = mysql.connector.connect(
      host=os.environ.get('MYSQL_HOST', 'localhost'),
      port=int(os.environ.get('MYSQL_PORT', 3306)),  # Default 3306 if not set
      user=os.environ.get('MYSQL_USER', 'root'),
      password=os.environ.get('MYSQL_PASSWORD', 'rootpassword'),
      database="billdb"
    )
    print("MySQL Database connection successful")
  except mysql.connector.Error as err:
    raise
    print(f"Error: '{err}'")

  return connection

connect()
