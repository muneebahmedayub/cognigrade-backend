from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Theory, TheorySubmission, TheorySubmissionAnswer, PlagiarismRecord
from .serializer import TheorySerializer, TheorySubmissionSerializer, TheorySubmissionAnswerSerializer
from cognigrade.utils.paginations import PagePagination
from .filters import TheoryFilter, TheorySubmissionFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from cognigrade.accounts.permissions import IsSuperAdminUser, IsAdminUser, IsTeacher
from django.db import transaction


# Create your views here.
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
        return Response({'message': 'Submissions evaluated'}, status=status.HTTP_200_OK)
    
    @transaction.atomic
    @action(url_path='check-plagiarism', detail=True, methods=['post'], permission_classes=[IsSuperAdminUser|IsAdminUser|IsTeacher])
    def check_plagiarism(self, request, *args, **kwargs):
        """Check for plagiarism across all submissions of a theory"""
        theory = self.get_object()
        
        submissions = TheorySubmission.objects.filter(theory=theory)
        if submissions.count() < 2:
            return Response({'error': 'Need at least 2 submissions to check for plagiarism'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        plagiarism_results = []
        processed_pairs = set() 
        
        for submission in submissions:
            plagiarism_records = PlagiarismRecord.objects.filter(
                models.Q(submission1=submission) | models.Q(submission2=submission)
            )
            
            for record in plagiarism_records:
                pair_key = tuple(sorted([record.submission1_id, record.submission2_id]))
                if pair_key not in processed_pairs:
                    processed_pairs.add(pair_key)
                    plagiarism_results.append({
                        'student1': record.submission1.student.get_full_name or record.submission1.student.username,
                        'student2': record.submission2.student.get_full_name or record.submission2.student.username,
                        'similarity_score': record.similarity_score,
                    })
            
            submission.check_plagiarism()
            
            updated_records = PlagiarismRecord.objects.filter(
                models.Q(submission1=submission) | models.Q(submission2=submission)
            )
            
            for record in updated_records:
                pair_key = tuple(sorted([record.submission1_id, record.submission2_id]))
                if pair_key not in processed_pairs:
                    processed_pairs.add(pair_key)
                    plagiarism_results.append({
                        'student1': record.submission1.student.get_full_name or record.submission1.student.username,
                        'student2': record.submission2.student.get_full_name or record.submission2.student.username,
                        'similarity_score': record.similarity_score,
                    })
        
        return Response({
            'theory_id': theory.id,
            'theory_title': theory.title,
            'plagiarism_results': plagiarism_results
        }, status=status.HTTP_200_OK)
    
    @action(url_path='plagiarism-records', detail=True, methods=['get'], permission_classes=[IsSuperAdminUser|IsAdminUser|IsTeacher])
    def get_plagiarism_records(self, request, *args, **kwargs):
        """Get all plagiarism records for a theory"""
        theory = self.get_object()
        
        plagiarism_records = PlagiarismRecord.objects.filter(
            models.Q(submission1__theory=theory) | models.Q(submission2__theory=theory)
        )
        
        plagiarism_results = []
        for record in plagiarism_records:
            plagiarism_results.append({
                'student1': record.submission1.student.get_full_name or record.submission1.student.username,
                'student2': record.submission2.student.get_full_name or record.submission2.student.username,
                'similarity_score': record.similarity_score,
            })
        
        return Response({
            'theory_id': theory.id,
            'theory_title': theory.title,
            'plagiarism_results': plagiarism_results
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
    