import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
from mysql.connector.errors import ProgrammingError, IntegrityError
import pandas as pd
from src.config import user, passwd
from src.utils.functions import *
import joblib

model = joblib.load("/home/apprenant/Documents/Brief-Journal-Intime/src/models/regression_logistique_model.sav")
vectorizer = joblib.load("/home/apprenant/Documents/Brief-Journal-Intime/src/models/regression_logistique_vectorizer.joblib")

### Access to MySQL 

db_connection, db_cursor = call_connector()

print(db_connection)

### Creation of our database named "coaching"

# drop_database = "DROP DATABASE coaching"

create_database = "CREATE DATABASE IF NOT EXISTS coaching" # Query to create the database

show_databases = "SHOW DATABASES" # Query to show the databases

use_database = "USE coaching"

### All the queries about the table 'Customer'

create_customer_table = """CREATE TABLE IF NOT EXISTS customer(
     id_customer INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
     name VARCHAR(40) NOT NULL,
     first_name VARCHAR(40) NOT NULL,
     date_of_birth DATE NOT NULL,
     age INT,
     PRIMARY KEY (id_customer)
)"""

add_customer = ("INSERT INTO customer "
               "(name, first_name, date_of_birth)"
               "VALUES (%s, %s, %s)"
)

add_unique_customer = ("""ALTER TABLE customer
                          ADD CONSTRAINT UC_Customer UNIQUE (name, first_name, date_of_birth); 
""")

customer_age = "UPDATE customer SET age = (SELECT DATE_FORMAT(NOW(), '%Y') - DATE_FORMAT(date_of_birth, '%Y') - (DATE_FORMAT(NOW(), '00-%m-%d') < DATE_FORMAT(date_of_birth, '00-%m-%d')))"

### All the queries about the table 'text'

create_text_table = """
CREATE TABLE IF NOT EXISTS text(
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

add_text = ("INSERT INTO text"
            "(id_customer, text_date, text, text_first_emotion, proba_negative_emotion, proba_positive_emotion)"
            "VALUES (%s, %s, %s, %s, %s, %s)"
)


### All the executions of our queries

# db_cursor.execute(drop_database)

# Creation of the database 'coaching' if it does not exists
try:
     db_cursor.execute(create_database)
except ProgrammingError as progErr:
     print("La database n'existe pas !")
      
db_cursor.execute(show_databases) # Displaying of our databases

for db in db_cursor:
	print(db) # Printing of all the databases 

db_cursor.execute(use_database)

try:
     db_cursor.execute(create_customer_table) # Creation of the table 'customer' if it does not exists
except ProgrammingError as progErr:
     print("La table n'existe pas !")

try:
     db_cursor.execute(add_unique_customer)
except ProgrammingError as progErr:
     print("Attention ! Vous essayez de renseigner un même client")

db_cursor.execute(create_text_table) # Creation of the table 'text' if it does not exists

# # Get some texts from emotion CSV
# my_texts = pd.read_csv("/home/apprenant/Documents/Brief-Journal-Intime/data/cleaned_emotion_final.csv")
# string_texts = my_texts['text'].sample(200).to_list() # Select 200 random texts from the CSV

# To associate a text to an ID, we first get all the IDs of the customer table
# db_cursor.execute("SELECT * FROM customer")
# result = db_cursor.fetchall() # Fetch all the rows of our customer table

# # Let's add the IDs in a list
# list_id_customer = []
# for row in result:
#     id=row[0]
#     list_id_customer.append(id)

# Let's create our datas for the table

# data_text = []
# for i in range(len(string_texts)):
#      random_date = insert_random_date()
#      predicted_emotion, proba_emotion = predict_emotion(string_texts[i], vectorizer, model)
#      text = (random.choice(list_id_customer), random_date, string_texts[i], predicted_emotion, round(proba_emotion[0][0] * 100, 4), round(proba_emotion[0][1] * 100, 4))
#      data_text.append(text)

# try:
#      db_cursor.executemany(add_text, data_text)
# except IntegrityError as intErr:
#      print("Vous essayez d\'ajouter de la donnée")

db_connection.commit()

