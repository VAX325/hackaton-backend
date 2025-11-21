from rest_framework import serializers  
from .models import Profile, Category, Post, Comment  
from django.contrib.auth.models import User  
  
class UsersSerializer(serializers.ModelSerializer):  
    """Сериализатор для модели Users"""  
  
    class Meta:  
        model = Users
        fields = ('username', 'visible_name', 'email', 'password_hash')  
  
