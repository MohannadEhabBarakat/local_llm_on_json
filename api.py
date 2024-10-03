from typing import Union
from fastapi import FastAPI
from data_cleaning import *
from logic import answer

app = FastAPI()
sortable_data, summarization_data = data_load()


@app.get("/{question}")
def read_root(question:str):
    return answer(question, sortable_data, summarization_data)
