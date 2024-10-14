from rest_framework import serializers
from .models import Institutions
from cognigrade.accounts.models import User
from django.db import transaction
from cognigrade.accounts.choices import RoleChoices

class InstitutionsSerializers(serializers.ModelSerializer):
    admins = serializers.PrimaryKeyRelatedField(many=True, write_only=True, queryset=User.objects.filter(role=RoleChoices.ADMIN))
    class Meta:
        model = Institutions
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data, **kwargs):
        admins = validated_data.pop('admins', [])
        institution = super(InstitutionsSerializers, self).create(validated_data, **kwargs)
        institution.institution_user.set(admins)
        return institution

    @transaction.atomic
    def update(self, instance, validated_data, **kwargs):
        admins = validated_data.pop('admins', [])
        institution = super(InstitutionsSerializers, self).update(instance, validated_data, **kwargs)
        
        institution.institution_user.set(admins)
        return institution