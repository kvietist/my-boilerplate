from fastapi import FastAPI
from routers import users, auth, diaries
app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(diaries.router)

@app.get("/")
async def home():
    return {"message": "api is online and ready for requests"}
    