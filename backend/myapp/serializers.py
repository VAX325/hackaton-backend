from rest_framework import serializers  
from .models import *  
from django.contrib.auth.models import User  
  

class SoftDeleteModelSerializer(serializers.ModelSerializer):
    """Сериализатор для модели SoftDeleteModel"""  
    class Meta:
        model = SoftDeleteModel
        fields = ('id', 'deleted_at', 'objects',
                  'all_objects')


class UsersSerializer(serializers.ModelSerializer):  
    """Сериализатор для модели Users"""  
  
    class Meta:
        model = Users
        fields = ('id', 'username', 'visible_name',
                'email', 'bio', 'follower_counter', 'avatar_url',
                'birthday', 'registration_day', 'password_hash')  

class UsersFollowsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UsersFollows"""
    class Meta:
        model = UsersFollows
        fields = ('id', 'user_id', 'follower_id')

class SessionsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Sessions"""
    class Meta:
        model = Sessions
        fields = ('id', 'token', 'start_time', 'finish_time');

class GlobalAdminsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели GlobalAdmins"""
    class Meta:
        model = GlobalAdmins
        fields = ('id', 'user_id')

class CommunitiesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Communities"""
    class Meta:
        model = Communities
        fields = ('id', 'label', 'description', 'avatar_url', 
            'member_counter', 'creator_id', 'creation_date')

class CommunitiesFollowsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CommunitiesFollows"""
    class Meta:
        model = CommunitiesFollows
        fields = ('id', 'community_id', 'follower_id')

class PostsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Posts"""
    class Meta:
        model = Posts
        fields = ('id', 'text', 'creator_id', 'community_id',
            'like_counter', 'dislike_counter')

class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comments"""
    class Meta:
        model = Comments
        fields = ('id', 'text', 'creator_id', 'post_id', 'creatoin_time')

class ResourcesDataSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ResourcesData"""
    class Meta:
        model = ResourcesData
        fields = ('id', 'resource_url')

class RecourcesRelationsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ResourcesRelations"""
    class Meta:
        model = ResourcesRelations
        fields = ('id', 'post_id', 'comment_id', 'resource_id')

class LikesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Likes"""
    class Meta:
        model = Likes
        fields = ('id', 'liker_id', 'post_id')

class DislikesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Dislikes"""
    class Meta:
        model = Dislikes
        fields = ('id', 'disliker_id', 'post_id')
