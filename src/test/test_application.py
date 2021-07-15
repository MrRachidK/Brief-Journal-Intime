import sys
sys.path.insert(0, "/home/apprenant/Documents/Brief-Journal-Intime/")
from src.utils.create_database import create_database, create_customer_if_not_exists, create_text_if_not_exists, add_unique_customer, delete_database

import warnings
from fastapi.testclient import TestClient
from src.utils.api import app

def fxn():
    warnings.warn("deprecated", DeprecationWarning)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()

client = TestClient(app)

delete_database("coaching_test")
create_database("coaching_test")
create_customer_if_not_exists("coaching_test")
add_unique_customer("coaching_test")
create_text_if_not_exists("coaching_test")

# we test if the API works and the get operation sends the good result

# CRUD customer : Create a customer
def test_create_customer():
  json={
  "name": "Vasseur",
  "first_name": "Leïla",
  "date_of_birth": "1994-11-28"
}
  response = client.post("/create_customer/coaching_test", json=json)
  assert response.status_code == 200
  data = response.json()
  assert data == {
  "name": "Vasseur",
  "first_name": "Leïla",
  "date_of_birth": "1994-11-28"
}

# CRUD customer : Read (Get) a customer
def test_get_client_infos():
  response = client.get("/get_client_infos/coaching_test")
  assert response.status_code == 200
  data = response.json()
  assert data["1"]['name'] == "Vasseur"
 
# CRUD customer : Update (Modify) a customer
def test_modify_customer():
  json={
  "name": "Potter",
  "first_name": "Harry",
  "date_of_birth": "1991-07-31",
  "id_customer" : 1
}
  response = client.put("/modify_customer/coaching_test", json=json)
  assert response.status_code == 200
  data = response.json()
  assert data == {"new_name" : "Potter", "new_first_name" : "Harry", "new_date_of_birth" : "1991-07-31"}


# def test_create_customer_error():
#   json={
#   "name": "Potter",
#   "first_name": "Harry",
#   "date_of_birth": "1991-07-31"
# }
  
#   with pytest.raises(IntegrityError):   
#     response = client.post("/create_customer/coaching_test", json=json)
#     assert response.status_code == 422
#     data = response.json()
#     assert data == {
#   "name": "Potter",
#   "first_name": "Harry",
#   "date_of_birth": "1991-07-31"
# }
  

# def test_create_text():
#     response = client.post(
#         "/create_text/coaching_test",
#         json={"id_customer" : 1, "text_date" : "2021-07-08", "text" : "string"},
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data == {
#   "id_customer": 1,
#   "text_date": "2021-07-08",
#   "text": "string",
#   "text_first_emotion": "émotion négative",
#   "proba_negative_emotion": 63.7848,
#   "proba_positive_emotion": 36.2152
# }

# def test_modify_text():
#     response = client.put("/modify_text/coaching_test", json = {"id_customer" : 1, "text_date" : "2021-07-08", "text" : "string_to_modify"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data == {
#   "id_customer": 1,
#   "text_date": "2021-07-08",
#   "new_text": "string_to_modify",
#   "text_first_emotion": "émotion négative",
#   "proba_negative_emotion": 64.4444,
#   "proba_positive_emotion": 35.5556
# }

# def test_get_text():
#     response = client.get("/get_text", json = {"id_customer" : 1, "text_date" : "2021-07-08"})
#     assert response.status_code == 200

# CRUD customer : Delete a customer
def test_delete_customer():
    json={
    "name": "Potter",
    "first_name": "Harry",
    "date_of_birth": "1991-07-31"
  }
    response = client.delete("/delete_customer/coaching_test", json=json)
    assert response.status_code == 200

