from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView

from .forms import BountyForm, CustomUserCreationForm
from .models import Bounty

# Registration view
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy(
        "login"
    )  # Redirect to login page after succesfull registration
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
    return redirect("login")  # Redirect to login page


# Post bounty view
@method_decorator(login_required, name="dispatch")
class PostBountyView(CreateView):
    model = Bounty
    form_class = BountyForm
    template_name = "core/post_bounty.html"
    # Redirect to home page after a successful post
    # todo: maybe think this over
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

# Creator dahsboard view
@method_decorator(login_required, name="dispatch")
class CreatorDashboardView(ListView):
    model = Bounty
    template_name = "core/creator_dashboard.html"
    context_object_name = "bounties"

    def get_queryset(self):
        return Bounty.objects.filter(creator=self.request.user)
