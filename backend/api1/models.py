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
        user = self.model(
            username=self.model.normalize_username(username=username), **extra_fields
        )  # Create user instance
        user.set_password(password)  # Hash the password
        user.save(using=self._db)  # Save to database
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class User(SoftDeleteUserModel):
    username = models.CharField(unique=True, max_length=16)
    visible_name = models.CharField(max_length=32, default="")
    password = models.CharField(max_length=128)
    bio = models.CharField(null=True, max_length=256)
    follower_counter = models.IntegerField(default=0)
    avatar_url = models.URLField(null=True)
    birthday = models.DateField()
    registration_day = models.DateField(default=timezone.now)
    last_login = models.DateTimeField(null=True)  # TODO: Fix that
    likes = models.ManyToManyField(to="Post", blank=True, related_name="likes_user_set")
    dislikes = models.ManyToManyField(
        to="Post", blank=True, related_name="dislikes_user_set"
    )
    comments = models.ManyToManyField(
        to="Comment", blank=True, related_name="comments_user_set"
    )
    followers = models.ManyToManyField(
        to="User", blank=True, related_name="followers_users_set"
    )
    subscribed = models.ManyToManyField(
        to="Community", blank=True, related_name="subscribed_users_set"
    )

    USERNAME_FIELD = "username"
    objects = CustomUserManager()


class GlobalAdmin(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT)


class Community(SoftDeleteModel):
    label = models.CharField(max_length=128)
    description = models.CharField(null=True, max_length=1024)
    avatar_url = models.URLField()
    members = models.ManyToManyField(
        to=User, blank=True, related_name="community_users_set"
    )
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    creation_date = models.DateTimeField(default=timezone.now)


class Post(SoftDeleteModel):
    text = models.CharField(max_length=2048)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    community = models.ForeignKey(Community, null=True, on_delete=models.PROTECT)
    liked = models.ManyToManyField(
        to=User, blank=True, related_name="post_user_liked_set"
    )
    disliked = models.ManyToManyField(
        to=User, blank=True, related_name="post_user_disliked_set"
    )
    creation_datetime = models.DateTimeField(default=timezone.now)


class Comment(SoftDeleteModel):
    text = models.CharField(max_length=512)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(default=timezone.now)


class ResourcesData(SoftDeleteModel):
    resource_url = models.URLField()


class ResourcesRelation(SoftDeleteModel):
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    comment = models.ForeignKey(Comment, on_delete=models.PROTECT)
    resource = models.ForeignKey(ResourcesData, on_delete=models.PROTECT)
