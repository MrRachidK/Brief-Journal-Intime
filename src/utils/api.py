import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
from fastapi import FastAPI, Form
import datetime
from src.config import user, passwd
from src.utils.create_database import add_customer
from src.utils.functions import *

  
db_connection, db_cursor = call_connector()

app = FastAPI()

@app.get("/")
def home():
    return {"Hello": "World"}

@app.post("/create_customer")
def create_customer(name:str = Form(...), first_name:str = Form(...), date_of_birth:datetime.date = Form(...)):
    customer_data = [(name, first_name, date_of_birth)]
    db_cursor.executemany(add_customer, customer_data)
    db_connection.commit()
    return {"name" : name, "first name" : first_name, "date of birth" : date_of_birth}
