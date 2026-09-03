from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Customer(BaseModel):
    id: str
    name: str
    email: str
    last_purchase_date: Optional[str] = None
    preferred_category: Optional[str] = None

class EmailDraft(BaseModel):
    customer_id: str
    subject: str
    body: str
