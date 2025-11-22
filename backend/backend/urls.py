from django.contrib import admin
from django.urls import path
from api1 import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/signin", views.auth_by_hash),
    path("api/v1/auth/signup", views.UserCreateView.as_view()),
    path("api/v1/users/getinfo/<int:pk>", views.UserInfoView.as_view()),
    path("users/", views.get_all_users),
]
