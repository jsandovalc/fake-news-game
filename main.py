import sqlalchemy as sa
import databases
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


DATABASE_URL = "sqlite:///./quizzes.db"
database = databases.Database(DATABASE_URL)


app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


metadata = sa.MetaData()

elements = sa.Table(
    "elements",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("image", sa.String),
    sa.Column("description", sa.Text),
    sa.Column("truth", sa.Boolean),
)

engine = sa.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


class Element(BaseModel):
    id: int
    image: str
    description: str
    truth: bool


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def index(request: Request):
    query = elements.select()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "quiz_element": await database.fetch_one(query)},
    )
