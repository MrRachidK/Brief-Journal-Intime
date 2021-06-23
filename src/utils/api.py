import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
from fastapi import FastAPI
import datetime
from src.config import user, passwd
from src.utils.create_database import add_customer, customer_age
from src.utils.functions import *

db_connection, db_cursor = call_connector()

app = FastAPI()

@app.get("/")
def home():
    return {"Hello": "World"}

@app.post("/create_customer")
def create_customer(name:str, first_name:str, date_of_birth:datetime.date):
    customer_data = [(name, first_name, date_of_birth)]
    db_cursor.executemany(add_customer, customer_data)
    db_connection.commit()
    return {"name" : name, "first name" : first_name, "date of birth" : date_of_birth}

@app.delete("/delete_customer")
def delete_customer(name:str, first_name:str):
    query = """ DELETE FROM customer WHERE name = {} AND first_name = {} """.format(name, first_name)
    db_cursor.execute(query)
    db_connection.commit()
    return {"deleted_name" : name, "deleted_first_name" : first_name}

@app.put("/modify_customer")
def delete_customer(new_name:str, new_first_name:str, new_date_of_birth:datetime.date, id_customer:int):
    query = """ UPDATE customer SET name = '%s', first_name = '%s', date_of_birth='%s' WHERE id_customer = '%d'"""
    db_cursor.execute(query%(new_name, new_first_name, new_date_of_birth, id_customer))
    db_cursor.execute(customer_age)
    db_connection.commit()
    return {"new_name" : new_name, "new_first_name" : new_first_name, "new_date_of_birth" : new_date_of_birth}