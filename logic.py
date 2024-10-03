"""
This file contains the logic for extracting information from the data files.

Functions (ideas not actual functions):
    extract_data takes the prompt1 output (see in logicNotes.txt) calls either summarization_extract_data or sortable_extract_data depending on the task.
    summarization_extract_data takes a list of one key and a list of counties. Return relative data
    sortable_extract_data takes a list of one or more keys and a list of counties. Format the data in a way that it can be sorted. return a list of dictionaries with the keys being the counties and the values being the data for that county. 

    answer:
        1- Use model to get extract keys
        2- Use logic to extract data
        3- Use model to format the data
"""

from typing import Dict, List, Tuple
from .model import *

def extract_data(response:Dict, data:Dict) -> Dict:

    task = response["task"]
    if task == "summarization":
        return summarization_extract_data(response["key"], response["counties"], data)
    else:
        sub_key = response["subkey"] if "subkey" in response else None  
        return sortable_extract_data(task, response["key"], response["counties"], response["max_counties"], data, sub_key) 
    
def summarization_extract_data(key:str, counties:List[str], data:Dict) -> Dict:
    """
    Extracts the data for the summarization task.

    Args:
        key (str): A key extract from the data.
        counties (list): A list of counties to extract data for.

    Returns:
        list: A list of dictionaries containing the extracted data.
    """
    extracted_data = {}
    counties = counties if counties[0] != "all" else list(data)
    for county in counties:
        extracted_data[county] = data[county][key]

    countries = list(extracted_data.keys())

    return {"countries": countries, "evedance": extracted_data}

def sortable_extract_data(task:str, key:str, counties:List[str], max_counties:int, data:Dict, subkey:str=None) -> Dict:
    """
    Extracts the data for the sortable task.

    Args:
        keys (str): A list of keys to extract from the data.
        counties (list): A list of counties to extract data for.
        max_counties (int): The maximum number of counties to return.

    Returns:
        list: A list of dictionaries containing the extracted data.
    """
    extracted_data = {}
    counties = counties if counties[0] != "all" else list(data)
    for county in counties:
        info = data[county]
        info = info[key]
        if subkey: info = info[subkey]
        if type(info) == dict:
            info = sum(info.values())
        extracted_data[county] = info

    if task == "list_accending":
        countries  = sorted(extracted_data.items(), key=lambda x: x[1])
    elif task == "list_decending":
        countries  = sorted(extracted_data.items(), key=lambda x: x[1], reverse=True)
    else:
        countries  = list(extracted_data.keys())
    
    countries = countries[:max_counties]

    evedance = [(country, extract_data[country]) for country in countries]

    return {"countries": countries, "evedance": evedance}


def format_data(extracted_data:Dict, task:str, question:str) -> Dict:
    if task == "summarization":
        return summarization_format_data(extracted_data, question)
    else:
        return sortable_format_data(extracted_data, question)
    
def summarization_format_data(extracted_data:Dict, question:str) -> Dict:
    countries, evedance = extracted_data["countries"], extracted_data["evedance"]

    for country in countries:
        if evedance[country] == None:
            


def sortable_format_data(extracted_data:Dict, question:str) -> Dict:
    pass

def answer(question:str, data:Dict) -> Dict:
    response = route(question)
    extracted_data = extract_data(response, data)
    return format_data(extracted_data, response["task"], question)