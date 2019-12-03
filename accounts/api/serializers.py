from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password
from accounts.models import User, UserBalance, UserAddress
from django_dbcache_fields.decorators import dbcache
from django.db import models


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    full_name = serializers.CharField(max_length=32,)
    password = serializers.CharField(min_length=8, max_length=100, write_only=True)
    confirm_password = serializers.CharField(min_length=8, max_length=100, write_only=True)

    class Meta:
        model = User
        fields = ("id", "full_name", "email", "password", "confirm_password", "date_joined")
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=make_password(validated_data['password']))
        return user

    def validate(self, attrs):
        """ Make sure Passwords match"""
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Those passwords don't match.")
        return attrs


class UserBalanceSerializer(serializers.ModelSerializer):
    queryset = UserBalance.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set

    class Meta:
        model = UserBalance
        fields = ['balance']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    user_balance = serializers.SerializerMethodField('get_user_balance')
    refill = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='refill-detail')
    cash_call = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='cashcall-detail')

    class Meta:
        model = User
        fields = ['url', 'id', 'email', 'full_name', 'user_balance', 'date_joined', 'refill', 'cash_call']
        read_only_fields = ['email', 'full_name', 'is_active', 'user_balance']

    def get_user_balance(self, obj):
        user = obj
        return user.user_balance.get().balance


class UserAddressSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserAddress
        fields = ['user', 'url', 'street_address', 'city', 'state', 'country']
