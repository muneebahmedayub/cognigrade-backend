from rest_framework import serializers
from .models import OMR, OMRQuestions


class OMRQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OMRQuestions
        fields = '__all__'

class OMRSerializer(serializers.ModelSerializer):
    questions = OMRQuestionsSerializer(many=True)
    class Meta:
        model = OMR
        fields = '__all__'

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        omr = OMR.objects.create(**validated_data)
        keep_questions = []
        for question in questions:
            keep_questions.append(OMRQuestions.objects.create(omr=omr, **question))
        omr.questions.set(keep_questions)
        omr.save()

        return omr