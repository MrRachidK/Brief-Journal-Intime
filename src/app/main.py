import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
import streamlit as st
import requests
from datetime import date
from src.utils.create_database import create_customer_age
from mysql.connector.errors import IntegrityError
from src.utils.functions import call_connector, get_formatted_date
import locale 
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

menu = st.sidebar.radio("Que souhaitez-vous faire ?", ("Créer un utilisateur", "Modifier un utilisateur", "Supprimer un utilisateur", "Lister tous les clients et les informations sur eux", "Afficher le texte d'un utilisateur et ses infos à une date précise", "Obtenir la roue des sentiments moyenne d'un client sur une période donnée", "Obtenir la roue des sentiments moyenne de tous les clients sur une période donnée"))

# Création d'un client

if menu == "Créer un utilisateur" :
  db_connection, db_cursor = call_connector("coaching")
  url = 'http://localhost:8000/create_customer/coaching'
  
  user_data = {}

  user_data['name'] = st.text_input('Votre nom')
  st.write('Voici le nom que vous avez entré :', user_data['name'])

  user_data['first_name'] = st.text_input('Votre prénom')
  st.write('Voici le prénom que vous avez entré :', user_data['first_name'])

  user_data['date_of_birth'] = st.date_input('Votre date de naissance', value = None, min_value = date(1900, 1, 1))
  user_data['date_of_birth'] = str(user_data['date_of_birth'])
  formatted_date = get_formatted_date(user_data['date_of_birth'], False)
  st.write('Voici la date de naissance que vous avez entré :', formatted_date)
  
  customer_data = [(user_data['name'], user_data['first_name'], user_data['date_of_birth'])]

  submit_button = st.button("Soumettre")

  if submit_button:
    try :
      response = requests.post(url, json = user_data)
      response = response.json()
      st.write("Bravo ! Vous avez réussi à créer le client suivant :")
      st.write("Nom : {}".format(response["name"]))
      st.write("Prénom : {}".format(response["first_name"]))
      st.write("Date de naissance : {}".format(get_formatted_date(response["date_of_birth"], False)))
    except :
      st.write("Nous n\'avons pas pu enregistrer ces informations car le client existe déjà dans la base de données")
    create_customer_age(db_connection, db_cursor, "coaching")

elif menu == "Modifier un utilisateur":
  db_connection, db_cursor = call_connector("coaching")
  url = 'http://localhost:8000/modify_customer/coaching'

  user_data = {}

  st.write("Renseignez le nouveau nom que vous voulez entrer")
  user_data['name'] = st.text_input("Nouveau nom de l'utilisateur")

  st.write("Renseignez le nouveau prénom que vous voulez entrer")
  user_data['first_name'] = st.text_input("Nouveau prénom de l'utilisateur")

  st.write("Renseignez la nouvelle date de naissance que vous voulez entrer")
  user_data['date_of_birth'] = st.date_input("Nouvelle date de naissance de l'utilisateur", value = None, min_value = date(1900, 1, 1))
  user_data['date_of_birth'] = str(user_data['date_of_birth'])
  formatted_date = get_formatted_date(user_data['date_of_birth'])

  st.write("Renseignez l'id de l'utilisateur que vous souhaitez modifier")
  user_data['id_customer'] = st.text_input("Id de l'utilisateur")

  submit_button = st.button("Soumettre")
  
  if submit_button:
    response = requests.put(url, json = user_data)
    response = response.json()
    st.write("Vous avez modifié avec succès le client numéro {}. Voici ses données actualisées :".format(user_data['id_customer']))
    st.write("Nom : {}".format(response['new_name']))
    st.write("Prénom : {}".format(response['new_first_name']))
    st.write("Date de naissance : {}".format(get_formatted_date(response['new_date_of_birth'], False)))

elif menu == "Supprimer un utilisateur":
  db_connection, db_cursor = call_connector("coaching")
  url = 'http://localhost:8000/delete_customer/coaching'

  user_data = {}

  st.write("Renseignez le nom de l'utilisateur que vous souhaitez retirer")
  user_data['name'] = st.text_input("Nom de l'utilisateur")

  st.write("Renseignez le prénom de l'utilisateur que vous souhaitez retirer")
  user_data['first_name'] = st.text_input("Prénom de l'utilisateur")

  st.write("Renseignez la date de naissance de l'utilisateur que vous souhaitez retirer")
  user_data['date_of_birth'] = st.date_input("Date de naissance de l'utilisateur", value = None, min_value = date(1900, 1, 1))
  user_data['date_of_birth'] = str(user_data['date_of_birth'])
  formatted_date = get_formatted_date(user_data['date_of_birth'])

  submit_button = st.button("Soumettre")
  
  if submit_button:
    try:
      response = requests.delete(url, json = user_data)
      response = response.json()
      st.write("Suppression du client suivant confirmé :")
      st.write("Nom : {}".format(response['name']))
      st.write("Prénom : {}".format(response['first_name']))
      st.write("Date de naissance : {}".format(get_formatted_date(response['date_of_birth']), False))
    except :
      st.write("Nous n\'avons pas pu supprimer ces informations car le client n'existe pas dans la base de données")

