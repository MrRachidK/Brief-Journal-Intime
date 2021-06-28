from pydantic import BaseModel
from typing import Optional
import datetime

class Text(BaseModel):
    id_customer:int
    text_date : Optional[datetime.date] = None
    text:str

class Customer(BaseModel):
    name:str
    first_name:str
    date_of_birth:datetime.date