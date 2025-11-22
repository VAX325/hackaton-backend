import uuid
from django.db import models
from datetime import date
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

# -------------- soft delete --------------


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=["is_deleted", "deleted_at"])


# -------------- model Users --------------


class User(SoftDeleteModel):
    username = models.CharField(unique=True, max_length=16)
    visible_name = models.CharField(max_length=32, default="")
    email = models.CharField(max_length=32)
    bio = models.CharField(null=True, max_length=256)
    follower_counter = models.IntegerField(default=0)
    avatar_url = models.URLField(null=True)
    birthday = models.DateField(default="1900-01-01")
    registration_day = models.DateField(default=timezone.now)
    password_hash = models.CharField(max_length=256)

    # def set_password(self, raw_password):
    #     self.password_hash = make_password(raw_password)

    # def password_check(self, raw_password):
    #     return check_password(raw_password, self.password_hash)


class UsersFollow(SoftDeleteModel):
    user_id = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="users_follow_user"
    )
    follower_id = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="users_follow_follower"
    )

    class Meta:
        unique_together = ("user_id", "follower_id")


class Session(SoftDeleteModel):
    user_id = models.ForeignKey(User, on_delete=models.PROTECT)
    token = models.CharField(max_length=16)
    start_time = models.DateTimeField(default=timezone.now)
    finish_time = models.DateTimeField()
    # device_name = models.CharField(max_length=128)


class GlobalAdmin(SoftDeleteModel):
    user_id = models.ForeignKey(User, on_delete=models.PROTECT)


class Community(SoftDeleteModel):
    label = models.CharField(max_length=128)
    description = models.CharField(null=True, max_length=1024)
    avatar_url = models.URLField()
    member_counter = models.IntegerField(default=0)
    creator_id = models.ForeignKey(User, on_delete=models.PROTECT)
    creation_date = models.DateTimeField(default=timezone.now)


class CommunitiesFollow(SoftDeleteModel):
    follower_id = models.ForeignKey(User, on_delete=models.PROTECT)


class Post(SoftDeleteModel):
    text = models.CharField(max_length=2048)
    creator_id = models.ForeignKey(User, on_delete=models.PROTECT)
    community_id = models.ForeignKey(Community, on_delete=models.PROTECT)
    like_counter = models.IntegerField(default=0)
    dislike_counter = models.IntegerField(default=0)


class Comment(SoftDeleteModel):
    text = models.CharField(max_length=512)
    creator_id = models.ForeignKey(User, on_delete=models.PROTECT)
    post_id = models.ForeignKey(Post, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(default=timezone.now)


class ResourcesData(SoftDeleteModel):
    resource_url = models.URLField()


class ResourcesRelation(SoftDeleteModel):
    post_id = models.ForeignKey(Post, on_delete=models.PROTECT)
    comment_id = models.ForeignKey(Comment, on_delete=models.PROTECT)
    resource_id = models.ForeignKey(ResourcesData, on_delete=models.PROTECT)


class Like(SoftDeleteModel):
    liker_id = models.ForeignKey(User, on_delete=models.PROTECT)
    post_id = models.ForeignKey(Post, on_delete=models.PROTECT)


class Dislike(SoftDeleteModel):
    disliker_id = models.ForeignKey(User, on_delete=models.PROTECT)
    post_id = models.ForeignKey(Post, on_delete=models.PROTECT)
