from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('allblogs/', views.allblogs, name='allblogs'),
    path('blogdetails/<int:id>/', views.blogdetails, name='blogdetails'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('payment/', views.payment, name='payment'),
    path('postblog/', views.postblog, name='postblog'),
    path('editblog/<int:id>/', views.editblog, name='editblog'),
    path('deleteblog/<int:id>/', views.deleteblog, name='deleteblog'),
]