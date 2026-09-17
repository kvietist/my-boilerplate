import os

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


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}
    


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "https://my-boilerplate-production.up.railway.app",
        "https://blog-app-rose-rho.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )