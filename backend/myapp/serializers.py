from rest_framework import serializers  
from .models import *  
from django.contrib.auth.models import User  
  

class SoftDeleteModelSerializer(serializers.ModelSerializer):
    """Сериализатор для модели SoftDeleteModel"""  
    class Meta:
        model = SoftDeleteModel
        fields = ('id', 'deleted_at', 'objects',
                  'all_objects')


class UserSerializer(serializers.ModelSerializer):  
    """Сериализатор для модели Users"""  
  
    class Meta:
        model = User
        fields = ("__all__")  

class UsersFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UsersFollows"""
    class Meta:
        model = UsersFollow
        fields = ('id', 'user_id', 'follower_id')

class SessionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Sessions"""
    class Meta:
        model = Session
        fields = ('id', 'token', 'start_time', 'finish_time');

class GlobalAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для модели GlobalAdmins"""
    class Meta:
        model = GlobalAdmin
        fields = ('id', 'user_id')

class CommunitySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Communities"""
    class Meta:
        model = Community
        fields = ('id', 'label', 'description', 'avatar_url', 
            'member_counter', 'creator_id', 'creation_date')

class CommunitiesFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CommunitiesFollows"""
    class Meta:
        model = CommunitiesFollow
        fields = ('id', 'community_id', 'follower_id')

class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Posts"""
    class Meta:
        model = Post
        fields = ('id', 'text', 'creator_id', 'community_id',
            'like_counter', 'dislike_counter')

class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comments"""
    class Meta:
        model = Comment
        fields = ('id', 'text', 'creator_id', 'post_id', 'creation_time')

class ResourcesDataSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ResourcesData"""
    class Meta:
        model = ResourcesData
        fields = ('id', 'resource_url')

class ResourcesRelationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ResourcesRelations"""
    class Meta:
        model = ResourcesRelation
        fields = ('id', 'post_id', 'comment_id', 'resource_id')

class LikeSeializer(serializers.ModelSerializer):
    """Сериализатор для модели Likes"""
    class Meta:
        model = Like
        fields = ('id', 'liker_id', 'post_id')

class DislikeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Dislikes"""
    class Meta:
        model = Dislike
        fields = ('id', 'disliker_id', 'post_id')
