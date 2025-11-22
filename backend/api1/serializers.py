from django.contrib.auth.models import User
from rest_framework import serializers

from .models import *


class SoftDeleteModelSerializer(serializers.ModelSerializer):
    """Сериализатор для модели SoftDeleteModel"""

    class Meta:
        model = SoftDeleteModel
        fields = ("id", "deleted_at", "objects", "all_objects")


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Users"""

    class Meta:
        model = User
        fields = [
            "username",
            "visible_name",
            "bio",
            "follower_counter",
            "avatar_url",
            "birthday",
            "registration_day",
            "last_login",
            "likes",
            "dislikes",
        ]


class GlobalAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для модели GlobalAdmins"""

    user = UserSerializer()

    class Meta:
        model = GlobalAdmin
        fields = ("id", "user")


class CommunitySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Communities"""

    creator = UserSerializer()

    class Meta:
        model = Community
        fields = (
            "id",
            "label",
            "description",
            "avatar_url",
            "member_counter",
            "creator",
            "creation_date",
        )


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Posts"""

    creator = UserSerializer()
    community = CommunitySerializer()
    likes = serializers.IntegerField(read_only=True)
    dislikes = serializers.IntegerField(read_only=True)
    user_reaction = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "text",
            "creator",
            "community",
            "liked",
            "disliked",
            "creation_datetime",
            "likes",
            "dislikes",
            "user_reaction",
        )

    def get_validation_exclusions(self):
        exclusions = super().get_validation_exclusions()
        return exclusions + ["creator"]


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comments"""

    class Meta:
        model = Comment
        fields = ("id", "text", "creator", "post", "creation_time")


class ResourcesDataSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ResourcesData"""

    class Meta:
        model = ResourcesData
        fields = ("id", "resource_url")


class ResourcesRelationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ResourcesRelations"""

    class Meta:
        model = ResourcesRelation
        fields = ("id", "post", "comment", "resource")
