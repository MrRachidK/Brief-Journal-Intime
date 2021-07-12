import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
from fastapi import FastAPI, HTTPException
from src.utils.create_database import create_database, create_customer_if_not_exists, create_text_if_not_exists, add_customer, add_text, create_customer_age
from src.utils.functions import call_connector, predict_emotion
from src.utils.classes import Text, TextBase, Customer, UserBase
import joblib
import uvicorn

model = joblib.load("/home/apprenant/Documents/Brief-Journal-Intime/src/models/regression_logistique_model.sav")
vectorizer = joblib.load("/home/apprenant/Documents/Brief-Journal-Intime/src/models/regression_logistique_vectorizer.joblib")

app = FastAPI()

@app.get("/")
def home():
    return {"Hello": "World"}

### Requêtes côté client

# Requête pour ajouter un nouveau texte

@app.post("/create_text/{database_name}")
def create_text(entry_text:Text, database_name):
    db_connection, db_cursor = call_connector(database_name)
    text_first_emotion, proba_emotion = predict_emotion(entry_text.text, vectorizer, model)
    proba_negative_emotion = round(proba_emotion[0][0] * 100, 4) 
    proba_positive_emotion = round(proba_emotion[0][1] * 100, 4)
    text_data = [(entry_text.id_customer, entry_text.text_date, entry_text.text, text_first_emotion, proba_negative_emotion, proba_positive_emotion)]
    add_text(db_connection, db_cursor, "coaching", text_data)
    return {"id_customer" : entry_text.id_customer, "text_date" : entry_text.text_date, "text" : entry_text.text, "text_first_emotion" : text_first_emotion, "proba_negative_emotion" : proba_negative_emotion, "proba_positive_emotion" : proba_positive_emotion}

# Requête pour modifier un texte dans la base de données

@app.put("/modify_text/{database_name}")
def modify_text(modify_text : Text, database_name):
    db_connection, db_cursor = call_connector(database_name)
    text_first_emotion, proba_emotion = predict_emotion(modify_text.text, vectorizer, model)
    proba_negative_emotion = round(proba_emotion[0][0] * 100, 4) 
    proba_positive_emotion = round(proba_emotion[0][1] * 100, 4)
    query = """ UPDATE text SET text = '%s', text_first_emotion = '%s', proba_negative_emotion = '%f', proba_positive_emotion = '%f' WHERE id_customer = '%d' AND text_date = '%s' """
    db_cursor.execute(query%(modify_text.text, text_first_emotion, proba_negative_emotion, proba_positive_emotion, modify_text.id_customer, modify_text.text_date))
    db_connection.commit()
    return {"id_customer" : modify_text.id_customer, "text_date" : modify_text.text_date, "new_text" : modify_text.text, "text_first_emotion" : text_first_emotion, "proba_negative_emotion" : proba_negative_emotion, "proba_positive_emotion" : proba_positive_emotion}

# Requête pour lire un texte à la date du jour ou aux autres dates

@app.get("/get_text/{database_name}")
def get_text(get_text : Text, database_name):
    db_connection, db_cursor = call_connector(database_name, isDictionnary=True)
    if get_text.text_date == None :
        query = """ SELECT * FROM text WHERE id_customer = '%d' """
        db_cursor.execute(query%(get_text.id_customer))
    else :
        query = """ SELECT * FROM text WHERE id_customer = '%d' AND text_date = '%s' """
        db_cursor.execute(query%(get_text.id_customer, get_text.text_date))
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

@app.post("/create_customer/{database_name}")
async def create_customer(customer:UserBase, database_name):
    db_connection, db_cursor = call_connector(database_name)
    customer_data = [(customer.name, customer.first_name, str(customer.date_of_birth))]
    add_customer(db_cursor, db_connection, database_name, customer_data)
    create_customer_age(db_connection, db_cursor, database_name)
    return customer

# Requête pour supprimer un client dans la base de données

@app.delete("/delete_customer/{database_name}")
def delete_customer(customer:UserBase, database_name):
    db_connection, db_cursor = call_connector(database_name)
    query = """ DELETE FROM customer WHERE name = '%s' AND first_name = '%s' AND date_of_birth = '%s'"""
    db_cursor.execute(query % (customer.name, customer.first_name, customer.date_of_birth))
    db_connection.commit()
    return customer

# Requête pour modifier un client dans la base de données

@app.put("/modify_customer/{database_name}")
def modify_customer(customer:Customer, database_name):
    db_connection, db_cursor = call_connector(database_name)
    query = """ UPDATE customer SET name = '%s', first_name = '%s', date_of_birth='%s' WHERE id_customer = '%d'"""
    db_cursor.execute(query%(customer.name, customer.first_name, customer.date_of_birth, customer.id_customer))
    db_connection.commit()
    create_customer_age(db_connection, db_cursor, database_name)
    return {"new_name" : customer.name, "new_first_name" : customer.first_name, "new_date_of_birth" : customer.date_of_birth}

