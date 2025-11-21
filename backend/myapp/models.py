from django.db import models
from datetime import date
from django.contrib.auth.hashers import make_password, check_password


class Users(models.Model):
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




class Users_follows(models.Model):
    follow_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(Users, on_delete=models.PROTECT)
    follower_id = models.ForeignKey(Users, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('user_id', 'follower_id')


class Sessions(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(Users, on_delete=models.PROTECT)
    token = models.CharField(length=16)
    start_time = models.DateTimeField(default=date.today())
    #device_name = models.CharField(max_length=128)


class global_admins(models.Model):
    admin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)


class Communities(models.Model):
    community_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=128)
    description = models.CharField(null=True, max_length=1024)
    avatar_url = models.URLField()
    member_counter = models.IntegerField(default=0)
    creator_id = models.ForeignKey(Users, on_delete=models.PROTECT)
    creation_date = models.DateTimeField(default=date.today())



class Communities_follows(models.Model):
    follow_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community_id = models.ForeignKey(Communities, on_delete=models.models.PROTECT)
    follower_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)



class Posts(models.Model):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=2048)
    creator_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)
    community_id = models.ForeignKey(Communities, on_delete=models.models.PROTECT)
    like_counter = models.IntegerField(default=0)
    dislike_counter = models.IntegerField(default=0)
    


class Comments(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=512)
    creator_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)
    post_id = models.ForeignKey(Posts, on_delete=models.models.PROTECT)
    creatoin_time = models.DateTimeField(default=date.today())



class Resources_data(models.Model):
    resource_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource_url = models.URLField()


class Recources_relations(models.Model):
    relation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.ForeignKey(Posts, on_delete=models.models.PROTECT)
    comment_id = models.ForeignKey(Comments, on_delete=models.models.PROTECT)
    resource_id = models.ForeignKey(Resources_data, on_delete=models.models.PROTECT)



class Likes(models.Model):
    like_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    liker_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)
    post_id = models.ForeignKey(Posts, on_delete=models.models.PROTECT)


class Dislikes(models.Model):
    dislike_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disliker_id = models.ForeignKey(Users, on_delete=models.models.PROTECT)
    post_id = models.ForeignKey(Posts, on_delete=models.models.PROTECT)