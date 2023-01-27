from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import path
from .views import UserView, profile_delete_view, userDelete, get_user_write_post

# Create your views here.
app_name="Account"
urlpatterns = [
    # path('account/view',UserView.as_view(), name = "account_view" ),
    path('account/view',get_user_write_post, name = "account_view" ),
    path('delete_success/', userDelete, name="delete_success"),
]