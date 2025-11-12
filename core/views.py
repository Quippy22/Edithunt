from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm


# Registration view
class SignUpView(CreateView):
    fom_class = CustomUserCreationForm
    success_url = reverse_lazy("login")  # Redirect to login page after succesfull registration
    template_name = "registration/signup.html"


# Login view
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    fields = "__all__"
    redirect_authenticated_user = True  # Redirect logged-in users

    def get_success_url(self):
        return reverse_lazy("home")  # Redirect to home page


# Logout view
def logout_view(request):
    logout(request)
    return redirect('login') # Redirect to login page
