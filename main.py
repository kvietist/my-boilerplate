from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, auth, diaries
app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(diaries.router)

@app.get("/")
async def home():
    return {"message": "api is online and ready for requests"}
    


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)