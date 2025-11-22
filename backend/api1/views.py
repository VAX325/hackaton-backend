import os
import random
from ast import literal_eval
from datetime import timedelta

import rest_framework.decorators as rdec
from django.conf import settings
from django.db import models, transaction
from django.db.models import Case, CharField, Count, Exists, OuterRef, Value, When
from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from .serializers import *


class RegistrationView(APIView):
    authentication_classes = []

    def post(self, request: Request):
        if request.user and request.user.is_authenticated:
            return Response(
                {"message": "Can't register while been authorized"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            userdata = serializer.data

            try:
                User.objects.get(
                    username=User.normalize_username(username=userdata["username"])
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


class UsersView(ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "username"


class UserView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "username"

    @staticmethod
    @api_view(["GET"])
    @rdec.permission_classes([IsAuthenticated])
    @rdec.authentication_classes([JWTAuthentication])
    def get_user_posts(request: Request, **kwargs):
        username = kwargs["username"]

        queryset = Post.objects.annotate(
            likes=Count("liked"), dislikes=Count("disliked")
        )

        user = request.user

        queryset = queryset.annotate(
            # 1. Проверяем, есть ли ID юзера в таблице Post_liked
            is_liked_by_user=Exists(
                Post.liked.through.objects.filter(
                    post_id=OuterRef("pk"), user_id=user.id
                )
            ),
            # 2. Проверяем, есть ли ID юзера в таблице Post_disliked
            is_disliked_by_user=Exists(
                Post.disliked.through.objects.filter(
                    post_id=OuterRef("pk"), user_id=user.id
                )
            ),
        ).annotate(
            # 3. Формируем итоговое поле user_reaction
            user_reaction=Case(
                When(is_liked_by_user=True, then=Value("like")),
                When(is_disliked_by_user=True, then=Value("dislike")),
                default=None,  # Если ни там, ни там
                output_field=CharField(),
            )
        )

        return Response(
            PostSerializer(queryset.filter(creator__username=username), many=True).data,
            status=status.HTTP_200_OK,
        )

    @staticmethod
    @api_view(["GET"])
    @rdec.permission_classes([IsAuthenticated])
    @rdec.authentication_classes([JWTAuthentication])
    def get_current_user(request: Request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )

    @staticmethod
    @api_view(["GET"])
    @rdec.permission_classes([IsAuthenticated])
    @rdec.authentication_classes([JWTAuthentication])
    def get_current_user_followers(request: Request):
        followers = request.user.followers_users_set.all()

        return Response(
            UserSerializer(followers, many=True).data,
            status=status.HTTP_200_OK,
        )

    @staticmethod
    @api_view(["GET"])
    @rdec.permission_classes([IsAuthenticated])
    @rdec.authentication_classes([JWTAuthentication])
    def get_current_user_communities(request: Request):
        # subscribed = request.user.subscribed_users_set.all()

        return Response(
            [],  # CommunitySerializer(subscribed).data,
            status=status.HTTP_200_OK,
        )


class PostsView(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Post.objects.annotate(
            likes=Count("liked"), dislikes=Count("disliked")
        )

        user = self.request.user

        # Если пользователь не авторизован, реакции быть не может
        if not user.is_authenticated:
            return queryset.annotate(
                user_reaction=Value(None, output_field=CharField())
            )

        return queryset.annotate(
            # 1. Проверяем, есть ли ID юзера в таблице Post_liked
            is_liked_by_user=Exists(
                Post.liked.through.objects.filter(
                    post_id=OuterRef("pk"), user_id=user.id
                )
            ),
            # 2. Проверяем, есть ли ID юзера в таблице Post_disliked
            is_disliked_by_user=Exists(
                Post.disliked.through.objects.filter(
                    post_id=OuterRef("pk"), user_id=user.id
                )
            ),
        ).annotate(
            # 3. Формируем итоговое поле user_reaction
            user_reaction=Case(
                When(is_liked_by_user=True, then=Value("like")),
                When(is_disliked_by_user=True, then=Value("dislike")),
                default=None,  # Если ни там, ни там
                output_field=CharField(),
            )
        )


class CreatePostView(CreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        data = request.data

        post = Post.objects.create(
            text=data["text"],
            creator=request.user,
            community=data.get("community", None),
        )
        post.save()
        post.likes = 0
        post.dislikes = 0
        post.user_reaction = None

        return Response(
            self.serializer_class(post).data, status=status.HTTP_201_CREATED
        )


class PostView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get(self, request: Request, **kwargs):
        user = request.user

        # Строим QuerySet (он еще не выполняется в БД)
        qs = Post.objects.annotate(likes=Count("liked"), dislikes=Count("disliked"))

        if user.is_authenticated:
            qs = qs.annotate(
                is_liked_by_user=Exists(
                    Post.liked.through.objects.filter(
                        post_id=OuterRef("pk"), user_id=user.id
                    )
                ),
                is_disliked_by_user=Exists(
                    Post.disliked.through.objects.filter(
                        post_id=OuterRef("pk"), user_id=user.id
                    )
                ),
            ).annotate(
                user_reaction=Case(
                    When(is_liked_by_user=True, then=Value("like")),
                    When(is_disliked_by_user=True, then=Value("dislike")),
                    default=None,
                    output_field=CharField(),
                )
            )
        else:
            qs = qs.annotate(user_reaction=Value(None, output_field=CharField()))

        try:
            # Выполняем запрос к БД
            post = qs.get(id=kwargs["id"])
        except Post.DoesNotExist:
            return Response(
                {"message": "Post doesn't exists"}, status=status.HTTP_404_NOT_FOUND
            )

        # Сериализатор сам подхватит поле user_reaction из аннотации
        return_data = PostSerializer(post).data

        return Response(return_data, status=status.HTTP_200_OK)

    @staticmethod
    @api_view(["POST"])
    @rdec.permission_classes([IsAuthenticated])
    @rdec.authentication_classes([JWTAuthentication])
    @transaction.atomic
    def like(request: Request, **kwargs):
        id = kwargs.get("id", None)
        if id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response(
                {"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        current_user: User = request.user
        try:
            current_user.likes.get(id=id)
            return Response(
                {"message": "Already liked"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Post.DoesNotExist:
            pass

        try:
            disliked_post = current_user.dislikes.get(id=id)
            current_user.dislikes.remove(disliked_post)
            post.disliked.remove(current_user)
        except Post.DoesNotExist:
            pass

        post.liked.add(current_user)
        current_user.likes.add(post)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    @api_view(["POST"])
    @rdec.permission_classes([IsAuthenticated])
    @rdec.authentication_classes([JWTAuthentication])
    @transaction.atomic
    def dislike(request: Request, **kwargs):
        id = kwargs.get("id", None)
        if id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response(
                {"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        current_user: User = request.user
        try:
            current_user.dislikes.get(id=id)
            return Response(
                {"message": "Already disliked"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Post.DoesNotExist:
            pass

        try:
            liked_post = current_user.likes.get(id=id)
            current_user.likes.remove(liked_post)
            post.liked.remove(current_user)
        except Post.DoesNotExist:
            pass

        post.disliked.add(current_user)
        current_user.dislikes.add(post)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    @api_view(["POST"])
    @rdec.permission_classes([IsAuthenticated])
    @rdec.authentication_classes([JWTAuthentication])
    @transaction.atomic
    def comment(request: Request, **kwargs):
        id = kwargs.get("id", None)
        if id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response(
                {"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        current_user: User = request.user

        comment = Comment.objects.create(
            text=request.data["content"],
            creator=current_user,
            post=post,
            creation_time=timezone.now(),
        )

        current_user.comments.add(comment)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    @api_view(["POST"])
    @rdec.permission_classes([IsAuthenticated])
    @rdec.authentication_classes([JWTAuthentication])
    @transaction.atomic
    def remove_reaction(request: Request, **kwargs):
        id = kwargs.get("id", None)
        if id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response(
                {"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        current_user: User = request.user

        try:
            disliked_post = current_user.dislikes.get(id=id)
            current_user.likes.remove(disliked_post)
            post.disliked.remove(current_user)
        except Post.DoesNotExist:
            pass

        try:
            liked_post = current_user.likes.get(id=id)
            current_user.likes.remove(liked_post)
            post.liked.remove(current_user)
        except Post.DoesNotExist:
            pass

        return Response(status=status.HTTP_200_OK)


class CommunityView(RetrieveUpdateAPIView):
    serializer_class = CommunitySerializer
    queryset = Community.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


@api_view(["GET"])
@rdec.permission_classes([AllowAny])
def get_random_asset(request: Request, username: str, filename: str):
    """
    Возвращает случайный JPG файл из папки 'assets' в корне проекта,
    игнорируя переданные username и filename.
    """
    # Путь к папке assets в корне проекта
    assets_dir = os.path.join(settings.BASE_DIR, "assets")

    if not os.path.exists(assets_dir):
        return Response(
            {"error": "Assets directory not found on server"},
            status=status.HTTP_404_NOT_FOUND,
        )

    images = [f for f in os.listdir(assets_dir) if f.lower().endswith((".png"))]

    if not images:
        return Response(
            {"error": "No images found in assets"}, status=status.HTTP_404_NOT_FOUND
        )

    # Выбираем случайный файл
    random_image = random.choice(images)
    image_path = os.path.join(assets_dir, random_image)

    # FileResponse эффективно отдает файлы (stream)
    return FileResponse(open(image_path, "rb"), content_type="image/png")
