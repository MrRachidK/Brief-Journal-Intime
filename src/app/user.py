import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
import streamlit as st
import requests
from datetime import date
from mysql.connector.errors import IntegrityError
from src.utils.functions import call_connector, get_formatted_date
import locale 
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

d = date.today()

menu = st.sidebar.radio("Que souhaitez-vous faire ?", ("Ajouter un nouveau texte", "Modifier un texte", "Lire un texte à la date du jour ou aux autres dates"))

st.subheader("Aujourd'hui, nous sommes le {0:%d} {0:%B} {0:%Y}.".format(d))

if menu == "Ajouter un nouveau texte":
    db_connection, db_cursor = call_connector()
    url = 'http://localhost:8000/create_text'

    user_data = {}

    st.write("Veuillez renseigner votre ID")
    user_data['id_customer'] = st.text_input("Id de l'utilisateur")

    st.write("Veuillez renseigner votre texte")
    user_data['text'] = st.text_input("Votre texte")

    st.write("Veuillez renseigner la date du jour")
    user_data['text_date'] = st.date_input('Date du jour', value = None, min_value = date(1900, 1, 1))
    user_data['text_date'] = str(user_data['text_date'])

    submit_button = st.button("Soumettre")

    if submit_button:
        try :
            response = requests.post(url, json = user_data)
            st.write("Votre ID : {}".format(user_data['id_customer']))
            st.write("Votre texte : {}".format(user_data['text']))
            st.write("Date d'entrée du texte : {}".format(get_formatted_date(user_data['text_date'], False)))
        except IntegrityError :
            st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
        except requests.ConnectionError as error:
            print(error)
    
elif menu == "Modifier un texte":
    db_connection, db_cursor = call_connector()
    url = 'http://localhost:8000/modify_text'

    user_data = {}

    st.write("Veuillez renseigner votre ID")
    user_data['id_customer'] = st.text_input("Id de l'utilisateur")

    st.write("Veuillez renseigner la date à laquelle vous avez entré votre texte")
    user_data['text_date'] = st.date_input('Date du texte', value = None, min_value = date(1900, 1, 1))
    user_data['text_date'] = str(user_data['text_date'])

    st.write("Veuillez renseigner votre nouveau texte")
    user_data['text'] = st.text_input("Votre texte")

    submit_button = st.button("Soumettre")

    if submit_button:
        try :
            response = requests.put(url, json = user_data)
            st.write("Votre ID : {}".format(user_data['id_customer']))
            st.write("Votre nouveau texte : {}".format(user_data['text']))
            st.write("Date d'entrée du texte : {}".format(get_formatted_date(user_data['text_date'], False)))
        except IntegrityError :
            st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
        except requests.ConnectionError as error:
            print(error)
    
else :
    db_connection, db_cursor = call_connector()
    url = 'http://localhost:8000/get_text'

    user_data = {}

    st.write("Voulez-vous consulter un texte à une date précise ? (Y pour Oui / N pour Non)")
    answer = st.text_input("Votre réponse")

    submit_button = st.button("Soumettre", key="1")

    if answer.lower() == "y":
        st.write("Veuillez renseigner votre ID")
        user_data['id_customer'] = st.text_input("Id de l'utilisateur")

        st.write("Veuillez renseigner une date")
        user_data['text_date'] = st.date_input('Date souhaitée', value = None, min_value = date(1900, 1, 1))
        user_data['text_date'] = str(user_data['text_date'])

        first_submit_button = st.button("Soumettre", key="2")

        if first_submit_button:

            try :
                response = requests.get(url, json = user_data)
                response = response.json()
                st.write("Votre ID : {}".format(user_data['id_customer']))
                st.write("Date entrée du texte : {}".format(get_formatted_date(user_data['text_date'], False)))
                st.write("Votre texte : {}".format(response["0"]['text']))
            except IntegrityError :
                st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
            except requests.ConnectionError as error:
                print(error)
    
    elif answer.lower() == "n" :
        st.write("Veuillez renseigner votre ID")
        user_data['id_customer'] = st.text_input("Id de l'utilisateur")

        second_submit_button = st.button("Soumettre", key="3")

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
                    st.write("Date entrée du texte : {}".format(get_formatted_date(response[key]["text_date"], False)))
                    st.markdown("_________")
            except IntegrityError :
                st.write("Nous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
            except requests.ConnectionError as error:
                print(error)