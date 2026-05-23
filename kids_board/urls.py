from django.urls import path  # URLを書くためのpathを使う
from .views import signup_view, login_view, logout_view


urlpatterns = [
    path("signup/", signup_view, name="signup"),  # http://localhost:8000/signup/
    path("login/", login_view, name="login"),  # login/
    path("logout/", logout_view, name="logout"),  # logout/
]
