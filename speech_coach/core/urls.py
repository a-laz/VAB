from django.urls import path
from . import views

urlpatterns = [
    path('api/speeches/', views.UserSpeechList.as_view(), name='speech-list'),
    path('api/speeches/<int:pk>/', views.UserSpeechDetail.as_view(), name='speech-detail'),
    path('api/speeches/<int:speech_id>/analysis/', views.speech_analysis, name='speech-analysis'),
    path('api/speeches/<int:speech_id>/status/', views.speech_status, name='speech-status'),
    path('api/speeches/<int:speech_id>/retry/', views.retry_processing, name='retry-processing'),
    path('api/exemplary-speeches/', views.ExemplarySpeechList.as_view(), name='exemplary-speech-list'),
    path('api/user/statistics/', views.user_statistics, name='user-statistics'),
]
