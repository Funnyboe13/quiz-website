from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('subject/<int:pk>/', views.topic_list, name='topic_list'),
    path('topic/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('my-results/', views.my_results, name='my_results'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]