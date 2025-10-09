# D:\...\backend\app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, menu, restaurants  # matches your filenames

app = FastAPI(title="AIF MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

# mount routers
app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(menu.router)
