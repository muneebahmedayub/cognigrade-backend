from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Theory, 
    TheorySubmission, 
    TheorySubmissionAnswer, 
    PlagiarismRecord,
    QuestionPlagiarismRecord
)
from .serializer import (
    TheorySerializer, 
    TheorySubmissionSerializer, 
    TheorySubmissionAnswerSerializer,
    PlagiarismRecordSerializer,
    QuestionPlagiarismRecordSerializer
)
from cognigrade.utils.paginations import PagePagination
from .filters import TheoryFilter, TheorySubmissionFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from cognigrade.accounts.permissions import IsSuperAdminUser, IsAdminUser, IsTeacher
from django.db import transaction
import logging

# Configure logging
logger = logging.getLogger(__name__)



class TheoryViewSet(viewsets.ModelViewSet):
    queryset = Theory.objects.all()
    serializer_class = TheorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PagePagination
    filterset_class = TheoryFilter
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'teacher':
            return qs.filter(classroom__teacher=user)
        elif user.role == 'student':
            return qs.filter(classroom__enrollments__in=[user])
        elif user.role == 'admin':
            return qs.filter(classroom__course__institution=user.institution)
        elif user.role == 'superadmin':
            return qs.all()
        return qs.none()
    
    @transaction.atomic
    @action(url_path='evaluate', detail=True, methods=['post'], permission_classes=[IsSuperAdminUser|IsAdminUser|IsTeacher])
    def evaluate(self, request, *args, **kwargs):
        theory = self.get_object()
        submissions = TheorySubmission.objects.filter(theory=theory)
        if submissions.count() == 0:
            return Response({'error': 'No submissions found'}, status=status.HTTP_400_BAD_REQUEST)
        for submission in submissions:
            submission.evaluate()
            submission.save()
        return Response({'message': 'Submissions evaluated', 'submissions': TheorySubmissionSerializer(submissions, many=True).data}, status=status.HTTP_200_OK)
    
    @transaction.atomic
    @action(url_path='check-plagiarism', detail=True, methods=['post'], permission_classes=[IsSuperAdminUser|IsAdminUser|IsTeacher])
    def check_plagiarism(self, request, *args, **kwargs):
        """Check for plagiarism across all submissions of a theory"""
        theory = self.get_object()
        
        # Log which theory is being checked
        logger.info(f"Checking plagiarism for theory: {theory.id} - {theory.title}")
        
        submissions = TheorySubmission.objects.filter(theory=theory)
        if submissions.count() < 2:
            logger.warning(f"Not enough submissions for theory {theory.id}: {submissions.count()}")
            return Response({'error': 'Need at least 2 submissions to check for plagiarism'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        # Get thresholds from request data
        thresholds = {
            'default': request.data.get('default_threshold', 0.85),
            'short': request.data.get('short_threshold', 0.90),
            'long': request.data.get('long_threshold', 0.85),
            'paraphrased': request.data.get('paraphrased_threshold', 0.80)
        }
        
        # Log thresholds for debugging
        logger.info(f"Using thresholds: {thresholds}")
        
        # Validate thresholds
        for key, value in thresholds.items():
            try:
                thresholds[key] = float(value)
                if not (0 <= thresholds[key] <= 1):
                    logger.error(f"Invalid threshold value for {key}: {value}")
                    return Response({
                        'error': f'Threshold {key} must be between 0 and 1'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                logger.error(f"Invalid threshold value for {key}: {value}")
                return Response({
                    'error': f'Invalid threshold value for {key}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # First, clear all existing plagiarism records for this theory
        # This will cascade delete related QuestionPlagiarismRecords due to on_delete=CASCADE
        logger.info(f"Deleting existing plagiarism records for theory {theory.id}")
        
        # Delete records where either submission1 or submission2 is from this theory
        deleted_count1 = PlagiarismRecord.objects.filter(submission1__theory=theory).delete()
        deleted_count2 = PlagiarismRecord.objects.filter(submission2__theory=theory).delete()
        
        logger.info(f"Deleted {deleted_count1[0] + deleted_count2[0]} existing plagiarism records")
        
        # Check each submission for plagiarism with the specified thresholds
        logger.info(f"Processing {submissions.count()} submissions")
        for submission in submissions:
            logger.info(f"Checking submission {submission.id} for student {submission.student.email}")
            submission.check_plagiarism(thresholds=thresholds)
        
        # Get all plagiarism records for this theory
        plagiarism_records = PlagiarismRecord.objects.filter(
            models.Q(submission1__theory=theory) | models.Q(submission2__theory=theory)
        ).prefetch_related('question_records')
        
        logger.info(f"Found {plagiarism_records.count()} plagiarism records")
        
        return Response({
            'theory_id': theory.id,
            'theory_title': theory.title,
            'thresholds_used': thresholds,
            'total_records': plagiarism_records.count(),
            'plagiarism_results': PlagiarismRecordSerializer(plagiarism_records, many=True).data
        }, status=status.HTTP_200_OK)

    @action(url_path='plagiarism-records', detail=True, methods=['get'], permission_classes=[IsSuperAdminUser|IsAdminUser|IsTeacher])
    def get_plagiarism_records(self, request, *args, **kwargs):
        """Get all plagiarism records for a theory"""
        theory = self.get_object()
        
        plagiarism_records = PlagiarismRecord.objects.filter(
            submission1__theory=theory
        ).prefetch_related('question_records').order_by('-similarity_score')
        
        # Add filtering for specific students if provided
        student_id = request.query_params.get('student_id')
        if student_id:
            plagiarism_records = plagiarism_records.filter(
                models.Q(submission1__student_id=student_id) | 
                models.Q(submission2__student_id=student_id)
            )
        
        # Add threshold filtering if provided
        threshold = request.query_params.get('threshold')
        if threshold:
            try:
                threshold = float(threshold)
                plagiarism_records = plagiarism_records.filter(similarity_score__gte=threshold)
            except ValueError:
                pass
        
        return Response({
            'theory_id': theory.id,
            'theory_title': theory.title,
            'plagiarism_results': PlagiarismRecordSerializer(plagiarism_records, many=True).data
        }, status=status.HTTP_200_OK)
    
    @action(url_path='student-plagiarism', detail=True, methods=['get'], permission_classes=[IsSuperAdminUser|IsAdminUser|IsTeacher])
    def get_student_plagiarism(self, request, *args, **kwargs):
        """Get plagiarism summary for each student in the theory"""
        theory = self.get_object()
        student_id = request.query_params.get('student_id')
        
        if student_id:
            # Get submissions for this student
            submissions = TheorySubmission.objects.filter(
                theory=theory,
                student_id=student_id
            )
            
            if not submissions.exists():
                return Response({'error': 'No submissions found for this student'}, 
                              status=status.HTTP_404_NOT_FOUND)
            
            # Get all plagiarism records involving this student
            plagiarism_records = PlagiarismRecord.objects.filter(
                models.Q(submission1__student_id=student_id, submission1__theory=theory) | 
                models.Q(submission2__student_id=student_id, submission2__theory=theory)
            ).prefetch_related('question_records').order_by('-similarity_score')
            
            return Response({
                'student_id': student_id,
                'theory_id': theory.id,
                'theory_title': theory.title,
                'plagiarism_records': PlagiarismRecordSerializer(plagiarism_records, many=True).data
            }, status=status.HTTP_200_OK)
        else:
            # Get all students with submissions for this theory
            submissions = TheorySubmission.objects.filter(theory=theory)
            
            student_summaries = []
            for submission in submissions:
                # Get the highest plagiarism score for this student
                highest_score = PlagiarismRecord.objects.filter(
                    models.Q(submission1=submission) | models.Q(submission2=submission)
                ).aggregate(max_score=models.Max('similarity_score'))['max_score'] or 0
                
                # Count how many questions have significant plagiarism
                question_count = QuestionPlagiarismRecord.objects.filter(
                    plagiarism_record__in=PlagiarismRecord.objects.filter(
                        models.Q(submission1=submission) | models.Q(submission2=submission)
                    )
                ).count()
                
                student_summaries.append({
                    'student_id': submission.student.id,
                    'student_name': submission.student.get_full_name or submission.student.email,
                    'highest_plagiarism_score': highest_score,
                    'questions_with_plagiarism': question_count,
                    'submission_id': submission.id
                })
            
            # Sort by highest plagiarism score
            student_summaries.sort(key=lambda x: x['highest_plagiarism_score'], reverse=True)
            
            return Response({
                'theory_id': theory.id,
                'theory_title': theory.title,
                'student_plagiarism_summary': student_summaries
            }, status=status.HTTP_200_OK)
    
    
class TheorySubmissionViewSet(viewsets.ModelViewSet):
    queryset = TheorySubmission.objects.all()
    serializer_class = TheorySubmissionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PagePagination
    filterset_class = TheorySubmissionFilter

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'student':
            return qs.filter(student=user)
        elif user.role == 'teacher':
            return qs.filter(theory__classroom__teacher=user)
        elif user.role == 'admin':
            return qs.filter(theory__classroom__course__institution=user.institution)
        elif user.role == 'superadmin':
            return qs.all()
        return qs.none()
    
    @action(url_path='check-single-submission-plagiarism', detail=True, methods=['post'], permission_classes=[IsSuperAdminUser|IsAdminUser|IsTeacher])
    def check_single_submission_plagiarism(self, request, *args, **kwargs):
        """Check a single submission for plagiarism against all other submissions"""
        submission = self.get_object()
        
        # Find other submissions for the same theory
        other_submissions = TheorySubmission.objects.filter(
            theory=submission.theory
        ).exclude(id=submission.id)
        
        if not other_submissions.exists():
            return Response({'error': 'No other submissions found for comparison'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Get thresholds from request data
        thresholds = {
            'default': request.data.get('default_threshold', 0.85),
            'short': request.data.get('short_threshold', 0.90),
            'long': request.data.get('long_threshold', 0.85),
            'paraphrased': request.data.get('paraphrased_threshold', 0.80)
        }
        
        # Validate thresholds
        for key, value in thresholds.items():
            try:
                thresholds[key] = float(value)
                if not (0 <= thresholds[key] <= 1):
                    return Response({
                        'error': f'Threshold {key} must be between 0 and 1'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({
                    'error': f'Invalid threshold value for {key}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete existing plagiarism records for this submission
        PlagiarismRecord.objects.filter(
            models.Q(submission1=submission) | models.Q(submission2=submission)
        ).delete()
        
        # Check for plagiarism
        submission.check_plagiarism(thresholds=thresholds)
        
        # Get plagiarism records involving this submission
        plagiarism_records = PlagiarismRecord.objects.filter(
            models.Q(submission1=submission) | models.Q(submission2=submission)
        ).prefetch_related('question_records')
        
        return Response({
            'submission_id': submission.id,
            'student_name': submission.student.get_full_name or submission.student.email,
            'theory_id': submission.theory.id,
            'theory_title': submission.theory.title,
            'thresholds_used': thresholds,
            'plagiarism_records': PlagiarismRecordSerializer(plagiarism_records, many=True).data
        }, status=status.HTTP_200_OK)