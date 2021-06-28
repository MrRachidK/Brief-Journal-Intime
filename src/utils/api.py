import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
from fastapi import FastAPI, Form
import datetime
from typing import Optional
from src.config import user, passwd
from src.utils.create_database import add_customer, add_text, customer_age, model, vectorizer
from src.utils.functions import *
from src.utils.classes import *

db_connection, db_cursor = call_connector()

app = FastAPI()

@app.get("/")
def home():
    return {"Hello": "World"}

### Requêtes côté client

# Requête pour ajouter un nouveau texte

@app.post("/create_text/")
def create_text(entry_text:Text):
    text_first_emotion, proba_emotion = predict_emotion(entry_text.text, vectorizer, model)
    proba_negative_emotion = round(proba_emotion[0][0] * 100, 4) 
    proba_positive_emotion = round(proba_emotion[0][1] * 100, 4)
    text_data = [(entry_text.id_customer, entry_text.text_date, entry_text.text, text_first_emotion, proba_negative_emotion, proba_positive_emotion)]
    db_cursor.executemany(add_text, text_data)
    db_connection.commit()
    return {"id_customer" : entry_text.id_customer, "text date" : entry_text.text_date, "text" : entry_text.text, "text first emotion" : text_first_emotion, "proba_negative_emotion" : proba_negative_emotion, "proba_positive_emotion" : proba_positive_emotion}

# Requête pour modifier un texte dans la base de données

@app.put("/modify_text")
def modify_text(new_text:str, id_customer:int, text_date:datetime.date):
    text_first_emotion, proba_emotion = predict_emotion(new_text, vectorizer, model)
    proba_negative_emotion = round(proba_emotion[0][0] * 100, 4) 
    proba_positive_emotion = round(proba_emotion[0][1] * 100, 4)
    query = """ UPDATE text SET text = '%s', text_first_emotion = '%s', proba_negative_emotion = '%f', proba_positive_emotion = '%f' WHERE id_customer = '%d' AND text_date = '%s' """
    db_cursor.execute(query%(new_text, text_first_emotion, proba_negative_emotion, proba_positive_emotion, id_customer, text_date))
    db_connection.commit()
    return {"id_customer" : id_customer, "text_date" : text_date, "new_text" : new_text, "text_first_emotion" : text_first_emotion, "proba_negative_emotion" : proba_negative_emotion, "proba_positive_emotion" : proba_positive_emotion}

# Requête pour lire un texte à la date du jour ou aux autres dates

@app.get("/get_text")
def get_text(id_customer : int, text_date : Optional[datetime.date] = None):
    db_cursor = db_connection.cursor(buffered=True, dictionary=True)
    if text_date :
        query = """ SELECT * FROM text WHERE id_customer = '%d' AND text_date = '%s' """
        db_cursor.execute(query%(id_customer, text_date))
    else :
        query = """ SELECT * FROM text WHERE id_customer = '%d' """
        db_cursor.execute(query%(id_customer))
    rows = db_cursor.fetchall()
    text_dict = {}
    n = 0
    for row in rows:
        row = {"id_customer" : row['id_customer'], "text_date" : row['text_date'], "text" : row["text"]}
        text_dict[n] = row
        n += 1
    db_connection.commit()
    return text_dict

### Requêtes côté coach

# Requête pour ajouter un nouveau client

@app.post("/create_customer")
async def create_customer(customer:Customer):
    customer_data = [(customer.name, customer.first_name, str(customer.date_of_birth))]
    db_cursor.executemany(add_customer, customer_data)
    db_cursor.execute(customer_age)
    db_connection.commit()
    return customer

# Requête pour supprimer un client dans la base de données

@app.delete("/delete_customer")
def delete_customer(customer:Customer):
    query = """ DELETE FROM customer WHERE name = '%s' AND first_name = '%s' """ % (customer.name, customer.first_name)
    db_cursor.execute(query)
    db_connection.commit()
    return {"deleted_name" : customer.name, "deleted_first_name" : customer.first_name}

# Requête pour modifier un client dans la base de données

@app.put("/modify_customer")
def modify_customer(new_name:str, new_first_name:str, new_date_of_birth:datetime.date, id_customer:int):
    query = """ UPDATE customer SET name = '%s', first_name = '%s', date_of_birth='%s' WHERE id_customer = '%d'"""
    db_cursor.execute(query%(new_name, new_first_name, new_date_of_birth, id_customer))
    db_cursor.execute(customer_age)
    db_connection.commit()
    return {"new_name" : new_name, "new_first_name" : new_first_name, "new_date_of_birth" : new_date_of_birth}

