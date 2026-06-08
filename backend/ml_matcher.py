from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dataset import QA_DATASET

dataset_questions = [qa["keywords"][0] for qa in QA_DATASET]
dataset_responses = [qa["response"] for qa in QA_DATASET]

vectorizer = TfidfVectorizer()
dataset_vectors = vectorizer.fit_transform(dataset_questions)

print(f"TF-IDF built successfully! {len(dataset_questions)} questions loaded.")

def ml_match(user_message: str, threshold: float = 0.3):
    """
    Match user message with dataset using TF-IDF + Cosine Similarity.
    Returns best matching response or None if no good match found.
    """
    # Convert user message to vector using SAME vectorizer
    user_vector = vectorizer.transform([user_message])

    # Calculate cosine similarity with all dataset vectors
    similarities = cosine_similarity(user_vector, dataset_vectors)

    # Get the highest similarity score and its index
    best_score = similarities.max()
    best_index = similarities.argmax()

    print(f"Best match score: {best_score:.2f} → '{dataset_questions[best_index]}'")

    # Only return answer if score is above threshold
    if best_score >= threshold:
        return {
            "response": dataset_responses[best_index],
            "score": float(best_score),
            "matched_question": dataset_questions[best_index]
        }

    return None
