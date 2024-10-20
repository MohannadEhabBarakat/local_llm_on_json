from typing import Union
from fastapi import FastAPI, File, UploadFile
try:from data_cleaning import *
except: from .data_cleaning import *
try:from logic import answer
except: from .logic import answer
from pydantic import BaseModel
import json
import ast

app = FastAPI()

class Data(BaseModel):
    data: dict

@app.get("/")
def read_root(question:str):
    sortable_data, summarization_data = data_load()

    return answer(question, sortable_data, summarization_data)


@app.post("/update_json")
def update_json(data:Data):
    
    with open("data.json", "w") as f:
        json.dump(data.data, f)

    return data_prep("data.json")


@app.post("/update_file")
def update_file(file: UploadFile):
    # print(json.loads(file.file.read().decode("utf-8")).keys())
    with open("data.json", "w") as f:
        json.dump(json.loads(file.file.read().decode("utf-8")), f)
    
    return data_prep("data.json")