from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Tuple, Dict
import os
import logging

logger = logging.getLogger(__name__)

# Path to store the models locally
LOCAL_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

# Load different models for different answer types
models = {
    "short": SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder=LOCAL_MODEL_DIR),
    "long": SentenceTransformer("sentence-transformers/all-mpnet-base-v2", cache_folder=LOCAL_MODEL_DIR),
    "paraphrased": SentenceTransformer("sentence-transformers/paraphrase-mpnet-base-v2", cache_folder=LOCAL_MODEL_DIR),
}

# Different thresholds for different answer types
plagiarism_thresholds = {
    "short": 0.90,      # Higher threshold for short answers as they can be more similar naturally
    "long": 0.85,       # Medium threshold for long answers
    "paraphrased": 0.80 # Lower threshold for paraphrased answers
}

def detect_question_plagiarism(answer1: str, answer2: str, answer_type: str = "short") -> float:
    """
    Detect plagiarism between two answers to the same question.
    
    Args:
        answer1: First student's answer
        answer2: Second student's answer
        answer_type: Type of answer - 'short', 'long', or 'paraphrased'
    
    Returns:
        Similarity score between the two answers
    """
    # Skip empty answers
    if not answer1 or not answer2 or answer1.strip() == '' or answer2.strip() == '':
        return 0.0
    
    # Normalize the answer type
    if answer_type not in models:
        answer_type = "short"
    
    # Select the appropriate model based on answer type
    model = models[answer_type]
    
    try:
        # Calculate embeddings
        emb1 = model.encode(answer1, convert_to_tensor=True)
        emb2 = model.encode(answer2, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = float(util.cos_sim(emb1, emb2)[0])
        
        return round(similarity, 3)
    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}")
        return 0.0


def detect_question_plagiarism_batch(question_data: List[Dict], answer_type: str = "short") -> List[Tuple[str, str, float]]:
    """
    Detect plagiarism between multiple answers to the same question.
    
    Args:
        question_data: List of dictionaries with 'submission_id' and 'answer' keys
        answer_type: Type of answer - 'short', 'long', or 'paraphrased'
    
    Returns:
        List of tuples containing (submission_id1, submission_id2, similarity_score)
    """
    # Filter out empty answers
    valid_data = [data for data in question_data if data['answer'] and data['answer'].strip() != '']
    
    if len(valid_data) < 2:
        return []
    
    submission_ids = [data['submission_id'] for data in valid_data]
    answers = [data['answer'] for data in valid_data]
    
    # Normalize the answer type
    if answer_type not in models:
        answer_type = "short"
    
    # Select the appropriate model and threshold
    model = models[answer_type]
    threshold = plagiarism_thresholds.get(answer_type, 0.85)
    
    try:
        # Calculate embeddings for all answers
        embeddings = model.encode(answers, convert_to_tensor=True)
        
        # Calculate pairwise similarities
        similarity_matrix = util.cos_sim(embeddings, embeddings).cpu().numpy()
        
        # Find pairs above threshold
        plagiarism_pairs = []
        for i in range(len(answers)):
            for j in range(i + 1, len(answers)):
                similarity = float(similarity_matrix[i][j])
                if similarity > threshold:
                    plagiarism_pairs.append((
                        submission_ids[i], 
                        submission_ids[j], 
                        round(similarity, 3)
                    ))
        
        return plagiarism_pairs
    except Exception as e:
        logger.error(f"Error in batch plagiarism detection: {str(e)}")
        return []


def compute_embeddings_bulk(texts: List[str], answer_type: str = "short"):
    """
    Compute embeddings for multiple texts in bulk.
    
    Args:
        texts: List of text strings to encode
        answer_type: Type of answer - 'short', 'long', or 'paraphrased'
    
    Returns:
        Tensor of embeddings
    """
    # Skip empty texts
    valid_texts = [text for text in texts if text and text.strip() != '']
    
    if not valid_texts:
        return None
    
    # Normalize the answer type
    if answer_type not in models:
        answer_type = "short"
    
    # Select the appropriate model
    model = models[answer_type]
    
    try:
        return model.encode(valid_texts, convert_to_tensor=True)
    except Exception as e:
        logger.error(f"Error computing embeddings: {str(e)}")
        return None


def detect_submission_plagiarism(submission_answers: Dict[str, Dict[str, str]], all_submission_answers: Dict[str, Dict[str, Dict[str, str]]]) -> Dict[str, Dict[str, float]]:
    """
    Comprehensive plagiarism detection between a submission and all other submissions,
    organized by question.
    
    Args:
        submission_answers: Dictionary mapping question_ids to {answer_type, answer_text} for the target submission
        all_submission_answers: Dictionary mapping submission_ids to dictionaries of {question_id: {answer_type, answer_text}}
    
    Returns:
        Dictionary of {submission_id: {question_id: similarity_score}}
    """
    results = {}
    
    # For each question in the submission
    for question_id, answer_data in submission_answers.items():
        answer_type = answer_data.get('answer_type', 'short')
        answer_text = answer_data.get('answer_text', '')
        
        # Skip if the answer is empty
        if not answer_text or answer_text.strip() == '':
            continue
        
        # For each other submission
        for other_id, other_submission in all_submission_answers.items():
            # Skip comparing to self
            if other_id not in results:
                results[other_id] = {}
            
            # If the other submission has an answer for this question
            if question_id in other_submission:
                other_answer = other_submission[question_id].get('answer_text', '')
                
                # Skip if the other answer is empty
                if not other_answer or other_answer.strip() == '':
                    continue
                
                # Calculate similarity
                similarity = detect_question_plagiarism(
                    answer_text, 
                    other_answer, 
                    answer_type
                )
                
                # Only record significant similarities
                threshold = plagiarism_thresholds.get(answer_type, 0.85)
                if similarity > threshold:
                    results[other_id][question_id] = similarity
    
    # Remove submissions with no significant similarities
    results = {sub_id: questions for sub_id, questions in results.items() if questions}
    
    return results