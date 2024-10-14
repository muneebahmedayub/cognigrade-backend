from rest_framework import serializers
from .models import User
from .choices import RoleChoices


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'role',
            'email',
            'password',
            'institution',
            'is_active',
            'is_deleted',
            'deleted_on',
            'deleted_by',
        ]
        read_only_fields = ['is_deleted', 'deleted_on', 'deleted_by']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
        
