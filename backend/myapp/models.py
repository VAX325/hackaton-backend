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
            self.save(update_fields=['is_deleted', 'deleted_at'])



# -------------- model Users --------------

class Users(SoftDeleteModel):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(unique=True, max_length=16)
    visible_name = models.CharField(max_length=32)
    email = models.CharField(max_length=32)
    bio = models.CharField(null=True, max_length=256)
    follower_counter = models.IntegerField(default=0)
    avatar_url = models.URLField()
    birthday = models.DateField(default='1900-01-01')
    registration_day = models.DateField(default=date.today())
    password_hash = models.CharField(max_length=256)

    # def set_password(self, raw_password):
    #     self.password_hash = make_password(raw_password)

    # def password_check(self, raw_password):
    #     return check_password(raw_password, self.password_hash)




class UsersFollows(SoftDeleteModel):
    follow_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(Users, on_delete=models.PROTECT)
    follower_id = models.ForeignKey(Users, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('user_id', 'follower_id')


class Sessions(SoftDeleteModel):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(Users, on_delete=models.PROTECT)
    token = models.CharField(length=16)
    start_time = models.DateTimeField(default=timezone.now())
    finish_time = models.DateTimeField()
    #device_name = models.CharField(max_length=128)


class GlobalAdmins(SoftDeleteModel):
    admin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)


class Communities(SoftDeleteModel):
    community_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=128)
    description = models.CharField(null=True, max_length=1024)
    avatar_url = models.URLField()
    member_counter = models.IntegerField(default=0)
    creator_id = models.ForeignKey(Users, on_delete=models.PROTECT)
    creation_date = models.DateTimeField(default=date.today())



class CommunitiesFollows(SoftDeleteModel):
    follow_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community_id = models.ForeignKey(Communities, on_delete=models.models.PROTECT)
    follower_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)



class Posts(SoftDeleteModel):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=2048)
    creator_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)
    community_id = models.ForeignKey(Communities, on_delete=models.models.PROTECT)
    like_counter = models.IntegerField(default=0)
    dislike_counter = models.IntegerField(default=0)
    


class Comments(SoftDeleteModel):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=512)
    creator_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)
    post_id = models.ForeignKey(Posts, on_delete=models.models.PROTECT)
    creatoin_time = models.DateTimeField(default=timezone.now())



class ResourcesData(SoftDeleteModel):
    resource_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource_url = models.URLField()


class RecourcesRelations(SoftDeleteModel):
    relation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.ForeignKey(Posts, on_delete=models.models.PROTECT)
    comment_id = models.ForeignKey(Comments, on_delete=models.models.PROTECT)
    resource_id = models.ForeignKey(ResourcesData, on_delete=models.models.PROTECT)



class Likes(SoftDeleteModel):
    like_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    liker_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)
    post_id = models.ForeignKey(Posts, on_delete=models.models.PROTECT)


class Dislikes(SoftDeleteModel):
    dislike_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disliker_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)
    post_id = models.ForeignKey(Posts, on_delete=models.models.PROTECT)
