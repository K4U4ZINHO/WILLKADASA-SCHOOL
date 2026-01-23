import mysql.connector
import sqlite3
import psycopg2

willkadasa = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword"
  base_dados="willkadasa"
)

mycursor = willkadasa.cursor()

mycursor.execute("CREATE DATABASE willkadasa")
 


 #DANIEL