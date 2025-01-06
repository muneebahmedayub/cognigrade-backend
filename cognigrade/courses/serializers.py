from rest_framework import serializers
from .models import Course, Classroom
from cognigrade.accounts.models import User
from cognigrade.institutions.models import Institutions
from django.db import transaction
from cognigrade.accounts.serializers import UserSerializer
class CourseSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(queryset=Institutions.objects.all())
    class Meta:
        model = Course
        fields = '__all__'


class ClassroomSerializer(serializers.ModelSerializer):
    enrollments = serializers.ListField(source="enrollments.all",child=serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='student')))
    
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
        return data
    
