from pydantic import BaseModel
from typing import Optional
import datetime

class TextBase(BaseModel):
    id_customer:Optional[int] = None
    text_date:Optional[datetime.date] = None
    date_start:Optional[datetime.date] = None
    date_end:Optional[datetime.date] = None
    
class Text(TextBase):
    text:Optional[str] = None

class UserBase(BaseModel):
    name:str
    first_name:str
    date_of_birth:datetime.date

class Customer(UserBase):
    id_customer:int
