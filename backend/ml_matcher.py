from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dataset import QA_DATASET

# Extract dataset questions and responses
dataset_questions = [qa["keywords"][0] for qa in QA_DATASET]
dataset_responses = [qa["response"] for qa in QA_DATASET]

NOISE_WORDS = {"is", "are", "was", "were", "the", "a", "an",
               "about", "of", "in", "on", "at", "to", "for",
               "with", "by", "from", "this", "that", "it"}


SYNONYMS = {
    "hi": "hello",
    "hey": "hello",
    "heyy": "hello",
    "hiii": "hello",
    "helloo": "hello",
    "hellooo": "hello",
    "greetings": "hello",
    "goodbye": "bye",
    "byee": "bye",
    "byeee": "bye",
    "byeeee": "bye",
    "ciao": "bye",
    "thanks": "thank",
    "laugh": "joke",
    "funny": "joke",
    "humor": "joke",
    "capabilities": "capabilities",
    "features": "capabilities",
}


INFO_WORDS = {"python", "java", "javascript", "ai", "ml",
              "machine", "learning", "deep", "neural", "data",
              "science", "define", "describe",
              "weather", "news", "stock", "price", "capital",
              "country", "history", "math", "science"}


def remove_noise(text: str) -> str:
    words = text.lower().split()
    filtered = [w for w in words if w not in NOISE_WORDS]
    result = " ".join(filtered)
    return result if result.strip() else text


def apply_synonyms(text: str) -> str:
    words = text.lower().split()
    replaced = [SYNONYMS.get(w, w) for w in words]
    return " ".join(replaced)


def has_info_words(text: str) -> bool:
    """Check if message contains information-seeking words"""
    words = text.lower().split()
    return any(w in INFO_WORDS for w in words)



cleaned_dataset_questions = [remove_noise(q) for q in dataset_questions]
print(f"Cleaned dataset: {cleaned_dataset_questions}")


vectorizer = TfidfVectorizer()
dataset_vectors = vectorizer.fit_transform(cleaned_dataset_questions)

print(f"TF-IDF built successfully! {len(dataset_questions)} questions loaded.")


def ml_match(user_message: str, threshold: float = 0.6):
    
    cleaned_message = remove_noise(user_message)

    
    cleaned_message = apply_synonyms(cleaned_message)

    word_count = len(cleaned_message.strip().split())
    print(f"User cleaned: '{user_message}' → '{cleaned_message}' ({word_count} words)")

    
    if has_info_words(cleaned_message):
        print("Info seeking message → skip ML match")
        return None

    
    if word_count > 3:
        print("Complex message → skip ML match")
        return None

    
    user_vector = vectorizer.transform([cleaned_message])

    
    similarities = cosine_similarity(user_vector, dataset_vectors)

    best_score = similarities.max()
    best_index = similarities.argmax()

    print(f"Best match score: {best_score:.2f} → '{dataset_questions[best_index]}'")

    if best_score >= threshold:
        return {
            "response": dataset_responses[best_index],
            "score": float(best_score),
            "matched_question": dataset_questions[best_index]
        }

    return None
