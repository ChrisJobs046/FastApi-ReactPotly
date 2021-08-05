from typing import List
import databases
#import psycopg2
import sqlalchemy
from pydantic import BaseModel
import os
import urllib
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import create_engine



host_server = os.environ.get('host_server', 'localhost')
db_server_port = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
database_name = os.environ.get('database_name', 'Prueba')
db_username = urllib.parse.quote_plus(str(os.environ.get('db_username', 'postgres')))
db_password = urllib.parse.quote_plus(str(os.environ.get('db_password', 'Chris998756725')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))
#DATABASE_URL = "postgresql://postgres:Chris998756725@postgresserver/Prueba"

DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)

metadata = sqlalchemy.MetaData()

notes = sqlalchemy.Table(

    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("completed", sqlalchemy.Boolean),
)

engine = create_engine(

    DATABASE_URL, pool_size=3, max_overflow=0
)

metadata.create_all(engine)

class NoteIn(BaseModel):
    text: str
    completed: bool

class Note(BaseModel):
    id: int
    text: str
    completed: bool

app = FastAPI(title="Rest Api using FastApi PostgreSQL Async EndPoints")
app.add_middleware(
    CORSMiddleware,
    #allow_origins=["client-facing-example-app.com", "localhost:5000"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

db = databases.Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

app.post("/notes/", response_model=Note, status_code = status.HTTP_201_CREATED)
async def create_note(note: NoteIn):
    query = notes.insert().values(text = note.text, completed = note.completed)
    last_record_id = await db.execute(query)
    return {
        **note.dict(), "id": last_record_id
    }

app.put("/notes/{note_id}/", response_model=Note, status_code = status.HTTP_200_OK)
async def update_note(note_id: int, payload: NoteIn):
    query = notes.update().where(notes.c.id == note_id).values(text = payload.text, completed = payload.completed)
    await db.execute(query)
    return {
        **payload.dict(), "id": note_id
    }
