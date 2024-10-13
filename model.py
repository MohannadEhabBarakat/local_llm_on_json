import transformers
import torch
import json

# model_id = "meta-llama/Meta-Llama-3.1-70B-Instruct"
model_id = "meta-llama/Llama-3.1-8B-Instruct"
# model_id = "meta-llama/CodeLlama-13b-Python-hf"
# model_id = "meta-llama/CodeLlama-7b-Instruct-hf"
# model_id = "meta-llama/CodeLlama-34b-Instruct-hf"
# model_id = "unsloth/Llama-3.2-3B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

jsn = '''
{
"United States": {
        "country": 55.0,
        "moi": 9.0,
        "defense": 9.0,
        "energy": {
            "Expl": 1.0,
            "Prdt": null,
            "Invest": 0.0,
            "LNG": 0.0
        },
        "mofa": {
            "EsgAlly": 4.0,
            "MultLoy": 7.0
        },
        "qia": {
            "QIACur": 6.0,
            "QIAPtos": 9.0
        },
        "qffd": 8.0,
        "moci": {
            "TrdFdi": 67.0,
            "EssTrd": 17.0
        },
        "talkingPoints": [
            {
                "SubTitle": 33333,
                "Title": 33333,
                "Details": " 33333  ",
                "FileAttachment": null
            },
            {
                "SubTitle": 999999,
                "Title": 88888,
                "Details": " 00000  ",
                "FileAttachment": null
            },
            {
                "SubTitle": "dfdf",
                "Title": "dffd",
                "Details": null,
                "FileAttachment": null
            }
        ],
        "outStandings": [
            {
                "Title": null,
                "FileAttachment": null,
                "Description": " Qatar beat Chile to reach Volleyball Challenger Cup Final"
            },
            {
                "Title": null,
                "FileAttachment": null,
                "Description": "Chile, officially the Republic of Chile "
            }
        ],
        "trips": null
    }
}
'''

# question = "What is the top five qia QIACr countries?"
# question = "Summary talking points for Chile?"

def route(question):
    question_template = f'''
        Help me extract relative data to answer this question {question}. Answer in this format please:
        {{
            "countries": a list of contries needed to answer the question or ["all"] if the question envolvs all countries
        }}

        Steps to follow:
        1- When answering ignore those words ["country", "moi", "defense", "energy", "mofa", "qia", "qffd", "moci", "Expl", "Prdt", "Invest", "LNG", "EsgAlly", "MultLoy", "QIACur", "QIAPtos", "TrdFdi", "EssTrd"]
        2- If no countries are mentioned (explicitly), set countries to ["all"] !Important
        3- Extract the countries mentioned in the question
        4- If all countries are mentioned, set countries to ["all"]
        5- NEVER EVER SET countries to None. Always set it to ["all"] if no countries are mentioned
        6- NEVER EVER add country that was not mentioned explicitly in the question. Only add countries that are explicitly mentioned in the question
        7- Please never add countries that are not mentioned in the question. Only add countries that are explicitly mentioned in the question or just ["all"] when in doubt

        Those countries are used to extract the data needed to answer the question. Make sure to extract the correct countries. If no countries are mentioned, set it to ["all"]

        Example:
        List top 10 countries for energy?
        {{
            "countries": ["all"],
        }}
        What are the lowest qia countries?
        {{
            "countries": ["all"],
        }}
        What are the lowest 5 countries for mofa EsgAlly?
        {{
            "countries": ["all"],
        }}
        List Chile, Qatar, and the United States for qia
        {{
            "countries": ["Chile", "Qatar", "United States"],
        }}

        list lowest 3 country in ...
        {{
            "countries": ["all"],
        }}
        
        Respond must be valid json. Make sure it is a vaild JSON. Must follow the example above

    '''

    messages = [
        {"role": "system", "content": f'''You are a json expert. You answer all questions in json only.'''},
        {"role": "user", "content": question_template},
    ]
    top_p = 0.9
    temperature = 0.9
    print("country:", temperature, top_p)
    outputs = pipeline(
        messages,
        max_new_tokens=512,
        temperature=temperature,
        top_p=top_p
    )
    print("outputs country", outputs)
    try:
      res = json.loads(outputs[0]["generated_text"][-1]["content"])
    except:
      res = rejson(outputs[0]["generated_text"][-1]["content"])
    
    print("outputs country 2", res)

    res["max_countries"] = subroute(question)
    key_subkey = route_key_subkey(question)
    res["key"] = key_subkey["key"]
    res["subkey"] = key_subkey["subkey"]
    res["task"] = route_task(question)
    
    # print("pre-review filter", res)
    # res = review(question, res)
    print("Finall filter", res)

    return res

