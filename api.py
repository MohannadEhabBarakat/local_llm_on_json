from typing import Union
from fastapi import FastAPI
try:from data_cleaning import *
except: from .data_cleaning import *
try:from logic import answer
except: from .logic import answer

app = FastAPI()
sortable_data, summarization_data = data_load()


@app.get("/{question}")
def read_root(question:str):
    return answer(question, sortable_data, summarization_data)


@app.get("/")
def update_data():
    return data_prep("data.json")