from rest_framework import serializers
from .models import Course, Classroom
from cognigrade.accounts.models import User
from cognigrade.institutions.models import Institutions
from django.db import transaction, models
from cognigrade.accounts.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(queryset=Institutions.objects.all())
    class Meta:
        model = Course
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        if user.is_superuser or user.is_admin:
            data['total_classrooms'] = instance.classrooms.count()
            data['total_students'] = instance.classrooms.aggregate(total_students=models.Count('enrollments'))['total_students']
        elif user.is_teacher:
            teacher_classrooms = instance.classrooms.filter(teacher=user)
            data['total_classrooms'] = teacher_classrooms.count()
            data['total_students'] = teacher_classrooms.aggregate(total_students=models.Count('enrollments'))['total_students']
        elif user.is_student:
            student_classrooms = instance.classrooms.filter(enrollments=user)
            data['total_classrooms'] = student_classrooms.count()
            data['total_students'] = student_classrooms.aggregate(total_students=models.Count('enrollments'))['total_students']
        return data


class ClassroomSerializer(serializers.ModelSerializer):
    enrollments = serializers.ListField(source="enrollments.all",child=serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='student')), required=False)
    
    @transaction.atomic
    def create(self, validated_data):
        enrollments = validated_data.pop('enrollments') if 'enrollments' in validated_data else None
        classroom = super().create(validated_data)
        if enrollments:
            classroom.enrollments.set(enrollments['all'])
        return classroom

    @transaction.atomic
    def update(self, instance, validated_data):
        enrollments = validated_data.pop('enrollments') if 'enrollments' in validated_data else None
        classroom = super().update(instance, validated_data)
        if enrollments:
            classroom.enrollments.set(enrollments['all'])
        return classroom
    

    class Meta:
        model = Classroom
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['enrollments'] = UserSerializer(instance.enrollments.all(), many=True).data
        data['course'] = CourseSerializer(instance.course, context={'request': self.context['request']}).data
        data['teacher'] = UserSerializer(instance.teacher, context={'request': self.context['request']}).data
        return data
    