def route_task(question):
    question_template = f'''
        Help me extract relative data to answer this question {question}.Answer in this format please.
        {{
            "task": one of the following "list_accending"(e.g. least, lowest, low ...etc), "list_decending"(e.g. top, best, heighst ...etc), "list_unordered" or "summarization",
        }}
        
        Example:
        List top 10 countries for energy?
        {{
            "task": "list_accending"
        }}
        What are the lowest qia countries?
        {{
            "task": "list_accending"
        }}
        What are the top 5 countries for mofa EsgAlly?
        {{
            "task": "list_accending"
        }}
        List 5 countries for qia
        {{
            "task": "list_unordered"
        }}

        Respond must be valid json. Make sure it is a vaild JSON. Must follow the example above

    '''

    messages = [
        {"role": "system", "content": f'''You are a json expert. You answer all questions in json only.'''},
        {"role": "user", "content": question_template},
    ]
    top_p = 0.9
    temperature = 0.6
    print("country:", temperature, top_p)
    outputs = pipeline(
        messages,
        max_new_tokens=512,
        temperature=temperature,
        top_p=top_p
    )
    print("outputs country", outputs)
    try:
      res = json.loads(outputs[0]["generated_text"][-1]["content"])
    except:
      res = rejson(outputs[0]["generated_text"][-1]["content"])
    
    

    return res["task"]

def rejson(simi_json):
  question_template = f'''
  Fix errors in the input to be valid json.
  Input: {simi_json}
  '''
  messages = [
        {"role": "system", "content": f'''You are a json expert. You answer all questions in json only. Use this json example as your guide for all answers {jsn}'''},
        {"role": "user", "content": question_template},
    ]
  outputs = pipeline(
        messages,
        max_new_tokens=512,
        temperature=0.3,
        top_p=0.9
    )
  return json.loads(outputs[0]["generated_text"][-1]["content"])

def subroute(question):
    question_template = f'''
        Help me extract relative data to answer this question {question}.Answer in this format please.
        {{
            "max_countries": What number of countries is the user intersted in seeing. If all countries are asked for, then return -1.
        }}
        Notes:
        1- Set max_countries to to countries asked for, if all countries are asked for set it to -1 (e.g. "List defense data for all countries" max_countries = -1 but What are the lowest 5  countries max_countries = 5)
        2- ALWAYS set max_countries to the number in the question or -1 ONLY if all countries are asked for

        Example:
        List top 10 countries for energy?
        {{
            "max_countries": 10
        }}
        What are the lowest QIA countries?
        {{
            "max_countries": -1
        }}
        What are the top 5 countries for mofa EsgAlly?
        {{
            "max_countries": 5
        }}
        List top 5 countries for qia
        {{
            "max_countries": 5
        }}
        

        Respond must be valid json. Make sure it is a vaild JSON

    '''

    messages = [
        {"role": "system", "content": f'''You are a json expert. You answer all questions in json only. '''},
        {"role": "user", "content": question_template},
    ]
    # print(messages)
    top_p = 0.9
    temperature = .6
    print("max_countries:", temperature, top_p)

    outputs = pipeline(
        messages,
        max_new_tokens=256,
        temperature=temperature,
        top_p=top_p
    )
    print("outputs max_countries", outputs)
    try:
      res = json.loads(outputs[0]["generated_text"][-1]["content"])
    except:
      res = rejson(outputs[0]["generated_text"][-1]["content"])
    

    return res["max_countries"]