# Requête pour lister tous les clients et les informations sur eux

@app.get("/get_client_infos")
def get_client_infos():
    db_cursor = db_connection.cursor(buffered=True, dictionary=True)
    query = """ SELECT * FROM customer """
    db_cursor.execute(query)
    rows = db_cursor.fetchall()
    customer_dict = {}
    for row in rows:
        row = {"id_customer" : row["id_customer"], "name" : row["name"], "first_name" : row["first_name"], "date_of_birth" : row["date_of_birth"], "age" : row["age"]}
        customer_dict[int(row["id_customer"])] = row
    db_connection.commit()
    return customer_dict

# Requête pour lire un texte d'un client à une date précise et les infos sur le texte

@app.get("/get_text_infos")
def get_text_infos(id_customer : int, text_date : datetime.date):
    db_cursor = db_connection.cursor(buffered=True, dictionary=True)
    query = """ SELECT * FROM text WHERE id_customer = '%d' AND text_date = '%s' """
    db_cursor.execute(query%(id_customer, text_date))
    rows = db_cursor.fetchall()
    print(rows)
    text_dict = {}
    n = 0
    for row in rows:
        row = {"id_customer" : row['id_customer'], "text_date" : row['text_date'], "text" : row["text"], "text_first_emotion" : row["text_first_emotion"], "proba_negative_emotion" : row["proba_negative_emotion"], "proba_positive_emotion" : row["proba_positive_emotion"]}
        text_dict[n] = row
        n += 1
    db_connection.commit()
    return text_dict

# Requête pour obtenir la roue des sentiments moyenne d'un client sur une période donnée

@app.get("/get_average_feeling_wheel_client")
def get_average_feeling_wheel_client(id_customer : int, date_start : datetime.date, date_end : datetime.date):
    db_cursor = db_connection.cursor(buffered=True, dictionary=True)
    query = """ SELECT * FROM text WHERE id_customer = '%d' AND (text_date > '%s' AND text_date < '%s') """
    db_cursor.execute(query%(id_customer, date_start, date_end))
    rows = db_cursor.fetchall()
    print(rows)
    average_negative_emotion = 0
    average_positive_emotion = 0
    average_feeling_wheel_client = {"average_negative_emotion": average_negative_emotion, "average_positive_emotion": average_positive_emotion}
    for row in rows:
        average_negative_emotion = average_negative_emotion + row["proba_negative_emotion"]
        average_feeling_wheel_client["average_negative_emotion"] = average_negative_emotion
        average_positive_emotion = average_positive_emotion + row["proba_positive_emotion"]
        average_feeling_wheel_client["average_positive_emotion"] = average_positive_emotion
    average_feeling_wheel_client["average_negative_emotion"] = round(average_feeling_wheel_client["average_negative_emotion"] / len(rows), 4)
    average_feeling_wheel_client["average_positive_emotion"] = round(average_feeling_wheel_client["average_positive_emotion"] / len(rows), 4)
    return average_feeling_wheel_client

# Requête pour obtenir la roue des sentiments moyenne de tous les clients sur une période donnée

@app.get("/get_average_feeling_wheel_clients")
def get_average_feeling_wheel_clients(date_start : datetime.date, date_end : datetime.date):
    db_cursor = db_connection.cursor(buffered=True, dictionary=True)
    query = """ SELECT * FROM text WHERE text_date > '%s' AND text_date < '%s' """
    db_cursor.execute(query%(date_start, date_end))
    rows = db_cursor.fetchall()
    print(rows)
    average_negative_emotion = 0
    average_positive_emotion = 0
    average_feeling_wheel_clients = {"average_negative_emotion": average_negative_emotion, "average_positive_emotion": average_positive_emotion}
    for row in rows:
        average_negative_emotion = average_negative_emotion + row["proba_negative_emotion"]
        average_feeling_wheel_clients["average_negative_emotion"] = average_negative_emotion
        average_positive_emotion = average_positive_emotion + row["proba_positive_emotion"]
        average_feeling_wheel_clients["average_positive_emotion"] = average_positive_emotion
    print(average_negative_emotion)
    print(average_positive_emotion)
    average_feeling_wheel_clients["average_negative_emotion"] = round(average_feeling_wheel_clients["average_negative_emotion"] / len(rows), 4)
    average_feeling_wheel_clients["average_positive_emotion"] = round(average_feeling_wheel_clients["average_positive_emotion"] / len(rows), 4)
    return average_feeling_wheel_clients