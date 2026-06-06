import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)


lemmatizer = WordNetLemmatizer()


STOP_WORDS = set(stopwords.words("english"))


KEEP_WORDS = {
    "what", "who", "where", "when", "why", "how",
    "not", "no", "never", "nothing",
    "you", "your", "me", "my", "i",
    "is", "are", "was", "were"
}


FINAL_STOP_WORDS = STOP_WORDS - KEEP_WORDS



def clean_text(text: str) -> str:
   
    text = text.lower()


    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(text: str) -> list:
    
    tokens = word_tokenize(text)
    return tokens


def remove_stopwords(tokens: list) -> list:
    
    filtered = [
        word for word in tokens
        if word not in FINAL_STOP_WORDS
    ]
    return filtered


def lemmatize(tokens: list) -> list:
    
    lemmatized = [lemmatizer.lemmatize(word) for word in tokens]
    return lemmatized



def preprocess(text: str) -> dict:
    
    cleaned = clean_text(text)

    
    tokens = tokenize(cleaned)

    
    filtered_tokens = remove_stopwords(tokens)

    
    lemmatized_tokens = lemmatize(filtered_tokens)

    
    processed_text = " ".join(lemmatized_tokens)

    return {
        "original": text,
        "cleaned": cleaned,
        "tokens": tokens,
        "filtered_tokens": filtered_tokens,
        "lemmatized_tokens": lemmatized_tokens,
        "processed_text": processed_text
    }