# Requête pour lister tous les clients et les informations sur eux

@app.get("/get_client_infos/{database_name}")
def get_client_infos(database_name):
    db_connection, db_cursor = call_connector(database_name, isDictionnary=True)
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

@app.get("/get_text_infos/{database_name}")
def get_text_infos(text : TextBase, database_name):
    db_connection, db_cursor = call_connector(database_name, isDictionnary=True)
    isGettingInfos = True
    while isGettingInfos:
        if text.text_date != None :
            query = """ SELECT * FROM text WHERE id_customer = '%d' AND text_date = '%s' """
            db_cursor.execute(query%(text.id_customer, text.text_date))
            rows = db_cursor.fetchall()
            print(rows)
            text_dict = {}
            n = 0
            for row in rows:
                row = {"id_customer" : row['id_customer'], "text_date" : row['text_date'], "text" : row["text"], "text_first_emotion" : row["text_first_emotion"], "proba_negative_emotion" : row["proba_negative_emotion"], "proba_positive_emotion" : row["proba_positive_emotion"]}
                text_dict[n] = row
                n += 1
            db_connection.commit()
            isGettingInfos = False
        else :
            pass
    return text_dict

# Requête pour obtenir la roue des sentiments moyenne d'un client sur une période donnée

@app.get("/get_average_feeling_wheel_client/{database_name}")
def get_average_feeling_wheel_client(text:TextBase, database_name):
    db_connection, db_cursor = call_connector(database_name, isDictionnary=True)
    query = """ SELECT * FROM text WHERE id_customer = '%d' AND (text_date >= '%s' AND text_date <= '%s') """
    db_cursor.execute(query%(text.id_customer, text.date_start, text.date_end))
    rows = db_cursor.fetchall()
    print(rows)
    text_numbers = 0
    average_negative_emotion = 0
    average_positive_emotion = 0
    average_feeling_wheel_client = {"text_numbers": text_numbers, "average_negative_emotion": average_negative_emotion, "average_positive_emotion": average_positive_emotion}
    for row in rows:
        text_numbers += 1
        average_negative_emotion = average_negative_emotion + row["proba_negative_emotion"]
        average_feeling_wheel_client["average_negative_emotion"] = average_negative_emotion
        average_positive_emotion = average_positive_emotion + row["proba_positive_emotion"]
        average_feeling_wheel_client["average_positive_emotion"] = average_positive_emotion
    average_feeling_wheel_client["text_numbers"] = text_numbers
    average_feeling_wheel_client["average_negative_emotion"] = round(average_feeling_wheel_client["average_negative_emotion"] / len(rows), 4)
    average_feeling_wheel_client["average_positive_emotion"] = round(average_feeling_wheel_client["average_positive_emotion"] / len(rows), 4)
    return average_feeling_wheel_client

# Requête pour obtenir la roue des sentiments moyenne de tous les clients sur une période donnée

@app.get("/get_average_feeling_wheel_clients/{database_name}")
def get_average_feeling_wheel_clients(text:TextBase, database_name):
    db_connection, db_cursor = call_connector(database_name, isDictionnary=True)
    query = """ SELECT * FROM text WHERE text_date >= '%s' AND text_date <= '%s' """
    db_cursor.execute(query%(text.date_start, text.date_end))
    rows = db_cursor.fetchall()
    print(rows)
    text_numbers = 0
    average_negative_emotion = 0
    average_positive_emotion = 0
    average_feeling_wheel_clients = {"text_numbers": text_numbers, "average_negative_emotion": average_negative_emotion, "average_positive_emotion": average_positive_emotion}
    for row in rows:
        text_numbers += 1
        average_negative_emotion = average_negative_emotion + row["proba_negative_emotion"]
        average_feeling_wheel_clients["average_negative_emotion"] = average_negative_emotion
        average_positive_emotion = average_positive_emotion + row["proba_positive_emotion"]
        average_feeling_wheel_clients["average_positive_emotion"] = average_positive_emotion
    average_feeling_wheel_clients["text_numbers"] = text_numbers
    average_feeling_wheel_clients["average_negative_emotion"] = round(average_feeling_wheel_clients["average_negative_emotion"] / len(rows), 4)
    average_feeling_wheel_clients["average_positive_emotion"] = round(average_feeling_wheel_clients["average_positive_emotion"] / len(rows), 4)
    return average_feeling_wheel_clients

if __name__ == "__main__" :
    create_database("coaching")
    create_customer_if_not_exists("coaching")
    create_text_if_not_exists("coaching")
    uvicorn.run(app, host="127.0.0.1", port=8000)
