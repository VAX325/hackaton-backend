from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view

# Create your views here.
class Auth:
    @api_view(['POST'])
    def r(request):
        return(HttpResponse(1))