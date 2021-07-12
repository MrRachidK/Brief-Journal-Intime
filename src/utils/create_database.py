from os import name
import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
from mysql.connector.errors import IntegrityError, ProgrammingError
from src.utils.functions import call_connector

def create_database(database_name):
     # Creation of our database named "coaching"
     db_connection, db_cursor = call_connector()
     create_database = "CREATE DATABASE IF NOT EXISTS {}".format(database_name) # Query to create the database
     try:
         db_cursor.execute(create_database)
     except ProgrammingError:
         print("La database n'existe pas !")
     db_connection.commit()

def display_db(database_name):
     # Connection with MySQL
     db_connection, db_cursor = call_connector(database_name)
     show_databases = "SHOW DATABASES" # Query to show the databases
     db_cursor.execute(show_databases) # Displaying of our databases

     for db in db_cursor:
          print(db) # Printing of all the databases


def create_customer_if_not_exists(database_name):
     # Creation of the table 'customer' if it does not exists
     db_connection, db_cursor = call_connector(database_name) # Connection with MySQL
     use_database = "USE {}".format(database_name)
     db_cursor.execute(use_database)
     create_customer_table = """CREATE TABLE IF NOT EXISTS customer(
     id_customer INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
     name VARCHAR(40) NOT NULL,
     first_name VARCHAR(40) NOT NULL,
     date_of_birth DATE NOT NULL,
     age INT,
     PRIMARY KEY (id_customer)
     )"""
     db_cursor.execute(create_customer_table)
     db_connection.commit()

def add_customer(db_connection, db_cursor, database_name, customer_data):
     # Creation of a customer
     db_connection, db_cursor = call_connector(database_name)
     add_customer = ("INSERT INTO customer "
               "(name, first_name, date_of_birth)"
               "VALUES (%s, %s, %s)"
     )
     db_cursor.executemany(add_customer, customer_data)
     db_connection.commit()

def add_unique_customer(database_name):
     # Creation of an unique customer
     db_connection, db_cursor = call_connector(database_name) # Connection with MySQL
     add_unique_customer = ("""ALTER TABLE customer
                         ADD CONSTRAINT UC_Customer UNIQUE (name, first_name, date_of_birth); 
                         """)
     try:
          db_cursor.execute(add_unique_customer)
     except IntegrityError:
          print("Attention ! Vous essayez de renseigner un même client")
     db_connection.commit()

def create_customer_age(db_connection, db_cursor, database_name):
     # Creation of customer age
     db_connection, db_cursor = call_connector(database_name)
     customer_age = "UPDATE customer SET age = (SELECT DATE_FORMAT(NOW(), '%Y') - DATE_FORMAT(date_of_birth, '%Y') - (DATE_FORMAT(NOW(), '00-%m-%d') < DATE_FORMAT(date_of_birth, '00-%m-%d')))"
     db_cursor.execute(customer_age)
     db_connection.commit()

def create_text_if_not_exists(database_name):
     # Creation of the table 'text' if it does not exists
     db_connection, db_cursor = call_connector(database_name)
     use_database = "USE {}".format(database_name)
     db_cursor.execute(use_database)
     create_text_table = """ CREATE TABLE IF NOT EXISTS text(
     id_text INTEGER UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
     id_customer INTEGER UNSIGNED NOT NULL,
     text_date DATE NOT NULL,
     text VARCHAR(500) NOT NULL,
     text_first_emotion VARCHAR(40) NOT NULL,
     proba_negative_emotion FLOAT NOT NULL,
     proba_positive_emotion FLOAT NOT NULL,
     FOREIGN KEY (id_customer) REFERENCES customer(id_customer) ON DELETE CASCADE
     )
     """
     db_cursor.execute(create_text_table)
     db_connection.commit()

def add_text(db_connection, db_cursor, database_name, text_data):
     # Add text to the text table
     db_connection, db_cursor = call_connector(database_name)
     add_text = ("INSERT INTO text"
            "(id_customer, text_date, text, text_first_emotion, proba_negative_emotion, proba_positive_emotion)"
            "VALUES (%s, %s, %s, %s, %s, %s)"
     )
     db_cursor.executemany(add_text, text_data)
     db_connection.commit()

def delete_database(database_name):
     db_connection, db_cursor = call_connector(database_name)
     drop_database = "DROP DATABASE {}".format(database_name)
     db_cursor.execute(drop_database)
     db_connection.commit()
 
if __name__ == "__main__":
     delete_database("coaching")
     create_database("coaching")
     display_db("coaching")
     create_customer_if_not_exists("coaching")
     add_unique_customer("coaching")
     create_text_if_not_exists("coaching")
