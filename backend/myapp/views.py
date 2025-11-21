from utils import random_token
from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import routers
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from django.contrib.auth.hashers import make_password
from .serializers import UsersSerializer
from models import User

# Create your views here.
class UserCreateView(CreateAPIView):
    serializer_class = UsersSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):

        request.data["password"] = make_password(request.data["password"])
        return super().post(request, *args, **kwargs)

class UserInfoView(RetrieveAPIView):
    serializer_class = UsersSerializer
    queryset = User.objects.all()    

@api_view(["POST"])
def auth_by_hash(request):
    name = request.data["username"]
    passhash = hash(request.data["pass"])

    if not User.objects.filter(name=name, password_hash=passhash).count() > 0:
       return
    
    token = random_token()

    ses_expire = datetime.now()+timedelta.days(7)

    Session.object.create(token=token, session_finish_time=ses_expire)
    return JsonResponse({"token":token})

@api_view(["POST"])
def update_session(request):
    old_token = request.data["token"]


@api_view(["POST"])
def Check_session(request):
    token = request.data["token"]

    res = Session.object.filter(token=token)

    if res.count <= 0:
        return JsonResponse({"status":403})
    res["s"]