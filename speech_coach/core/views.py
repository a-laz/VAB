from django.shortcuts import render
from rest_framework import generics
from .models import UserSpeech, ExemplarySpeech
from .serializers import UserSpeechSerializer, ExemplarySpeechSerializer

# Create your views here.

class SpeechList(generics.ListCreateAPIView):
    queryset = UserSpeech.objects.all()
    serializer_class = UserSpeechSerializer

class SpeechDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserSpeech.objects.all()
    serializer_class = UserSpeechSerializer

class ExemplarySpeechList(generics.ListAPIView):
    queryset = ExemplarySpeech.objects.all()
    serializer_class = ExemplarySpeechSerializer
