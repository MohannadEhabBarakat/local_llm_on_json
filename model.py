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
        Help me extract relative data to answer this question {question}.Answer in this format please.
        {{
            "countries": a list of contries asked about or ["all"] if the question envolvs all countries,
            "task": one of the following "list_accending"(e.g. least, lowest ...etc), "list_decending"(e.g. top, best ...etc), "list_unordered" or "summarization",
            "key": The main key in the question (ignore any country key),
            "subkey": The sub key in the question (ignore any country key) ONLY used if the subkey is explicitly mentioned in the question otherwise None. Never set it when metioned in question,

        }}
        Notes
        1- If subkey is not metioned in the question it must not be in the output. For example 'What is the top five qia countries?' "qia": 'mofa' but no subkey
        2- DO NOT repeate a key
        3- DO NOT repeate a country
        4- NEVER EVER SET subkey if not metioned in the question. 
        5- Make sure to use the correct key/subkey name.
        6- Was the subkey mentioned in the question? use it. If not, None.

        Example:
        List top 10 countries for energy?
        {{
            "countries": ["all"],
            "task": "list_accending",
            "key": "energy",
            "subkey": None
        }}
        What are the lowest qia countries?
        {{
            "countries": ["all"],
            "task": "list_accending",
            "key": "qia",
            "subkey": None
        }}
        What are the top 5 countries for mofa EsgAlly?
        {{
            "countries": ["all"],
            "task": "list_accending",
            "key": "mofa",
            "subkey": "EsgAlly"
        }}
        Respond must be valid json. Make sure it is a vaild JSON

    '''

    messages = [
        {"role": "system", "content": f'''You are a json expert. You answer all questions in json only. Use this json example as your guide for all answers {jsn}'''},
        {"role": "user", "content": question_template},
    ]
    top_p = 0.4
    temperature = 0.3
    print("key/sbukey:", temperature, top_p)
    outputs = pipeline(
        messages,
        max_new_tokens=512,
        temperature=temperature,
        top_p=top_p
    )

    try:
      res = json.loads(outputs[0]["generated_text"][-1]["content"])
    except:
      res = rejson(outputs[0]["generated_text"][-1]["content"])

    res["max_countries"] = subroute(question)
    key_subkey = route_key_subkey(question)
    res["key"] = key_subkey["key"]
    res["subkey"] = key_subkey["subkey"]
    return res

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
        top_p=0.4
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
    temperature = .3
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
        Respond must be valid json. Make sure it is a vaild JSON

    '''

    messages = [
        {"role": "system", "content": f'''You are a json expert. You answer all questions in json only. Use this json example as your guide for all answers {jsn}'''},
        {"role": "user", "content": question_template},
    ]
    top_p = 0.9
    temperature = 0.1
    print("key/sbukey:", temperature, top_p)
    outputs = pipeline(
        messages,
        max_new_tokens=512,
        temperature=temperature,
        top_p=top_p
    )
    print("outputs key/sbukey", outputs)


    try:
      res = json.loads(outputs[0]["generated_text"][-1]["content"])
    except:
      res = rejson(outputs[0]["generated_text"][-1]["content"])

  
    return res

def answerLLM(question, evedance):
    question_template = f'''
    Question: {question}
    Evedance: {evedance}

    Note:
    1- evedance is for your info to get proper answer. Never descripe its shape or structure. Just use it to answer the question. 
    2- All of your data is factual and uptodate
    3- Never add any extra information to the answer that is not in the evedance
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

if __name__ == "__main__":
    question = "What is the top five qia QIACr countries?"
    print(route(question))
    question = "Summary talking points for Chile?"
    print(route(question)) 