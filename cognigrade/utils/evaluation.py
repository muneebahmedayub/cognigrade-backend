from sentence_transformers import SentenceTransformer, util
from typing import Tuple
import os

LOCAL_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

models = {
    "short": SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder=LOCAL_MODEL_DIR),
    "long": SentenceTransformer("sentence-transformers/all-mpnet-base-v2", cache_folder=LOCAL_MODEL_DIR),
    "paraphrased": SentenceTransformer("sentence-transformers/paraphrase-mpnet-base-v2", cache_folder=LOCAL_MODEL_DIR),
}

grading_thresholds = {
    "strict": {
        "full": 0.85,
        "partial": 0.7
    },
    "loose": {
        "full": 0.8,
        "partial": 0.65
    },
    "paraphrased": {
        "full": 0.75,
        "partial": 0.6
    }
}

def grade_answer_proc(
    student_answer: str,
    answer_key: str,
    answer_type: str
) -> Tuple[str, float]:
    
    if answer_type == "paraphrased":
        model = models["paraphrased"]
    else:
        model = models["short"] if answer_type == "short" else models["long"]

    emb_student = model.encode(student_answer, convert_to_tensor=True)
    emb_key = model.encode(answer_key, convert_to_tensor=True)

    similarity = float(util.cos_sim(emb_student, emb_key)[0])

    thresholds = grading_thresholds.get(answer_type, grading_thresholds["strict"])

    if similarity >= thresholds["full"]:
        return "Full Marks", similarity
    elif similarity >= thresholds["partial"]:
        return "Partial Marks", similarity
    else:
        return "Incorrect", similarity