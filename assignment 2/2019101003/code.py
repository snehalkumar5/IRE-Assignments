import requests

def get_query():
    SPARQL_URL = "https://query.wikidata.org/sparql"
    query = "SELECT ?objectLabel ?dataLabel { VALUES (?state) {(wd:Q1174)} ?state ?p ?statement . ?statement ?ps ?data . ?object wikibase:statementProperty ?ps. SERVICE wikibase:label { bd:serviceParam wikibase:language 'hi' } }"
    param = {
        'query': query,
        'format': 'json'
    }
    resp = requests.get(SPARQL_URL, params=param, headers={ 'User-Agent': 'IRE_WIKI_BOT' }).json()
    # print(resp)
    return resp

def female(predicate):
    return True if any(noun in predicate for noun in ["प्रशासनिक इकाई", "आईडी", "वेबसाइट", "राजधानी", "जनसंख्या","भाषा", "निकाय", "छवि"]) else False

def respect(predicate):
    return True if any(noun in predicate for noun in ["तिथि","राज्याध्यक्ष","निर्माण","स्थान","विषय", "शासनाध्यक्ष"]) else False

def get_output(response):
    Grammar = []
    out = response["results"]
    for data in out["bindings"]:
        if 'xml:lang' in data["objectLabel"]:
            if data['objectLabel']['xml:lang'] == 'hi':
                Grammar.append({
                    "subject": "हरियाणा",
                    "predicate": data["objectLabel"]["value"],
                    "object": data["dataLabel"]["value"]
                })
    # print(Grammar)
    return Grammar
    
if __name__ == "__main__":
    # Query result from SPARQL
    resp = get_query()
    RDFTriplets = get_output(resp)

    # Convert RDFTiplets to text for article
    SUBJECT = "हरियाणा"
    GENDER = {"MALE":"का", "THEY":"के", "FEMALE":"की"}
    TENSE = {"PRESENT":"है","RESPECT":"हैं"}
    sentences = []
    neighbours = []
    for data in RDFTriplets:
        predi = data['predicate']
        obj = data['object']
        sentence = ""
        if "उदहारण" in data["predicate"]:
            sentence = " ".join([SUBJECT, obj, GENDER["MALE"], data["predicate"], TENSE["PRESENT"]])
        elif "प्रशासनिक इकाई में है" in data["predicate"]:
            sentence = " ".join([SUBJECT, obj, GENDER["FEMALE"], data["predicate"]])
        elif "प्रशासनिक इकाई" in data["predicate"]:
            if "Q" in obj:
                sentence = " ".join(["अंक", obj, SUBJECT, GENDER["FEMALE"], data["predicate"], "में", TENSE["PRESENT"]])
            else:
                sentence = " ".join([obj, SUBJECT, GENDER["FEMALE"], data["predicate"], "में", TENSE["PRESENT"]])            
        elif female(data["predicate"]):
            sentence = " ".join([SUBJECT, GENDER["FEMALE"], data["predicate"], obj, TENSE["PRESENT"]])
        elif respect(data["predicate"]):
            sentence = " ".join([SUBJECT, GENDER["THEY"], data["predicate"], obj, TENSE["RESPECT"]])
        elif "सीमा लगती है" in data["predicate"]:
            neighbours.append(obj)
            sentence = " ".join([SUBJECT, GENDER["FEMALE"], obj, "से", data["predicate"]])
        elif TENSE["PRESENT"] not in data["predicate"]:
            sentence = " ".join([SUBJECT, GENDER["MALE"], data["predicate"], obj, TENSE["PRESENT"]])
        else:
            sentence = " ".join([SUBJECT, obj, data["predicate"]])
        sentences.append(sentence)
    print("।\n".join(sentences))