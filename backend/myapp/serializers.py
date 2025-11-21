from rest_framework import serializers  
from .models import Profile, Category, Post, Comment  
from django.contrib.auth.models import User  
  

class SoftDeleteModelSerializer(serializers.ModelSerializer):
    """Сериализатор для модели SoftDeleteModel"""  
    class Meta:
        model = SoftDeleteModel
        fields = ('is_deleted', 'deleted_at', 'objects',
                  'all_objects')


class UsersSerializer(serializers.ModelSerializer):  
    """Сериализатор для модели Users"""  
  
    class Meta:
        model = Users
        fields = ('user_id', 'username', 'visible_name',
                'email', 'bio', 'follower_counter', 'avatar_url',
                'birthday', 'registration_day', 'password_hash')  

class UsersFollowsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UsersFollows"""
    class Meta:
        model = UsersFollows
        fields = ('follow_id', 'user_id', 'follower_id')

class SessionsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Sessions"""
    class Meta:
        model = Sessions
        fields = ('session_id', 'token', 'start_time', 'finish_time');

class GlobalAdminsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели GlobalAdmins"""
    class Meta:
        model = GlobalAdmins
        fields = ('admin_id', 'user_id')

class CommunitiesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Communities"""
    class Meta:
        model = Communities
        fields = ('community_id', 'label', 'description', 'avatar_url', 
            'member_counter', 'creator_id', 'creation_date')

class CommunitiesFollowsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CommunitiesFollows"""
    class Meta:
        model = CommunitiesFollows
        fields = ('follow_id', 'community_id', 'follower_id')

class PostsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Posts"""
    class Meta:
        model = Posts
        fields = ('post_id', 'text', 'creator_id', 'community_id',
            'like_counter', 'dislike_counter')

