from django.urls import path
from .import views


urlpatterns = [

    path('',views.Home,name='Home' ),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    


]