# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import the new routers
from app.routers import auth, restaurants, categories, items, variations, menu

app = FastAPI(title="AIF MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

# mount all routers
app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(variations.router)
app.include_router(menu.router) 