from rest_framework import serializers
from .models import Theory, TheoryQuestions
from django.db import transaction

class TheoryQuestionsSerializer(serializers.ModelSerializer):
    theory = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    class Meta:
        model = TheoryQuestions
        fields = '__all__'

class TheorySerializer(serializers.ModelSerializer):
    questions = TheoryQuestionsSerializer(many=True)
    class Meta:
        model = Theory
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        questions = validated_data.pop('questions') if 'questions' in validated_data else None
        theory = super().create(validated_data)
        keep_questions = []
        for question in questions:
            keep_questions.append(TheoryQuestions.objects.create(theory=theory, **question))
        theory.questions.set(keep_questions)
        theory.save()

        return theory
    
    @transaction.atomic
    def update(self, instance, validated_data):
        questions = validated_data.pop('questions') if 'questions' in validated_data else None
        theory = super().update(instance, validated_data)
        if questions is None:
            return theory
        
        keep_questions = []
        for question in questions:
            keep_questions.append(TheoryQuestions.objects.create(theory=theory, **question))

        theory.questions.set(keep_questions)
        theory.save()
        for question in instance.questions.all():
            if question not in keep_questions:
                question.delete()

        theory.save()
        return theory
    