from rest_framework import serializers  
from .models import Profile, Category, Post, Comment  
from django.contrib.auth.models import User  
  
class UsersSerializer(serializers.ModelSerializer):  
    """Сериализатор для модели Users"""  
  
    class Meta:  
        model = User
        fields = ('user_id', 'username', 'visible_name',
                'email', 'bio', 'follower_counter', 'avatar_url',
                'birthday', 'registration_day', 'password_hash')  
