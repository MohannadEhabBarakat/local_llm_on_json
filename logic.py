"""
This file contains the logic for extracting information from the data files.

Functions (ideas not actual functions):
    extract_data takes the prompt1 output (see in logicNotes.txt) calls either summarization_extract_data or sortable_extract_data depending on the task.
    summarization_extract_data takes a list of one key and a list of countries. Return relative data
    sortable_extract_data takes a list of one or more keys and a list of countries. Format the data in a way that it can be sorted. return a list of dictionaries with the keys being the countries and the values being the data for that county. 

    answer:
        1- Use model to get extract keys
        2- Use logic to extract data
        3- Use model to format the data
"""

from typing import Dict, List, Tuple
try: from model import answerLLM, route
except: from .model import answerLLM, route

def extract_data(response:Dict, sortable_data:Dict, summarization_data:Dict) -> Dict:

    task = response["task"]
    if response['key'] in ["outStandings", "trips", "talkingPoints"]:
        task = "summarization"
        response["task"] = "summarization"
    else:
        if response["task"] == "summarization":
            task = "list_accending"
            response["task"] = "list_accending"
            response["max_countries"] = 1 if "max_countries" not in response else response["max_countries"]
        if "max_countries" not in response:
            response["max_countries"] = 10

    if task == "summarization":
        return summarization_extract_data(response["key"], response["countries"], summarization_data)
    else:
        sub_key = response["subkey"] if "subkey" in response else None  
        # sub_key = None  
        return sortable_extract_data(task, response["key"], response["countries"], response["max_countries"], sortable_data, sub_key) 
    
def summarization_extract_data(key:str, countries:List[str], data:Dict) -> Dict:
    """
    Extracts the data for the summarization task.

    Args:
        key (str): A key extract from the data.
        countries (list): A list of countries to extract data for.

    Returns:
        list: A list of dictionaries containing the extracted data.
    """
    extracted_data = {}
    countries = countries if countries[0] != "all" else list(data)
    for county in countries:
        extracted_data[county] = data[county][key]

    countries = list(extracted_data.keys())

    return {"countries": countries, "evedance": extracted_data}

def sortable_extract_data(task:str, key:str, countries:List[str], max_countries:int, data:Dict, subkey:str=None) -> Dict:
    """
    Extracts the data for the sortable task.

    Args:
        keys (str): A list of keys to extract from the data.
        countries (list): A list of countries to extract data for.
        max_countries (int): The maximum number of countries to return.

    Returns:
        list: A list of dictionaries containing the extracted data.
    """
    extracted_data = {}
    if countries[0] != "all" and countries != "all":
        countries = countries   
    else:
        countries =  list(data)

    for county in countries:
        info = data[county]
        info = info[key]
        if subkey: info = info[subkey]
        if type(info) == dict:
            info = sum(info.values())
        extracted_data[county] = info

    if task == "list_accending":
        evedance  = sorted(extracted_data.items(), key=lambda x: x[1])
    elif task == "list_decending":
        print("list_decending")
        evedance  = sorted(extracted_data.items(), key=lambda x: x[1], reverse=True)
    else:
        print("list_unordered")
        countries  = list(extracted_data.keys())
        evedance = list(extracted_data.items())
    if max_countries != -1:
        evedance = evedance[:max_countries]
        countries = [country for country,_ in evedance]

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
            evedance.pop(country)
    
    ans = answerLLM(question, evedance)
    return {"answer":ans, "countries": list(evedance.keys()), "evedance": evedance}


def sortable_format_data(extracted_data:Dict, question:str) -> Dict:
    return extracted_data

def answer(question:str, sortable_data:Dict, summarization_data:Dict) -> Dict:
    for i in range(5):
        try: 
            response = route(question)
            break
        except Exception as e:
            print("retrying because of error", e)

    # response = '''
    # {
    #     "countries": ["all"],
    #     "task": "summarization",
    #     "key": "outStandings"
    # }
    # '''

    # response = json.loads(response)
    print("response", response)
    extracted_data = extract_data(response, sortable_data, summarization_data)
    print("extracted_data", extracted_data)
    return format_data(extracted_data, response["task"], question)


if __name__ == "__main__":
    from data_cleaning import *
    sortable_data, summarization_data = data_load()
    question = ""
    print(answer(question, sortable_data, summarization_data))