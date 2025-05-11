from django.db import models
from cognigrade.utils.models import BaseModel
from cognigrade.courses.models import Classroom
from cognigrade.accounts.models import User
from cognigrade.utils.evaluation import grade_answer_proc
from cognigrade.utils.plagiarism import detect_question_plagiarism

class TheoryType(models.TextChoices):
    ASSIGNMENT = 'assignment'
    QUIZ = 'quiz'
    EXAM = 'exam'

class AnswerType(models.TextChoices):
    SHORT = 'short'
    LONG = 'long'
    PARAPHRASED = 'paraphrased'

class Theory(BaseModel):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TheoryType.choices)


class TheoryQuestions(BaseModel):
    theory = models.ForeignKey(Theory, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    answer = models.TextField()
    options = models.JSONField(default=list)
    marks = models.IntegerField(default=0)
    answer_type = models.CharField(max_length=255, choices=AnswerType.choices, default=AnswerType.SHORT)

class TheorySubmission(BaseModel):
    theory = models.ForeignKey(Theory, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    score = models.IntegerField(default=0)
    # Overall plagiarism score for the entire submission
    plagiarism_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.theory.title}"
    
    def evaluate(self):
        self.score = 0
        for answer in self.answers.all():
            grade, similarity = grade_answer_proc(answer.answer, answer.question.answer, answer.question.answer_type)
            answer.marks = similarity * answer.question.marks
            answer.save()
            self.score += answer.marks
            
        self.save()
    
    def check_plagiarism(self, thresholds=None):
        """
        Check for plagiarism against other submissions for the same theory
        
        Args:
            thresholds: Dictionary with thresholds for different answer types
                        Example: {'short': 0.9, 'long': 0.85, 'paraphrased': 0.8}
        """
        # Default thresholds if none provided
        if thresholds is None:
            thresholds = {
                'short': 0.9,
                'long': 0.85,
                'paraphrased': 0.8
            }
        
        # Get the default threshold (used for the PlagiarismRecord)
        default_threshold = thresholds.get('default', 0.85)
        
        other_submissions = TheorySubmission.objects.filter(
            theory=self.theory
        ).exclude(id=self.id)
        
        # Delete existing plagiarism records involving this submission
        plagiarism_records = PlagiarismRecord.objects.filter(
            models.Q(submission1=self) | models.Q(submission2=self)
        )
        
        # This will cascade delete related QuestionPlagiarismRecords due to on_delete=CASCADE
        plagiarism_records.delete()
        
        # Track detected plagiarism for each other submission
        submission_plagiarism = {}
        
        # Compare each question's answer with the corresponding answers from other submissions
        for question in self.theory.questions.all():
            # Get this student's answer to the current question
            try:
                student_answer = TheorySubmissionAnswer.objects.get(
                    submission=self,
                    question=question
                )
            except TheorySubmissionAnswer.DoesNotExist:
                continue
                
            # Skip if the answer is empty
            if not student_answer.answer or student_answer.answer.strip() == '':
                continue
            
            # Get the threshold for this answer type
            answer_type = question.answer_type
            threshold = thresholds.get(answer_type, default_threshold)
                
            for other_submission in other_submissions:
                # Initialize tracking for this submission if needed
                if other_submission.id not in submission_plagiarism:
                    submission_plagiarism[other_submission.id] = {
                        'submission': other_submission,
                        'max_similarity': 0.0,
                        'question_similarities': []
                    }
                
                # Get the other student's answer to the same question
                try:
                    other_answer = TheorySubmissionAnswer.objects.get(
                        submission=other_submission,
                        question=question
                    )
                except TheorySubmissionAnswer.DoesNotExist:
                    continue
                    
                # Skip if the other answer is empty
                if not other_answer.answer or other_answer.answer.strip() == '':
                    continue
                
                # Calculate similarity for this specific question
                similarity = detect_question_plagiarism(
                    student_answer.answer, 
                    other_answer.answer,
                    question.answer_type
                )
                
                # If similarity is above threshold, track it
                if similarity > threshold:
                    submission_plagiarism[other_submission.id]['question_similarities'].append({
                        'question': question,
                        'similarity': similarity
                    })
                    
                    # Update max similarity
                    if similarity > submission_plagiarism[other_submission.id]['max_similarity']:
                        submission_plagiarism[other_submission.id]['max_similarity'] = similarity
        
        # Create plagiarism records for submissions that had similarities above threshold
        overall_max_similarity = 0.0
        
        for sub_id, data in submission_plagiarism.items():
            if data['question_similarities']:
                other_submission = data['submission']
                max_similarity = data['max_similarity']
                
                # Update overall max similarity for this submission
                overall_max_similarity = max(overall_max_similarity, max_similarity)
                
                # Ensure consistent ordering of submissions
                submission1 = self if self.id < other_submission.id else other_submission
                submission2 = other_submission if self.id < other_submission.id else self
                
                # Create the main plagiarism record
                plagiarism_record = PlagiarismRecord.objects.create(
                    submission1=submission1,
                    submission2=submission2,
                    similarity_score=max_similarity,
                    threshold_used=default_threshold
                )
                
                # Create question-level plagiarism records
                for question_data in data['question_similarities']:
                    QuestionPlagiarismRecord.objects.create(
                        plagiarism_record=plagiarism_record,
                        question=question_data['question'],
                        similarity_score=question_data['similarity']
                    )
        
        # Update the overall plagiarism score for this submission
        if overall_max_similarity > 0:
            self.plagiarism_score = overall_max_similarity
            self.save()


class TheorySubmissionAnswer(BaseModel):
    submission = models.ForeignKey(TheorySubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(TheoryQuestions, on_delete=models.CASCADE, related_name='answers')
    answer = models.TextField()
    marks = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.submission.student.name} - {self.question.question}"
    
    def save(self, *args, **kwargs):
        if self.answer is None:
            self.answer = ''
        super().save(*args, **kwargs)


class PlagiarismRecord(BaseModel):
    """Records overall plagiarism between two submissions"""
    submission1 = models.ForeignKey(TheorySubmission, on_delete=models.CASCADE, related_name='plagiarism_as_submission1')
    submission2 = models.ForeignKey(TheorySubmission, on_delete=models.CASCADE, related_name='plagiarism_as_submission2')
    similarity_score = models.FloatField()
    # Track the threshold that was used to detect this plagiarism
    threshold_used = models.FloatField(default=0.85)
    
    class Meta:
        unique_together = ('submission1', 'submission2')
    
    def __str__(self):
        return f"Plagiarism between {self.submission1.student.name} and {self.submission2.student.name} ({self.similarity_score:.2f})"


class QuestionPlagiarismRecord(BaseModel):
    """Records plagiarism for specific questions within a plagiarism record"""
    # Link to the parent plagiarism record
    plagiarism_record = models.ForeignKey(PlagiarismRecord, on_delete=models.CASCADE, related_name='question_records')
    # The question that had plagiarism
    question = models.ForeignKey(TheoryQuestions, on_delete=models.CASCADE, related_name='plagiarism_records')
    # Similarity score for this specific question
    similarity_score = models.FloatField()
    
    class Meta:
        unique_together = ('plagiarism_record', 'question')
    
    def __str__(self):
        return f"Question plagiarism for {self.question.question[:30]}... ({self.similarity_score:.2f})"