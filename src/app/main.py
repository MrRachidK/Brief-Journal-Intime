import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
import streamlit as st
import datetime
from src.config import user, passwd
from src.utils.create_database import add_customer, customer_age, IntegrityError
from src.utils.functions import *
  
db_connection, db_cursor = call_connector()

name = st.text_input('Your name')
st.write('Here is the name you have entered :', name)

first_name = st.text_input('Your first name')
st.write('Here is the first name you have entered :', first_name)

date_of_birth = st.date_input('Your date of birth', value = None, min_value = datetime.date(1900, 1, 1))
st.write('Here is the date of birth you have entered :', date_of_birth)

customer_data = [(name, first_name, date_of_birth)]

submit_button = st.button("Submit")

if submit_button:
  try :
    db_cursor.executemany(add_customer, customer_data)
  except IntegrityError :
    st.write("Vous n\'avons pas pu vous enregistrer car vous existez déjà dans la base de données")
  db_cursor.execute(customer_age)

db_connection.commit()