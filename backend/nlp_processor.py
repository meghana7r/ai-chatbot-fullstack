import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (runs once)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Load English stopwords
STOP_WORDS = set(stopwords.words("english"))

# Keep these important words even if they are stopwords
# Because removing them changes the meaning!
KEEP_WORDS = {
    "what", "who", "where", "when", "why", "how",
    "not", "no", "never", "nothing",
    "you", "your", "me", "my", "i",
    "is", "are", "was", "were"
}

# Final stopwords = english stopwords MINUS keep words
FINAL_STOP_WORDS = STOP_WORDS - KEEP_WORDS


# ── Step 1: Clean Text ────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    """
    Clean the user input text.
    - Convert to lowercase
    - Remove special characters
    - Remove extra spaces
    """
    # Convert to lowercase
    # "Hello WORLD" → "hello world"
    text = text.lower()

    # Remove special characters but keep letters, numbers, spaces
    # "hello!!!" → "hello"
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Remove extra spaces
    # "hello   world" → "hello world"
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ── Step 2: Tokenization ──────────────────────────────────────────────────────
def tokenize(text: str) -> list:
    """
    Split sentence into individual words (tokens).
    "hello how are you" → ["hello", "how", "are", "you"]
    """
    tokens = word_tokenize(text)
    return tokens


# ── Step 3: Stop Word Removal ─────────────────────────────────────────────────
def remove_stopwords(tokens: list) -> list:
    """
    Remove common useless words.
    ["hello", "how", "are", "you"] → ["hello", "you"]
    """
    filtered = [
        word for word in tokens
        if word not in FINAL_STOP_WORDS
    ]
    return filtered


# ── Step 4: Lemmatization ─────────────────────────────────────────────────────
def lemmatize(tokens: list) -> list:
    """
    Convert words to their base form.
    "running" → "run"
    "studies" → "study"
    "better"  → "good"
    """
    lemmatized = [lemmatizer.lemmatize(word) for word in tokens]
    return lemmatized


# ── Step 5: Full NLP Pipeline ─────────────────────────────────────────────────
def preprocess(text: str) -> dict:
    """
    Complete NLP preprocessing pipeline.
    Runs all 4 steps in order and returns each step's result.
    """
    # Step 1: Clean
    cleaned = clean_text(text)

    # Step 2: Tokenize
    tokens = tokenize(cleaned)

    # Step 3: Remove stopwords
    filtered_tokens = remove_stopwords(tokens)

    # Step 4: Lemmatize
    lemmatized_tokens = lemmatize(filtered_tokens)

    # Final processed text (join tokens back to string)
    processed_text = " ".join(lemmatized_tokens)

    return {
        "original": text,
        "cleaned": cleaned,
        "tokens": tokens,
        "filtered_tokens": filtered_tokens,
        "lemmatized_tokens": lemmatized_tokens,
        "processed_text": processed_text
    }
