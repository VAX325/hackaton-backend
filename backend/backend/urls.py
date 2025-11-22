from api1 import views
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from backend.settings import DEBUG

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/signup", views.RegistrationView.as_view()),
    path("api/v1/auth/signin", views.LoginView.as_view()),
    path("api/v1/auth/signout", views.LogoutView.as_view()),
    path("api/v1/auth/token_refresh", TokenRefreshView.as_view()),
    path("api/v1/user/<str:username>", views.UserView.as_view()),
    path("api/v1/user/<str:username>/posts", views.UserView.get_user_posts),
    path("api/v1/user_me", views.UserView.get_current_user),
    path("api/v1/user_me/followers", views.UserView.get_current_user_followers),
    path("api/v1/user_me/communities", views.UserView.get_current_user_communities),
    path("api/v1/posts", views.PostsView.as_view()),
    path("api/v1/post/create", views.CreatePostView.as_view()),
    path("api/v1/post/<int:id>", views.PostView.as_view()),
    path("api/v1/post/<int:id>/like", views.PostView.like),
    path("api/v1/post/<int:id>/dislike", views.PostView.dislike),
    path("api/v1/post/<int:id>/comment", views.PostView.comment),
    path("api/v1/post/<int:id>/remove_reaction", views.PostView.remove_reaction),
    path("api/v1/community/<str:community_name>", views.CommunityView.as_view()),
    path("api/v1/assets/<str:username>/<str:filename>", views.get_random_asset),
]

if DEBUG:
    urlpatterns.append(path("api/v1/users", views.UsersView.as_view()))
