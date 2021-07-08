import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
from fastapi import FastAPI
from src.utils.create_database import create_coaching_database, create_customer_if_not_exists, create_text_if_not_exists, add_customer, add_text, create_customer_age
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

@app.post("/create_text")
def create_text(entry_text:Text):
    db_connection, db_cursor = call_connector()
    text_first_emotion, proba_emotion = predict_emotion(entry_text.text, vectorizer, model)
    proba_negative_emotion = round(proba_emotion[0][0] * 100, 4) 
    proba_positive_emotion = round(proba_emotion[0][1] * 100, 4)
    text_data = [(entry_text.id_customer, entry_text.text_date, entry_text.text, text_first_emotion, proba_negative_emotion, proba_positive_emotion)]
    add_text(db_connection, db_cursor, text_data)
    return {"id_customer" : entry_text.id_customer, "text_date" : entry_text.text_date, "text" : entry_text.text, "text_first_emotion" : text_first_emotion, "proba_negative_emotion" : proba_negative_emotion, "proba_positive_emotion" : proba_positive_emotion}

# Requête pour modifier un texte dans la base de données

@app.put("/modify_text")
def modify_text(modify_text : Text):
    db_connection, db_cursor = call_connector()
    text_first_emotion, proba_emotion = predict_emotion(modify_text.text, vectorizer, model)
    proba_negative_emotion = round(proba_emotion[0][0] * 100, 4) 
    proba_positive_emotion = round(proba_emotion[0][1] * 100, 4)
    query = """ UPDATE text SET text = '%s', text_first_emotion = '%s', proba_negative_emotion = '%f', proba_positive_emotion = '%f' WHERE id_customer = '%d' AND text_date = '%s' """
    db_cursor.execute(query%(modify_text.text, text_first_emotion, proba_negative_emotion, proba_positive_emotion, modify_text.id_customer, modify_text.text_date))
    db_connection.commit()
    return {"id_customer" : modify_text.id_customer, "text_date" : modify_text.text_date, "new_text" : modify_text.text, "text_first_emotion" : text_first_emotion, "proba_negative_emotion" : proba_negative_emotion, "proba_positive_emotion" : proba_positive_emotion}

# Requête pour lire un texte à la date du jour ou aux autres dates

@app.get("/get_text")
def get_text(get_text : Text):
    db_connection, db_cursor = call_connector(isDictionnary=True)
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

@app.post("/create_customer")
async def create_customer(customer:UserBase):
    db_connection, db_cursor = call_connector()
    customer_data = [(customer.name, customer.first_name, str(customer.date_of_birth))]
    add_customer(db_cursor, db_connection, customer_data)
    create_customer_age(db_connection, db_cursor)
    return customer

# Requête pour supprimer un client dans la base de données

@app.delete("/delete_customer")
def delete_customer(customer:UserBase):
    db_connection, db_cursor = call_connector()
    query = """ DELETE FROM customer WHERE name = '%s' AND first_name = '%s' AND date_of_birth = '%s'"""
    db_cursor.execute(query % (customer.name, customer.first_name, customer.date_of_birth))
    db_connection.commit()
    return customer

# Requête pour modifier un client dans la base de données

@app.put("/modify_customer")
def modify_customer(customer:Customer):
    db_connection, db_cursor = call_connector()
    query = """ UPDATE customer SET name = '%s', first_name = '%s', date_of_birth='%s' WHERE id_customer = '%d'"""
    db_cursor.execute(query%(customer.name, customer.first_name, customer.date_of_birth, customer.id_customer))
    db_connection.commit()
    create_customer_age(db_connection, db_cursor)
    return {"new_name" : customer.name, "new_first_name" : customer.first_name, "new_date_of_birth" : customer.date_of_birth}

# Requête pour lister tous les clients et les informations sur eux

@app.get("/get_client_infos")
def get_client_infos():
    db_connection, db_cursor = call_connector(isDictionnary=True)
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
def get_text_infos(text : TextBase):
    db_connection, db_cursor = call_connector(isDictionnary=True)
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

@app.get("/get_average_feeling_wheel_client")
def get_average_feeling_wheel_client(text:TextBase):
    db_connection, db_cursor = call_connector(isDictionnary=True)
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

@app.get("/get_average_feeling_wheel_clients")
def get_average_feeling_wheel_clients(text:TextBase):
    db_connection, db_cursor = call_connector(isDictionnary=True)
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
    create_coaching_database()
    create_customer_if_not_exists()
    create_text_if_not_exists()
    uvicorn.run(app, host="127.0.0.1", port=8000)
