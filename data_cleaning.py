"""
## Data cleaning
- remove the word String ✅
- any "" or '' should be none ✅

- drop any FileAttachmentString key ✅
- drop ginfo for now (ask later) ✅
- drop trips for now (ask later) ✅

- sortable keys are ✅ 
    - ["country", "moi", "defense", "energy", "mofa", "qia", "qffd", "moci"] ✅
- Summary keys are ✅
    - ["talkingPoints", "outStandings", "trips"] ✅
- If a key has a list value that has only one value in it compress it 

"""
import json
from typing import Dict, List, Tuple
import json


def json2dict(file_path: str) -> Dict:
    """
    Converts a JSON file to a Python dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The Python dictionary representation of the JSON data.
    """
    with open(file_path, 'r') as file:
        data: Dict = json.load(file)
    return data

def remove_string(data: Dict) -> Dict:
    """
    Recursively removes the word 'String' from the keys of a nested dictionary.

    Args:
        data (dict): The input dictionary to be processed.

    Returns:
        dict: The processed dictionary with the word 'String' removed from the keys.
    """
    for key in list(data.keys()):
        new_key = key.replace('String', '')
        
        if 'String' in key:
            data[new_key] = data.pop(key)
        
        if type(data[new_key]) == dict:
            data[new_key] = remove_string(data[new_key])
        elif type(data[new_key]) == list:
            for i in range(len(data[new_key])):
                data[new_key][i] = remove_string(data[new_key][i])
    return data

def data_types_standerdize(data: Dict) -> Dict:
    """
    Recursively standardizes the data types in a nested dictionary.

    Args:
        data (dict): The input dictionary to be standardized.

    Returns:
        dict: The standardized dictionary with data types converted.

    """
    for key in data.keys():
        if type(data[key]) == dict:
            data[key] = data_types_standerdize(data[key])
        elif type(data[key]) == list:
            for i in range(len(data[key])):
                data[key][i] = data_types_standerdize(data[key][i])
        elif type(data[key]) == str and data[key].strip() == "":
            data[key] = None
        elif type(data[key]) == str and data[key].replace(".", "").isnumeric():
            data[key] = float(data[key])

    return data


def drop_keys(data: Dict, keys: List[str]) -> Dict:
    """
    Recursively drops the specified keys from a nested dictionary.

    Args:
        data (dict): The input dictionary to be processed.
        keys (list): The list of keys to be dropped.

    Returns:
        dict: The processed dictionary with the specified keys removed.
    """
    for key in keys:
        if key in data:
            data.pop(key)
        for key in data.keys():
            if type(data[key]) == dict:
                data[key] = drop_keys(data[key], keys)
            elif type(data[key]) == list:
                for i in range(len(data[key])):
                    data[key][i] = drop_keys(data[key][i], keys)
    return data


def clean_data(data: Dict) -> Dict:
    """
    Cleans the data by removing the word 'String', standardizing data types, and dropping specified keys.

    Args:
        data (dict): The input dictionary to be cleaned.

    Returns:
        dict: The cleaned dictionary with the word 'String' removed, data types standardized, and specified keys dropped.
    """
    data = remove_string(data)
    data = data_types_standerdize(data)
    data = drop_keys(data, ["FileAttachment", "ginfo"])
    return data


def select_keys(data: Dict, keys: List[str]) -> Dict:
    """
    Selects specific keys from a dictionary of data for each country.

    Args:
        data (Dict): A dictionary containing data for each country.
        keys (List[str]): A list of keys to select for each country.

    Returns:
        Dict: A new dictionary containing only the selected keys for each country.
    """
    new_data = {}
    for country in data.keys():
        new_data[country] = {}
        for key in keys:
            if key in data[country]:
                new_data[country][key] = data[country][key]
            else:
                new_data[country][key] = None

    return new_data

def compress_list_dict_combo(data: Dict) -> Dict:
    new_data = {}
    for country in data.keys():
        new_data[country] = {}
        for key in data[country].keys():
            if key in ["country", "moi", "qffd", "defense"] and data[country][key] is not None:
                new_data[country][key] = data[country][key][0][list(data[country][key][0])[0]]
            else:
                if key in ["outStandings", "talkingPoints", "trips"]:
                    new_data[country][key] = data[country][key] 
                    continue
                new_data[country][key] = data[country][key][0] if data[country][key] is not None else None

    return new_data


def save_json(data: Dict, file_path: str) -> None:
    """
    Saves a dictionary to a JSON file.

    Args:
        data (dict): The dictionary to be saved.
        file_path (str): The path to save the JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def replace_none_with_0(data: Dict) -> Dict:
    """
    Recursively replaces all None values in a dictionary with 0.

    Args:
        data (dict): The input dictionary to be processed.

    Returns:
        dict: The processed dictionary with None values replaced by 0.
    """
    for key in data.keys():
        if type(data[key]) == dict:
            data[key] = replace_none_with_0(data[key])
        elif type(data[key]) == list:
            for i in range(len(data[key])):
                data[key][i] = replace_none_with_0(data[key][i])
        elif data[key] is None:
            data[key] = 0
    return data

def load_sortable_data(file_path: str) -> Dict:
    """
    Loads and cleans the sortable data from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the sortable data.

    Returns:
        dict: The cleaned sortable data.
    """
    data = json2dict(file_path)
    data = clean_data(data)
    data = select_keys(data, ["country", "moi", "defense", "energy", "mofa", "qia", "qffd", "moci"])
    data = compress_list_dict_combo(data)
    return data

def load_summarization(file_path: str) -> Dict:
    """
    Loads and cleans the summarization data from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the summarization data.

    Returns:
        dict: The cleaned summarization data.
    """
    data = json2dict(file_path)
    data = clean_data(data)
    data = select_keys(data, ["talkingPoints", "outStandings", "trips"])
    data = compress_list_dict_combo(data)
    return data

def data_prep(file_path: str) -> None:
    """
    Load data from the specified file path and save it as JSON files.

    Args:
        file_path (str): The path to the data file.

    Returns:
        None
    """
    sortable_data = load_sortable_data(file_path)
    summarization_data = load_summarization(file_path)

    save_json(sortable_data, "sortable_data.json")
    save_json(summarization_data, "summarization_data.json")
    

# -------- Main Functions --------
 
def data_load() -> Tuple[Dict, Dict]:
    """
    Load data from JSON files and return a tuple of dictionaries.

    Returns:
        A tuple containing two dictionaries: sortable_data and summarization_data.
    """
    sortable_data = json2dict("sortable_data.json")
    summarization_data = json2dict("summarization_data.json")
    sortable_data = replace_none_with_0(sortable_data)

    return sortable_data, summarization_data

def sample_data_load() -> Tuple[Dict, Dict]:
    """
    Load sample data from JSON files.

    Returns:
        A tuple containing two dictionaries:
        - sortable_data: The data loaded from "sample_sortable_data.json".
        - summarization_data: The data loaded from "sample_summarization_data.json".
    """
    sortable_data = json2dict("sample_sortable_data.json")
    summarization_data = json2dict("sample_summarization_data.json")
    return sortable_data, summarization_data


if __name__ == "__main__":
    data_prep("data.json")
    sortable_data, summarization_data = data_load()
    # print(sortable_data)
    # print(summarization_data)

    data_prep("data.json")
    print("saved")