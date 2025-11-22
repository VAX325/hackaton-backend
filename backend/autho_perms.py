from django.contrib.auth.backends import BaseBackend
from .models import CommunityModerator, Community, Comment

class CanAddPosts(BaseBackend):
    message = "У вас нет права добавлять посты в это сообщество."

    def has_permission(self, request, view):
        community_id = view.kwargs.get("community_id")
        if not community_id:
            return False

        return CommunityModerator.objects.filter(
            user=request.user,
            community_id=community_id,
            can_add_posts=True
        ).exists()
    

class CanDeletePosts(BaseBackend):
    message = "У вас нет права удалять посты в этом сообществе."

    def has_permission(self, request, view):
        community_id = view.kwargs.get("community_id")
        if not community_id:
            return False

        return CommunityModerator.objects.filter(
            user=request.user,
            community_id=community_id,
            can_delete_posts=True
        ).exists()


class CanDeleteComments(BaseBackend):
    message = "У вас нет права удалять комментарии в этом сообществе."

    def has_permission(self, request, view):
        community_id = view.kwargs.get("community_id")
        if not community_id:
            return False

        return CommunityModerator.objects.filter(
            user=request.user,
            community_id=community_id,
            can_delete_comments=True
        ).exists()


class CanChangePosts(BaseBackend):
    message = "У вас нет права изменять посты в это сообществе."

    def has_permission(self, request, view):
        community_id = view.kwargs.get("community_id")
        if not community_id:
            return False

        return CommunityModerator.objects.filter(
            user=request.user,
            community_id=community_id,
            can_change_posts=True
        ).exists()