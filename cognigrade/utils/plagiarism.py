from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Tuple, Dict
import os

LOCAL_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", cache_folder=LOCAL_MODEL_DIR)

def compute_embeddings(answers: List[str]):
    return model.encode(answers, convert_to_tensor=True)

def compute_similarity_matrix(embeddings) -> np.ndarray:
    return util.cos_sim(embeddings, embeddings).cpu().numpy()

def detect_plagiarism_proc(student_answers: List[Dict[str, str]], threshold: float = 0.85) -> List[Tuple[str, str, float]]:
    """
    Detect plagiarism between student answers.
    
    Args:
        student_answers: List of dictionaries, each containing 'student_id' and 'answer'
        threshold: Similarity threshold above which answers are considered plagiarized (default: 0.85)
    
    Returns:
        List of tuples containing (student_id1, student_id2, similarity_score)
    """
    student_ids = [answer['student_id'] for answer in student_answers]
    answers = [answer['answer'] for answer in student_answers]
    
    embeddings = compute_embeddings(answers)
    similarity_matrix = compute_similarity_matrix(embeddings)

    cheating_pairs = []
    for i in range(len(answers)):
        for j in range(i + 1, len(answers)):
            similarity = similarity_matrix[i][j]
            print(f"Comparing student {student_ids[i]} with student {student_ids[j]}: similarity = {similarity}")
            if similarity > threshold:
                cheating_pairs.append((student_ids[i], student_ids[j], float(round(similarity, 3))))

    return cheating_pairs