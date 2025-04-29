from rest_framework import serializers
from .models import Theory, TheoryQuestions, TheorySubmission, TheorySubmissionAnswer
from django.db import transaction

class TheoryQuestionsSerializer(serializers.ModelSerializer):
    theory = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    class Meta:
        model = TheoryQuestions
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        if user.role == 'student':
            data['answer'] = None
        return data

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
        

class TheorySubmissionAnswerSerializer(serializers.ModelSerializer):
    submission = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    class Meta:
        model = TheorySubmissionAnswer
        fields = '__all__'


class TheorySubmissionSerializer(serializers.ModelSerializer):
    answers = TheorySubmissionAnswerSerializer(many=True)
    student = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    class Meta:
        model = TheorySubmission
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        answers = validated_data.pop('answers') if 'answers' in validated_data else None
        user = self.context['request'].user
        validated_data['student'] = user
        submission = super().create(validated_data)
        print(answers)
        if answers is None:
            return submission
        
        keep_answers = []
        for answer in answers:
            keep_answers.append(TheorySubmissionAnswer.objects.create(submission=submission, **answer))
        submission.answers.set(keep_answers)
        submission.save()
        return submission
    
    @transaction.atomic
    def update(self, instance, validated_data):
        answers = validated_data.pop('answers') if 'answers' in validated_data else None
        submission = super().update(instance, validated_data)
        if answers is None:
            return submission

        keep_answers = []
        for answer in answers:
            keep_answers.append(TheorySubmissionAnswer.objects.create(submission=submission, **answer))

        submission.answers.set(keep_answers)
        submission.save()
        return submission
    