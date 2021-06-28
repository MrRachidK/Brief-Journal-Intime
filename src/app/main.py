import sys
import json
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
import streamlit as st
import requests
import datetime
from src.config import user, passwd
from src.utils.create_database import add_customer, customer_age, IntegrityError
from src.utils.functions import *

menu = st.sidebar.radio("Que souhaitez-vous faire ?", ("Créer un utilisateur", "Supprimer un utilisateur"))

# Création d'un client

if menu == "Créer un utilisateur" :
  db_connection, db_cursor = call_connector()
  url = 'http://localhost:8000/create_customer'
  
  user = {}

  user['name'] = st.text_input('Votre nom')

  st.write('Voici le nom que vous avez entré :', user['name'])

  user['first_name'] = st.text_input('Votre prénom')
  st.write('Voici le prénom que vous avez entré :', user['first_name'])

  user['date_of_birth'] = st.date_input('Votre date de naissance', value = None, min_value = datetime.date(1900, 1, 1))
  user['date_of_birth'] = str(user['date_of_birth'])
  st.write('Voici la date de naissance que vous avez entré :', user['date_of_birth'])

  customer_data = [(user['name'], user['first_name'], user['date_of_birth'])]

  submit_button = st.button("Submit")

  if submit_button:
    try :
      response = requests.post(url, json = user)
    except IntegrityError :
      st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
    except requests.ConnectionError as error:
      print(error)
    db_cursor.execute(customer_age)

  db_connection.commit()

elif menu == "Supprimer un utilisateur":
  db_connection, db_cursor = call_connector()
  url = 'http://localhost:8000/delete_customer'

  user = {}

  st.write("Renseignez le nom de l'utilisateur que vous souhaitez retirer")
  user['deleted_name'] = st.text_input("Nom de l'utilisateur")

  st.write("Renseignez le prénom de l'utilisateur que vous souhaitez retirer")
  user['deleted_first_name'] = st.text_input("Prénom de l'utilisateur")

  submit_button = st.button("Submit")

  if submit_button:
    response = requests.delete(url, json = user)
  db_connection.commit()