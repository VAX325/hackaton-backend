from utils import random_token
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework import routers
from rest_framework.generics import CreateAPIView
from django.contrib.auth.hashers import make_password
from .serializers import UsersSerializer, User

router = routers.SimpleRouter()
# Create your views here.
class UserCreateView(CreateAPIView):
    serializer_class = UsersSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):

        request.data["password"] = make_password(request.data["password"])
        return super().post(request, *args, **kwargs)
    
@api_view(["POST"])
def auth_by_hash(request):
    name = request.data["username"]
    passhash = hash(request.data["pass"])

    if not User.objects.filter(name=name, password_hash=passhash).count() > 0:
       return
    
    token = random_token()

    Session.object.create(token=token)
    return HttpResponse(token)

