from django.urls import path  # URLを書くためのpathを使う
from .views import signup_view
from .views import login_view

urlpatterns = [
    path("signup/", signup_view, name="signup"),  # http://localhost:8000/signup/
    path("login/", login_view, name="login"),
]
