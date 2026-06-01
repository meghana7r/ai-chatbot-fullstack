from fastapi import APIRouter
from pydantic import BaseModel
from nlp_processor import preprocess

router = APIRouter()


class NLPRequest(BaseModel):
    text: str


@router.post("/nlp/preprocess")
def nlp_preprocess(request: NLPRequest):
    """
    NLP Preprocessing endpoint.
    Shows each step of the pipeline:
    1. Clean text
    2. Tokenize
    3. Remove stopwords
    4. Lemmatize
    """
    result = preprocess(request.text)

    return {
        "original": result["original"],
        "step1_cleaned": result["cleaned"],
        "step2_tokens": result["tokens"],
        "step3_filtered_tokens": result["filtered_tokens"],
        "step4_lemmatized_tokens": result["lemmatized_tokens"],
        "final_processed_text": result["processed_text"],
        "status": "success"
    }
