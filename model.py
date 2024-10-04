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
            "subkey"(optional): The sub key in the question (ignore any country key) ONLY used if the subkey is explicitly mentioned in the question otherwise please omit the key. Never set it id nor metioned in question,
            "max_countries"(optional): in case of sort multiple countries what number of countries to return. If all countries are asked for then return -1

        }}
        Notes
        1- If subkey is not metioned in the question it must not be in the output. For example 'What is the top five mofa countries?' "key": 'mofa' but no subkey
        2- DO NOT repeate a key
        3- DO NOT repeate a country
        4- If the key is outStandings, trips or talkingPoints then the task must be summarization
        5- Think carefully about subkey. Was it mentioned explicitly in the question? If no omit it, if not sure also omit it
    '''

    messages = [
        {"role": "system", "content": f'''You are a json expert. You answer all questions in json only. Use this json example as your guide for all answers {jsn}'''},
        {"role": "user", "content": question_template},
    ]
    print(messages)
    outputs = pipeline(
        messages,
        max_new_tokens=256,
        temperature=0.1
    )

    return json.loads(outputs[0]["generated_text"][-1]["content"])

def answerLLM(question, evedance):
    question_template = f'''
    Question: {question}
    Evedance: {evedance}

    Note:
    1- evedance is for your info to get proper answer. Never descripe its shape or structure. Just use it to answer the question. 
    2- All of your data is factual and uptodate
    '''
    messages = [
        {"role": "system", "content": f'''You are an expert. You'll be given a question and evedance. Answer the question based on the provided evedance only. If answer not available just say "I could'nt find the answer". All of your answers are in plain English with a direct frendly tone'''},
        {"role": "user", "content": question_template},
    ]

    outputs = pipeline(
        messages,
        max_new_tokens=3000,
        temperature=0.1
    )
    return outputs[0]["generated_text"][-1]["content"]

if __name__ == "__main__":
    question = "What is the top five qia QIACr countries?"
    print(route(question))
    question = "Summary talking points for Chile?"
    print(route(question)) 