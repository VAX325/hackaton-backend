from rest_framework import status
from utils import random_token
from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import routers
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from django.contrib.auth.hashers import make_password
from .serializers import *
from models import *

# Create your views here.
class UserCreateView(CreateAPIView):
    serializer_class = UsersSerializer
    queryset = Users.objects.all()

    def post(self, request, *args, **kwargs):
        
        request.data["password"] = make_password(request.data["password"])
        return super().post(request, *args, **kwargs)

class UserInfoView(RetrieveAPIView):
    serializer_class = UsersSerializer
    queryset = Users.objects.all()    
    def get(self, request, *args, **kwargs):
        try:
            check_session(request.data.token)
        except:

            if Sessions.object.filter(token=request.data.token, user_id=request.data.user_id).count <= 0:
                return JsonResponse({}, status=status.HTTP_401_UNAUTHORIZED)

        

        return super().get(request, *args, **kwargs)

@api_view(["POST"])
def auth_by_hash(request):
    try:
        check_session(request.data.token)
    except:
        name = request.data["username"]
        passhash = hash(request.data["pass"])

        if not Users.objects.filter(name=name, password_hash=passhash).count() > 0:
           return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        token = random_token()

        ses_expire = datetime.now()+timedelta.days(7)

        Sessions.object.create(token=token, session_finish_time=ses_expire)
        return JsonResponse({"token":token},status=status.HTTP_200_OK)


def update_session(token):
    r = Sessions.object.filter(token=token)

    new_token = random_token()

    r["token"] = new_token
    r.save()
    return



def check_session(token):
    res = Sessions.object.filter(token=token)

    if res.count <= 0:
        raise JsonResponse({"message":"Session is not exist"}, status.HTTP_400_BAD_REQUEST)
    if res["finish_time"] < datetime.now():
        raise JsonResponse({"message": "Session expire"},status=status.HTTP_401_UNAUTHORIZED)
    update_session(token=token)
    

