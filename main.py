from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import models
from database import engine
from routers import users, auth, diaries

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(diaries.router)
app.include_router(diaries.miniapp_router)
app.mount("/app", StaticFiles(directory="Blog-app", html=True), name="miniapp-ui")

@app.get("/")
async def home():
    return {"Api is working"}
    


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)