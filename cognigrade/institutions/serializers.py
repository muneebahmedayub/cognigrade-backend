from rest_framework import serializers
from .models import Institutions

class InstitutionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Institutions
        fields = '__all__'