elif menu == "Lister tous les clients et les informations sur eux" :
  db_connection, db_cursor = call_connector("coaching")
  url = 'http://localhost:8000/get_client_infos/coaching'
  response = requests.get(url)
  response = response.json()
  st.title("Liste des différents clients")
  for key in response:
    st.header("Client numéro {}".format(int(key)))
    st.write("Nom : {}".format(response[key]["name"]))
    st.write("Prénom : {}".format(response[key]["first_name"]))
    st.write("Date de naissance : {}".format(get_formatted_date(response[key]["date_of_birth"], False)))
    st.markdown("_________")

elif menu == "Afficher le texte d'un utilisateur et ses infos à une date précise":
  db_connection, db_cursor = call_connector("coaching")
  url = 'http://localhost:8000/get_text_infos/coaching'

  user_data = {}

  st.write("Renseignez l'id de l'utilisateur que vous souhaitez consulter")
  user_data['id_customer'] = st.text_input("Id de l'utilisateur")

  st.write("Renseignez la date du texte entré par l'utilisateur")
  user_data['text_date'] = st.date_input('Date du texte', value = None, min_value = date(1900, 1, 1))
  user_data['text_date'] = str(user_data['text_date'])

  submit_button = st.button("Soumettre")
  
  if submit_button:
    try:
      response = requests.get(url, json = user_data)
      response = response.json()
      st.header("Client numéro {}".format(response["0"]["id_customer"]))
      st.write("Date du texte : {}".format(get_formatted_date(response["0"]["text_date"], False)))
      st.write("Texte : {}".format(response["0"]["text"]))
      st.write("Emotion principale du texte : {}".format(response["0"]["text_first_emotion"]))
      st.write("Probabilité d'une émotion négative : {} %".format(response["0"]["proba_negative_emotion"]))
      st.write("Probabilité d'une émotion positive : {} %".format(response["0"]["proba_positive_emotion"]))
    except KeyError :
      st.write("Aucun texte de cet ID utilisateur n'existe dans la base de données")

elif menu == "Obtenir la roue des sentiments moyenne d'un client sur une période donnée":
  db_connection, db_cursor = call_connector("coaching")
  url = 'http://localhost:8000/get_average_feeling_wheel_client/coaching'

  user_data = {}

  st.write("Renseignez l'id de l'utilisateur que vous souhaitez consulter")
  user_data['id_customer'] = st.text_input("Id de l'utilisateur")

  st.write("Renseignez pour la période la date la plus ancienne")
  user_data['date_start'] = st.date_input('Date la plus ancienne', value = None, min_value = date(1900, 1, 1))
  user_data['date_start'] = str(user_data['date_start'])

  st.write("Renseignez pour la période la date la plus récente")
  user_data['date_end'] = st.date_input('Date la plus récente', value = None, min_value = date(1900, 1, 1))
  user_data['date_end'] = str(user_data['date_end'])

  submit_button = st.button("Soumettre")
  
  if submit_button:
    try:
      response = requests.get(url, json = user_data)
      response = response.json()
      st.header("Client numéro {}".format(user_data['id_customer']))
      st.subheader("Période du {} au {}".format(get_formatted_date(user_data['date_start'], False), get_formatted_date(user_data['date_end'], False)))
      st.write("Nombre de textes sur cette période : {}".format(response["text_numbers"]))
      st.write("Probabilité moyenne d'émotion négative : {} %".format(response["average_negative_emotion"]))
      st.write("Probabilité moyenne d'émotion positive : {} %".format(response["average_positive_emotion"]))
    except :
      st.write("Aucun texte n'est répertorié sur cette période-là")

else :
  db_connection, db_cursor = call_connector("coaching")
  url = 'http://localhost:8000/get_average_feeling_wheel_clients/coaching'

  user_data = {}

  st.write("Renseignez pour la période la date la plus ancienne")
  user_data['date_start'] = st.date_input('Date la plus ancienne', value = None, min_value = date(1900, 1, 1))
  user_data['date_start'] = str(user_data['date_start'])

  st.write("Renseignez pour la période la date la plus récente")
  user_data['date_end'] = st.date_input('Date la plus récente', value = None, min_value = date(1900, 1, 1))
  user_data['date_end'] = str(user_data['date_end'])

  submit_button = st.button("Soumettre")
  
  if submit_button:
    try:
      response = requests.get(url, json = user_data)
      response = response.json()
      st.subheader("Période du {} au {}".format(get_formatted_date(user_data['date_start'], False), get_formatted_date(user_data['date_end'], False)))
      st.write("Nombre de textes sur cette période : {}".format(response["text_numbers"]))
      st.write("Probabilité moyenne d'émotion négative : {} %".format(response["average_negative_emotion"]))
      st.write("Probabilité moyenne d'émotion positive : {} %".format(response["average_positive_emotion"]))
    except IntegrityError :
      st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
    except requests.ConnectionError as error:
      print(error)
