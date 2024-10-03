

# Logic Notes
- Does the question needs to sort multiple countries?
    - If yes. Deceending or Accending or random? 
        - Which countries to sort or all?
        - What keys/subkeys to sort by based on this json example (remove non sortabls)
        - How meny countries to return? 
        - return json snnipets 

- If No. Does the question needs to Summary multiple or single countries?
    - If yes. Which countries to Summary or all?
        - What keys/subkeys to use for Summary. json example (Only )
        - return json snnipets


PROMPTS: 
returns 
{
    "countries": a list of contries asked about or ["all"] if the question envolvs all countries,
    "task": one of the following "list_accending", "list_decending", "list_unordered" or "summarization",
    "key/subkeys": an ordered tuple of a key and their childs,
    "max_countries"(optional): in case of sort multiple countries what number of countries to return. 
     
}


prompt 2
takes data + question returns answer 

## Data cleaning
- remove the word String
- any "" or '' should be none
- drop any FileAttachment key
- drop ginfo for now (ask later)
<!-- - drop trips for now (ask later) -->
- sortable keys are 
    - ["country", "moi", "defense", "energy", "mofa", "qia", "qffd", "moci"]
- Summary keys are
    - ["talkingPoints", "outStandings", "trips"]
- If a key has a list value that has only one value in it compress it 

## Time plan
- **Mon**: Data cleaning ✅ ~4hours
- **Tue**: Data cleaning + LLAMA 3.1 70B or 8B + logic
- **Wed**: fastapi + Deploy first iteration (on 48 70B should be fine)

