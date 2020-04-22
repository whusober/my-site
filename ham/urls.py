from django.urls import path

from . import views

app_name = 'ham'
urlpatterns = [
    path('', views.ham, name='ham'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('welcome/', views.ham, name='ham'),
    path('check/', views.check, name='check'),
    path('update/', views.update, name='update'),
]