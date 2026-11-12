import requests
from langchain_core.tools import tool


@tool
def define_word(word: str) -> str:
    """
    Look up the definition, pronunciation, part of speech, usage examples,
    and synonyms for any English word. Uses Free Dictionary API — no API key.
    """
    r = requests.get(
        f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.strip()}",
        timeout=10
    )
    if r.status_code != 200:
        return f"Word '{word}' not found. Check spelling or try a simpler form."

    data = r.json()[0]
    phonetic = data.get("phonetic", "")
    result = f"Word: {data['word']}  {phonetic}\n\n"

    for meaning in data.get("meanings", [])[:3]:
        pos = meaning.get("partOfSpeech", "")
        result += f"[{pos}]\n"
        for defn in meaning.get("definitions", [])[:2]:
            result += f"  Definition : {defn.get('definition', '')}\n"
            if defn.get("example"):
                result += f"  Example    : {defn['example']}\n"
        synonyms = meaning.get("synonyms", [])[:5]
        if synonyms:
            result += f"  Synonyms   : {', '.join(synonyms)}\n"
        result += "\n"

    return result.strip()
