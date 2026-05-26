from dataset import QA_DATASET, DEFAULT_RESPONSE

def keyword_match(user_message: str) -> str:
    """
    Rule-based chatbot using keyword matching.
    Steps:
    1. Lowercase the user message
    2. Check each Q&A entry for keyword matches
    3. Score by number of keyword hits
    4. Return the best matching response
    """
    message_lower = user_message.lower().strip()
    
    best_match = None
    best_score = 0
    
    for qa in QA_DATASET:
        score = 0
        for keyword in qa["keywords"]:
            if keyword.lower() in message_lower:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = qa
    
    if best_match and best_score > 0:
        return best_match["response"]
    
    return DEFAULT_RESPONSE
