from pydantic import BaseModel, EmailStr
from typing import List

class NotificationRequest(BaseModel):
    to_emails: List[EmailStr]
    subject: str
    body_html: str 