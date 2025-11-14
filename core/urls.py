from django.urls import path
from django.views.generic.base import TemplateView
from .views import SignUpView, CustomLoginView, logout_view

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]
