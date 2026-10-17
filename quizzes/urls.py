from django.urls import path
from . import views

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('subject/<int:pk>/', views.topic_list, name='topic_list'),
    path('topic/<int:pk>/', views.take_quiz, name='take_quiz'),
]