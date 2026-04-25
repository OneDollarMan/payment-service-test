from fastapi import FastAPI
from src.web import payment_router


app = FastAPI()
app.include_router(payment_router)