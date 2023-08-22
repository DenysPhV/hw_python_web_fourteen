import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.connector import get_db
from src.routes import contacts, notes, auth, users
from src.conf.config import settings

app = FastAPI()


@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    return r


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def root():
    return {"message": "Welcome to FastAPI homework!"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(contacts.router, prefix='/api')
app.include_router(contacts.finder, prefix='/api')
app.include_router(notes.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')

app.add_middleware(CORSMiddleware,
                   allow_origins=[settings.origins],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )

app.mount("/static", StaticFiles(directory="src/static"), name="static")

if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", reload=True, log_level="info")
