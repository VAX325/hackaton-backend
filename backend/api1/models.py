import uuid
from datetime import date

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone

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


class SoftDeleteUserModel(AbstractBaseUser):
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


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Email field must be set")
        user = self.model(
            username=self.model.normalize_username(username=username), **extra_fields
        )  # Create user instance
        user.set_password(password)  # Hash the password
        user.save(using=self._db)  # Save to database
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(SoftDeleteUserModel):
    username = models.CharField(unique=True, max_length=16)
    visible_name = models.CharField(max_length=32, default="")
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=32)
    bio = models.CharField(null=True, max_length=256)
    follower_counter = models.IntegerField(default=0)
    avatar_url = models.URLField(null=True)
    birthday = models.DateField()
    registration_day = models.DateField(default=timezone.now)
    last_login = models.DateTimeField(null=True)  # TODO: Fix that

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    objects = CustomUserManager()

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
