import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
import streamlit as st
import requests
import datetime
from src.config import user, passwd
from src.utils.create_database import add_customer, customer_age, IntegrityError
from src.utils.functions import *

menu = st.sidebar.radio("Que souhaitez-vous faire ?", ("Ajouter un nouveau texte", "Modifier un texte", "Lire un texte à la date du jour ou aux autres dates"))

if menu == "Ajouter un nouveau texte":
    db_connection, db_cursor = call_connector()
    url = 'http://localhost:8000/create_text'

    user_data = {}

    st.write("Veuillez renseigner votre ID")
    user_data['id_customer'] = st.text_input("Id de l'utilisateur")

    st.write("Veuillez renseigner votre texte")
    user_data['text'] = st.text_input("Votre texte")

    st.write("Veuillez renseigner la date du jour")
    user_data['text_date'] = st.text_input("Date du jour")

    submit_button = st.button("Submit")

    if submit_button:
        try :
            response = requests.post(url, json = user_data)
            st.write("Votre ID : {}".format(user_data['id_customer']))
            st.write("Votre texte : {}".format(user_data['text']))
            st.write("Date d'entrée du texte : {}".format(user_data['text_date']))
        except IntegrityError :
            st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
        except requests.ConnectionError as error:
            print(error)
    
    db_connection.commit()

elif menu == "Modifier un texte":
    db_connection, db_cursor = call_connector()
    url = 'http://localhost:8000/modify_text'

    user_data = {}

    st.write("Veuillez renseigner votre ID")
    user_data['id_customer'] = st.text_input("Id de l'utilisateur")

    st.write("Veuillez renseigner la date à laquelle vous avez entré votre texte")
    user_data['text_date'] = st.text_input("Date du jour")

    st.write("Veuillez renseigner votre nouveau texte")
    user_data['text'] = st.text_input("Votre texte")

    submit_button = st.button("Submit")

    if submit_button:
        try :
            response = requests.put(url, json = user_data)
            st.write("Votre ID : {}".format(user_data['id_customer']))
            st.write("Votre nouveau texte : {}".format(user_data['text']))
            st.write("Date d'entrée du texte : {}".format(user_data['text_date']))
        except IntegrityError :
            st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
        except requests.ConnectionError as error:
            print(error)
    
    db_connection.commit()

else :
    db_connection, db_cursor = call_connector()
    url = 'http://localhost:8000/get_text'

    user_data = {}

    st.write("Voulez-vous consulter un texte à une date précise ? (Y pour Oui / N pour Non)")
    answer = st.text_input("Votre réponse")

    submit_button = st.button("Submit", key="1")

    if answer.lower() == "y":
        st.write("Veuillez renseigner votre ID")
        user_data['id_customer'] = st.text_input("Id de l'utilisateur")

        st.write("Veuillez renseigner une date")
        user_data['text_date'] = st.text_input("Date souhaitée")

        first_submit_button = st.button("Submit", key="2")

        if first_submit_button:

            try :
                response = requests.get(url, json = user_data)
                response = response.json()
                st.write("Votre ID : {}".format(user_data['id_customer']))
                st.write("Date entrée du texte : {}".format(user_data['text_date']))
                st.write("Votre texte : {}".format(response["0"]['text']))
            except IntegrityError :
                st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
            except requests.ConnectionError as error:
                print(error)
    
    elif answer.lower() == "n" :
        st.write("Veuillez renseigner votre ID")
        user_data['id_customer'] = st.text_input("Id de l'utilisateur")

        second_submit_button = st.button("Submit", key="3")

        if second_submit_button:

            try :
                response = requests.get(url, json = user_data)
                response = response.json()
                st.header("Votre ID : {}".format(user_data['id_customer']))
                st.subheader("Voici tous vos textes :")
                st.markdown("_________")
                for key in response:
                    st.write("Texte numéro {}".format(int(key) + 1))
                    st.write("Texte : {}".format(response[key]["text"]))
                    st.write("Date entrée du texte : {}".format(response[key]["text_date"]))
                    st.markdown("_________")
            except IntegrityError :
                st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
            except requests.ConnectionError as error:
                print(error)
        
    
    db_connection.commit()

