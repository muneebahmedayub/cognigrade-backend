from django.db import models
from cognigrade.utils.models import BaseModel
from cognigrade.courses.models import Classroom
from cognigrade.accounts.models import User
from cognigrade.utils.evaluation import grade_answer_proc
from cognigrade.utils.plagiarism import detect_plagiarism_proc

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

    def __str__(self):
        return f"{self.student.name} - {self.theory.title}"
    
    def evaluate(self):
        for answer in self.answers.all():
            grade, similarity = grade_answer_proc(answer.answer, answer.question.answer, answer.question.answer_type)
            print(grade, similarity)
            answer.marks = similarity * answer.question.marks
            answer.save()
            self.score += answer.marks
            
        self.save()
    
    def check_plagiarism(self):
        """Check for plagiarism against other submissions of the same theory"""
    
        other_submissions = TheorySubmission.objects.filter(
            theory=self.theory
        ).exclude(id=self.id)
        
        student_answers = []
        
        for answer in self.answers.all():
            student_answers.append({
                'student_id': str(self.id),
                'answer': answer.answer
            })
        
        for submission in other_submissions:
            for answer in submission.answers.all():
                student_answers.append({
                    'student_id': str(submission.id),
                    'answer': answer.answer
                })
        
        cheating_pairs = detect_plagiarism_proc(student_answers)
        
        for student1_id, student2_id, similarity in cheating_pairs:
            if str(self.id) in [student1_id, student2_id]:
                submission1_id = min(int(student1_id), int(student2_id))
                submission2_id = max(int(student1_id), int(student2_id))
                
                PlagiarismRecord.objects.update_or_create(
                    submission1_id=submission1_id,
                    submission2_id=submission2_id,
                    defaults={'similarity_score': similarity}
                )
                
        if cheating_pairs:
            self.plagiarism_score = max(score for _, _, score in cheating_pairs)
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
    submission1 = models.ForeignKey(TheorySubmission, on_delete=models.CASCADE, related_name='plagiarism_as_submission1')
    submission2 = models.ForeignKey(TheorySubmission, on_delete=models.CASCADE, related_name='plagiarism_as_submission2')
    similarity_score = models.FloatField()
    
    class Meta:
        unique_together = ('submission1', 'submission2')
    
    def __str__(self):
        return f"Plagiarism between {self.submission1.student.name} and {self.submission2.student.name} ({self.similarity_score:.2f})"
