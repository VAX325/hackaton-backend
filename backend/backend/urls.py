from api1 import views
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/signup", views.RegistrationView.as_view()),
    path("api/v1/auth/signin", views.LoginView.as_view()),
    path("api/v1/auth/signout", views.LogoutView.as_view()),
    path("api/v1/auth/token_refresh/", TokenRefreshView.as_view()),
    path("api/v1/users/getinfo/<int:pk>", views.UserInfoView.as_view()),
]