def route_key_subkey(question):
    question_template = f'''
        Help me extract relative data to answer this question {question}.Answer in this format please.
        {{
            "key": The main key in the question (ignore any country key),
            "subkey": The sub key in the question (ignore any country key) ONLY used if the subkey is explicitly mentioned in the question otherwise None. Never set it when metioned in question,

        }}
        Notes
        1- If subkey is not metioned in the question it must not be in the output. For example 'What is the top five qia countries?' "qia": 'mofa' but no subkey
        2- DO NOT repeate a key
        4- NEVER EVER SET subkey if not metioned in the question. 
        5- Make sure to use the correct key/subkey name.
        6- Was the subkey mentioned in the question? use it. If not, None.
        7- Your response JSON has only key and subkey

        Example:
        List top 10 countries for energy?
        {{
            "key": "energy",
            "subkey": None
        }}
        What are the lowest qia countries?
        {{
            "key": "qia",
            "subkey": None
        }}
        What are the top 5 countries for mofa EsgAlly?
        {{
            "key": "mofa",
            "subkey": "EsgAlly"
        }}
        list top 7 moci countries
        {{
            "key": "moci",
            "subkey": None
        }}
        List top 5 countries for Invest
        {{
            "key": "energy",
            "subkey": "Invest"
        }}

        Respond must be valid json. Make sure it is a vaild JSON. Must follow the example above

    '''

    messages = [
        {"role": "system", "content": f'''You are a json expert. You answer all questions in json only. Use this json example as your guide for all answers {jsn}'''},
        {"role": "user", "content": question_template},
    ]
    top_p = 0.9
    temperature = 0.6
    print("key/sbukey:", temperature, top_p)
    outputs = pipeline(
        messages,
        max_new_tokens=512,
        temperature=temperature,
        top_p=top_p
    )
    print("outputs key/sbukey 2", outputs)


    try:
      res = json.loads(outputs[0]["generated_text"][-1]["content"])
    except:
      res = rejson(outputs[0]["generated_text"][-1]["content"])

    print("outputs key/sbukey 3", res)
  
    return res

def answerLLM(question, evedance):
    question_template = f'''
    Question: {question}
    Evedance: {evedance}

    Note:
    1- evedance is for your info to get proper answer. Never descripe its shape or structure. Just use it to answer the question. 
    2- All of your data is factual and uptodate
    3- Never add any extra information to the answer that is not in the evedance

    Do not add information that is not in the evedance. Just answer the question based on the evedance provided. If answer not available just say "I could'nt find the answer". All of your answers are in plain English with a direct frendly tone
    '''
    messages = [
        {"role": "system", "content": f'''You are an expert. You'll be given a question and evedance. Answer the question based on the provided evedance only. If answer not available just say "I could'nt find the answer". All of your answers are in plain English with a direct frendly tone'''},
        {"role": "user", "content": question_template},
    ]

    outputs = pipeline(
        messages,
        max_new_tokens=3000,
        temperature=0.2
    )
    return outputs[0]["generated_text"][-1]["content"]


def review(question, keys):
    question_template = f'''
    Question: {question}
    dictionary: {keys}

    Response format:
    {{
        'countries': a list of contries asked about or ["all"] if the question envolvs all countries,
        "task": one of the following "list_accending"(e.g. least, lowest ...etc), "list_decending"(e.g. top, best ...etc), "list_unordered" or "summarization",
        'max_countries': What number of countries is the user intersted in seeing. If all countries are asked for, then return -1., 
        "key": The main key in the question (ignore any country key),
        "subkey": The sub key in the question (ignore any country key) ONLY used if the subkey is explicitly mentioned in the question otherwise None. Never set it when metioned in question,
    }}

    Steps to follow:
    1- Think about the question and the dictionary provided
    2- Is there a mistake in the dictionary? If so, fix it. If in doubt, leave it as is
    3- Return a valid dictionary with the corrected values. Do not add any extra information to the dictionary. Just correct the values that are wrong. If the value is correct, leave it as is.

    Only resond with a valid JSON. Make sure it is a vaild JSON. Must follow the example above
    '''
    messages = [
        {"role": "system", "content": f'''You are an JSON expert. You'll be given a question and extraction dictionary. Fix any errors in the dictionary and return the corrected dictionary'''},
        {"role": "user", "content": question_template},
    ]

    outputs = pipeline(
        messages,
        max_new_tokens=512,
        temperature=0.6,
        top_p=0.9
    )
    return outputs[0]["generated_text"][-1]["content"]

if __name__ == "__main__":
    question = "What is the top five qia QIACr countries?"
    print(route(question))
    question = "Summary talking points for Chile?"
    print(route(question)) 