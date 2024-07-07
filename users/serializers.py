from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organisation

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('userId', 'firstName', 'lastName', 'email', 'phone')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('firstName', 'lastName', 'email', 'password', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            password=validated_data['password'],
            phone=validated_data['phone']
        )
        # pylint: disable=no-member
        organisation = Organisation.objects.create(
            name=f"{validated_data['firstName']}'s Organisation",
            description=f"This is {validated_data['firstName']}'s Organisation",
        )
        organisation.users.add(user)
        return user


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ('orgId', 'name', 'description')
