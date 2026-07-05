from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# SIMPLIFIED DATASET - only basic greetings/small talk
dataset = [
    {"keywords": ["hello", "hi", "hey"], "response": "Hi there! How can I help you today? 😊"},
    {"keywords": ["bye", "goodbye", "see you"], "response": "Goodbye! Have a great day! 👋"},
    {"keywords": ["thank you", "thanks"], "response": "You're welcome! Happy to help. 😊"},
    {"keywords": ["who are you"], "response": "I'm an AI assistant for Gaint Clout, here to help you!"},
]

dataset_questions = [entry["keywords"][0] for entry in dataset]
dataset_responses = [entry["response"] for entry in dataset]

NOISE_WORDS = {"is", "are", "was", "were", "the", "a", "an", "about", 
               "of", "in", "on", "at", "to", "for", "tell", "me"}

SYNONYMS = {
    "hi": "hello",
    "hey": "hello",
    "heyy": "hello",
    "byeee": "bye",
    "goodbye": "bye",
    "thanks": "thank you"
}

# Expanded info words - anything that should ALWAYS go to Groq
INFO_WORDS = {
    "python", "java", "javascript", "ai", "ml", "machine", "learning",
    "weather", "news", "stock", "price", "capital", "country",
    "bts", "music", "song", "movie", "actor", "celebrity", "sports",
    "history", "science", "math", "physics", "chemistry", "biology",
    "recipe", "cook", "food", "travel", "place", "city", "country",
    "explain", "what is", "how does", "why does", "define"
}

vectorizer = TfidfVectorizer()

def clean_dataset():
    cleaned = []
    for q in dataset_questions:
        words = q.split(" ")
        filtered = [w for w in words if w not in NOISE_WORDS]
        cleaned.append(" ".join(filtered))
    return cleaned

cleaned_dataset = clean_dataset()
dataset_vectors = vectorizer.fit_transform(cleaned_dataset)

print(f"Cleaned dataset: {cleaned_dataset}")
print(f"TF-IDF built successfully! {len(dataset_questions)} questions loaded.")


def remove_noise(text):
    words = text.split(" ")
    filtered = [w for w in words if w not in NOISE_WORDS]
    return " ".join(filtered)


def apply_synonyms(text):
    words = text.split(" ")
    replaced = [SYNONYMS.get(w, w) for w in words]
    return " ".join(replaced)


def has_info_words(text):
    words = text.split(" ")
    for word in words:
        if word in INFO_WORDS:
            return True
    return False


def ml_match(user_message, threshold=0.7):  # Increased threshold for stricter matching
    cleaned = remove_noise(user_message)
    cleaned = apply_synonyms(cleaned)
    
    # Skip ML match if contains any info/knowledge words
    if has_info_words(user_message.lower()):
        print(f"Info word detected → skip ML match, use Groq")
        return None
    
    word_count = len(cleaned.split(" "))
    if word_count > 3:
        print(f"Complex message → skip ML match")
        return None
    
    if not cleaned.strip():
        return None
    
    user_vector = vectorizer.transform([cleaned])
    similarities = cosine_similarity(user_vector, dataset_vectors)
    
    best_score = 0
    best_index = -1
    
    for i in range(len(similarities[0])):
        score = similarities[0][i]
        if score > best_score:
            best_score = score
            best_index = i
    
    print(f"User cleaned: '{user_message}' → '{cleaned}' ({word_count} words)")
    print(f"Best match score: {best_score:.2f} → '{dataset_questions[best_index] if best_index >= 0 else 'none'}'")
    
    if best_score >= threshold:
        return {
            "response": dataset_responses[best_index],
            "score": best_score
        }
    
    return None
