from rest_framework import status
from .utils import random_token
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework import routers
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from django.contrib.auth.hashers import make_password
from .serializers import *
from .models import *
from ast import literal_eval


class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):

        if User.objects.filter(username=request.data["username"]).count() > 0:
            return JsonResponse(
                {"message": "non-correct username"}, status=status.HTTP_400_BAD_REQUEST
            )

        request.data["password"] = make_password(request.data["password"])
        return super().post(request, *args, **kwargs)


class UserInfoView(RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            check_session(request.data.token)
        except:

            if (
                Session.object.filter(
                    token=request.data.token, user_id=request.data.user_id
                ).count
                <= 0
            ):
                return JsonResponse({}, status=status.HTTP_401_UNAUTHORIZED)
        return super().get(request, *args, **kwargs)


@api_view(["POST"])
def post_create_view(request):
    try:
        check_session(request.data.token)
    
        post = Post.objects.create(
            text=request.data.text,
            creator_id=request.data.creator_id,
            community_creator=request.data.community_creator,
        )

        resources_arr = literal_eval(request["resources"])
        #! add upload by cdn
        # urls_resources = upload_cdn(resources_arr)
        for resource in resources_arr:
            ResourcesData.objects.create(resource_url=resource)
            ResourcesRelation.objects.create(
                resource_id=ResourcesData.objects.filter(resource_url=resource).id,
                comment_id=-1,
                post_id=post.id,
            )

        return JsonResponse({"message": "OK"}, status=status.HTTP_201_CREATED)


    except Exception as e:
        return JsonResponse({"message":e})

@api_view(["POST"])
def post_get_view(request):
    try:
        check_session(request.data.token)
    except:
        post = Post.objects.filter(id=request.data.post_id)

        if post.count() <= 0:
            return JsonResponse(
                {"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST
            )

        resources = []
        for resource_relation_id in ResourcesRelation.objects.filter(post_id=post.id):
            resources.append(
                ResourcesData.objects.filter(
                    resource_id=resource_relation_id
                ).resource_url
            )

        comments_id = []
        for comm in Comment.objects.filter(post_id=post.id):
            comments_id.append(comm)

        return JsonResponse(
            {
                "post_resources": resources,
                "post_comments": comments_id,
                "post_info": {
                    "text": post.text,
                    "creator_id": post.creator_id,
                    "community_id": post.community_id,
                    "like_counter": post.like_counter,
                    "deslike_counter": post.deslike_counter,
                },
            }
        )


@api_view(["POST"])
def comment_create_view(request):
    try:
        check_session(request.data.token)
        comment = Comment.objects.create(
            text=request.data.text,
            creator_id=request.data.creator_id,
            post_id=request.data.post_id,
            creation_time=timezone.now(),
        )

        resources_arr = literal_eval(request["resources"])
        #! add upload by cdn
        # urls_resources = upload_cdn(resources_arr)
        for resource in resources_arr:
            ResourcesData.objects.create(resource_url=resource)
            ResourcesRelation.objects.create(
                resource_id=ResourcesData.objects.filter(resource_url=resource).id,
                comment_id=comment.id,
                post_id=-1,
            )

        return JsonResponse({"message": "OK"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse({"message":e})

@api_view(["POST"])
def comment_get_view(request):
    try:
        check_session(request.data.token)
    except:
        comment = Comment.objects.filter(id=request.data.post_id)

        if comment.count() <= 0:
            return JsonResponse(
                {"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST
            )

        resources = []
        for resource_relation_id in ResourcesRelation.objects.filter(
            comment_id=comment.id
        ):
            resources.append(
                ResourcesData.objects.filter(
                    resource_id=resource_relation_id
                ).resource_url
            )

        return JsonResponse(
            {
                "comment_resources": resources,
                "comment_info": {
                    "text": comment.text,
                    "creator_id": comment.creator_id,
                    "creation_time": comment.creation_time,
                },
            }
        )


    except Exception as e:
        return JsonResponse({"message":e})


@api_view(["POST"])
def auth_by_hash(request):

    name = request.data["username"]
    passhash = hash(request.data["password"])

    if not User.objects.filter(username=name, password_hash=passhash).count() > 0:
        return JsonResponse(
            {"message": "User is not exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    token = random_token()

    ses_expire = timezone.now() + timedelta.days(7)

    Session.object.create(
        token=token,
        session_finish_time=ses_expire,
        user_id=User.objects.filter(username=name, password_hash=passhash).id,
    )
    return JsonResponse({"token": token}, status=status.HTTP_200_OK)


@api_view(["POST"])
def users_following_create_view(request):
    try:
        check_session(request.data.token)

        if User.objects.filter(id=request.data.user_id).count() <= 0 and User.objects.filter(id=request.data.follower_id).count() <= 0:    
            return JsonResponse({"message":"Users not Exist"}, status=status.HTTP_404_NOT_FOUND)

        UsersFollow.objects.create(user_id=request.data.user_id, follower_id=request.data.follower_id)

        return JsonResponse({"message":"CREATED"}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return JsonResponse({"message":e})


@api_view(["POST"])
def get_follower_view(request):
    try:
        check_session(request.data.token)
        
        r = UsersFollow.objects.filter(user_id=request.data.user_id)

        if r.count() <= 0 :
            return JsonResponse({"data":[]}, status=status.HTTP_200_OK)

        data = []
        for follow in r:
            data.append(
                {
                    "id":follow.id,
                    "user_id":follow.user_id,
                    "follower_id":follow.follower_id
                })

        return JsonResponse({"data":data},status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse(e)

@api_view(["GET"])
def get_all_users(request):
    """
    !ONLY FOR TEST
    """
    try:
        check_session(request.token)
        # Check user by he is admin


        return HttpResponse(User.objects.all())
    
    except Exception as e:
        return JsonResponse({"message":e})


def update_session(token):
    r = Session.object.filter(token=token)

    new_token = random_token()

    r["token"] = new_token
    r["finish_time"] = timezone.now()
    r.save()
    return


def check_session(token):
    res = Session.object.filter(token=token)

    if res.count <= 0:
        raise JsonResponse(
            {"message": "Session is not exist"}, status.HTTP_400_BAD_REQUEST
        )
    if res["finish_time"] < timezone.now():
        raise JsonResponse(
            {"message": "Session expire"}, status=status.HTTP_401_UNAUTHORIZED
        )
    update_session(token=token)
