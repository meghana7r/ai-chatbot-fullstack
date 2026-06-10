from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dataset import QA_DATASET

# Extract dataset questions and responses
dataset_questions = [qa["keywords"][0] for qa in QA_DATASET]
dataset_responses = [qa["response"] for qa in QA_DATASET]

# Noise words to remove
NOISE_WORDS = {"what", "is", "are", "how", "who", "where",
               "when", "why", "tell", "me", "about", "explain",
               "define", "describe", "give", "the", "a", "an"}

# Synonym mapping - map similar words to same word
SYNONYMS = {
    "hi": "hello",
    "hey": "hello",
    "greetings": "hello",
    "howdy": "hello",
    "thanks": "thank",
    "bye": "bye",
    "goodbye": "bye",
    "ciao": "bye",
}

def remove_noise(text: str) -> str:
    words = text.lower().split()
    filtered = [w for w in words if w not in NOISE_WORDS]
    result = " ".join(filtered)
    return result if result.strip() else text

def apply_synonyms(text: str) -> str:
    """Replace synonym words with their standard form"""
    words = text.lower().split()
    replaced = [SYNONYMS.get(w, w) for w in words]
    return " ".join(replaced)

# Clean dataset questions
cleaned_dataset_questions = [remove_noise(q) for q in dataset_questions]
print(f"Cleaned dataset: {cleaned_dataset_questions}")

# Build TF-IDF vectorizer
vectorizer = TfidfVectorizer()
dataset_vectors = vectorizer.fit_transform(cleaned_dataset_questions)

print(f"TF-IDF built successfully! {len(dataset_questions)} questions loaded.")


def ml_match(user_message: str, threshold: float = 0.8):
    """
    Match user message with dataset using TF-IDF + Cosine Similarity.
    Uses strict threshold 0.8 to avoid wrong matches.
    """
    # Step 1: Remove noise words
    cleaned_message = remove_noise(user_message)

    # Step 2: Apply synonyms
    cleaned_message = apply_synonyms(cleaned_message)

    word_count = len(cleaned_message.strip().split())
    print(f"User cleaned: '{user_message}' → '{cleaned_message}' ({word_count} words)")

    # Step 3: If more than 2 words → complex → skip
    if word_count > 2:
        print("Complex message → skip ML match")
        return None

    # Step 4: Convert to vector
    user_vector = vectorizer.transform([cleaned_message])

    # Step 5: Calculate cosine similarity
    similarities = cosine_similarity(user_vector, dataset_vectors)

    best_score = similarities.max()
    best_index = similarities.argmax()

    print(f"Best match score: {best_score:.2f} → '{dataset_questions[best_index]}'")

    # Step 6: Strict threshold 0.8 → only very confident matches
    if best_score >= threshold:
        return {
            "response": dataset_responses[best_index],
            "score": float(best_score),
            "matched_question": dataset_questions[best_index]
        }

    return None
