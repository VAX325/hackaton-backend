from ast import literal_eval
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.utils import timezone
from rest_framework import routers, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from .serializers import *


class RegistrationView(APIView):
    def post(self, request: Request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            userdata = serializer.data

            try:
                User.objects.get(
                    username=User.normalize_username(username=userdata.username)
                )

                return Response(
                    {"message": "User alreaddy exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except User.DoesNotExist:
                pass

            user = User.objects.create_user(
                username=userdata["username"],
                password=userdata["password"],
                visible_name=userdata["username"],
                email=userdata["email"],
                birthday=timezone.now(),
            )

            refresh = RefreshToken.for_user(user)  # Создание Refesh и Access
            refresh.payload.update(
                {
                    "user_id": user.id,
                    "username": user.username,
                }
            )

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),  # Отправка на клиент
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "Invalid registration data"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    def post(self, request: Request):
        data = request.data
        username = data.get("username", None)
        password = data.get("password", None)
        if username is None or password is None:
            return Response(
                {"message": "Login/Password invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(
                username=username,
            )
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid Login or Password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {"message": "Invalid Login or Password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        refresh.payload.update({"user_id": user.id, "username": user.username})
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    def post(self, request: Request):
        refresh_token = request.data.get(
            "refresh_token"
        )  # С клиента нужно отправить refresh token
        if not refresh_token:
            return Response(
                {"error": "Необходим Refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Добавить его в чёрный список
        except Exception as e:
            return Response(
                {"error": "Неверный Refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"success": "Выход успешен"}, status=status.HTTP_200_OK)


class UserInfoView(RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class PostsView(ListCreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class PostView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


@api_view(["POST"])
def post_create_view(request):
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

    return Response({"message": "OK"}, status=status.HTTP_201_CREATED)


"""
@api_view(["POST"])
def post_get_view(request):
    try:
        check_session(request.data.token)
    except:
        return

        try:
            post = Post.objects.get(id=request.data.post_id)
        except:
            return Response(
                {"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST
            )

        resources = []
        for resource_relation_id in ResourcesRelation.objects.filter(post_id=post.id):
            resources.append(
                ResourcesData.objects.get(resource_id=resource_relation_id).resource_url
            )

        comments_id = []
        for comm in Comment.objects.filter(post_id=post.id):
            comments_id.append(comm)

        return Response(
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

        return Response({"message": "OK"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"message": e})


@api_view(["POST"])
def comment_get_view(request):
    try:
        check_session(request.data.token)
    except Exception as e:
        return Response({"message": e})

    try:
        comment = Comment.objects.get(id=request.data.post_id)
    except Comment.DoesNotExist:
        return Response(
            {"message": "Comment doesn't exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    resources = []
    for resource_relation_id in ResourcesRelation.objects.filter(comment_id=comment.id):
        resources.append(
            ResourcesData.objects.filter(resource_id=resource_relation_id).resource_url
        )

    return Response(
        {
            "comment_resources": resources,
            "comment_info": {
                "text": comment.text,
                "creator_id": comment.creator_id,
                "creation_time": comment.creation_time,
            },
        }
    )


@api_view(["POST"])
def users_following_create_view(request):
    try:
        check_session(request.data.token)

        if (
            User.objects.filter(id=request.data.user_id).count() <= 0
            and User.objects.filter(id=request.data.follower_id).count() <= 0
        ):
            return Response(
                {"message": "Users not Exist"}, status=status.HTTP_404_NOT_FOUND
            )

        UsersFollow.objects.create(
            user_id=request.data.user_id, follower_id=request.data.follower_id
        )

        return Response({"message": "CREATED"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"message": e})


@api_view(["POST"])
def get_follower_view(request):
    try:
        check_session(request.data.token)

        r = UsersFollow.objects.filter(user_id=request.data.user_id)

        if r.count() <= 0:
            return Response({"data": []}, status=status.HTTP_200_OK)

        data = []
        for follow in r:
            data.append(
                {
                    "id": follow.id,
                    "user_id": follow.user_id,
                    "follower_id": follow.follower_id,
                }
            )

        return Response({"data": data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(e)
"""
