import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
import mysql.connector
import datetime
import random
import re
from src.config import user, passwd

def call_connector():
    """ Function which connects to MySQL """
    db_connection = mysql.connector.connect(
    host="localhost",
    user=user,
    passwd = passwd,
    database="coaching")

    db_cursor = db_connection.cursor(buffered=True, dictionary=False)
    return db_connection, db_cursor

def insert_random_date():
    """ Function which insert random dates """
    start_date = datetime.date(2010, 1, 1)
    end_date = datetime.date(2021, 1, 1)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    
    return random_date

def preprocessor(text):
    """ Function which preprocesses a string """
    text = re.sub('<[^>]*>', '', text) # Effectively removes HTML markup tags
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text)
    text = re.sub('[\W]+', ' ', text.lower()) + ' '.join(emoticons).replace('-', '')
    return text

def predict_emotion(message, vectorizer, model):
    """ Function which predicts an emotion according to a model """
    emotions = ['émotion négative', 'émotion positive']
    preprocessed_message = preprocessor(message)
    vectorized_message = vectorizer.transform([preprocessed_message])
    emotion = model[0].predict(vectorized_message)
    proba_emotion = model[0].predict_proba(vectorized_message)
    return emotions[int(emotion)], proba_emotion

def get_formatted_date(date, isCapitalized = True):
    date_to_datetime = datetime.datetime.strptime(date, '%Y-%m-%d')
    datetime_to_string = date_to_datetime.strftime("%A %d %B %Y")
    if isCapitalized:
        formatted_date = datetime_to_string.capitalize()
    else :
        formatted_date = datetime_to_string
    return formatted_date