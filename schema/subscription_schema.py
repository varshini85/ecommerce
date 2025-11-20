from pydantic import BaseModel, EmailStr

class SubscriptionCreate(BaseModel):
    email: EmailStr


