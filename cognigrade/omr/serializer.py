from rest_framework import serializers
from .models import OMR, OMRQuestions
from django.db import transaction

class OMRQuestionsSerializer(serializers.ModelSerializer):
    omr = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    class Meta:
        model = OMRQuestions
        fields = '__all__'

class OMRSerializer(serializers.ModelSerializer):
    questions = OMRQuestionsSerializer(many=True)
    class Meta:
        model = OMR
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        questions = validated_data.pop('questions') if 'questions' in validated_data else None
        omr = super().create(validated_data)
        keep_questions = []
        for question in questions:
            keep_questions.append(OMRQuestions.objects.create(omr=omr, **question))
        omr.questions.set(keep_questions)
        omr.save()

        return omr
    
    @transaction.atomic
    def update(self, instance, validated_data):
        questions = validated_data.pop('questions') if 'questions' in validated_data else None
        omr = super().update(instance, validated_data)
        keep_questions = []
        for question in questions:
            keep_questions.append(OMRQuestions.objects.create(omr=omr, **question))

        omr.questions.set(keep_questions)
        omr.save()
        for question in instance.questions.all():
            if question not in keep_questions:
                question.delete()

        omr.save()
        return omr
    