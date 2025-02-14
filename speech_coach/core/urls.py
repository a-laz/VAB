from django.urls import path
from . import views

urlpatterns = [
    path('api/speeches/', views.SpeechList.as_view(), name='speech-list'),
    path('api/speeches/<int:pk>/', views.SpeechDetail.as_view(), name='speech-detail'),
    path('api/exemplary-speeches/', views.ExemplarySpeechList.as_view(), name='exemplary-speech-list'),
]
