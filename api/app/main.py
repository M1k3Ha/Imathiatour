from fastapi import FastAPI
from .models import AboutMember
from .data import TEAM_MEMBERS

app = FastAPI(
    title="Imathiatour API",
    version="1.0.0"
)

@app.get("/about", response_model=list[AboutMember])
def about():
    return TEAM_MEMBERS
