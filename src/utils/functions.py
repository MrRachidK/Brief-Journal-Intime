import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
import mysql.connector
from src.config import user, passwd

def call_connector():
    db_connection = mysql.connector.connect(
    host="localhost",
    user=user,
    passwd = passwd,
    database="coaching")

    db_cursor = db_connection.cursor(buffered=True)
    return db_connection, db_cursor