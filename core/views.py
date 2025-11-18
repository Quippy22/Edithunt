from re import sub

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, View

from .filters import BountyFilter
from .forms import BountyForm, CustomUserCreationForm
from .models import Bounty, Submission


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


@method_decorator(login_required, name="dispatch")
class ViewSubmissionsView(View):
    def get(self, request, bounty_id, *args, **kwargs):
        bounty = get_object_or_404(Bounty, id=bounty_id, creator=request.user)
        submissions = Submission.objects.filter(bounty=bounty)
        context = {
            "bounty": bounty,
            "submissions": submissions,
        }
        return render(request, "core/view_sumbissions.html", context)


@method_decorator(login_required, name="dispatch")
class BountyBoardView(ListView):
    model = Bounty
    template_name = "core/bounty_board.html"
    context_object_name = "bounties"

    def get_paginate_by(self, queryset):
        # Get the 'paginate_by' value from the request's GET parameters, default to 10
        return self.request.GET.get('paginate_by', 10)

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at') # Start with a default order
        
        # Apply filters from django-filter
        self.filter = BountyFilter(self.request.GET, queryset=queryset)
        
        # Apply sorting based on user selection
        sort_by = self.request.GET.get('sort')
        if sort_by == 'budget_asc':
            return self.filter.qs.order_by('budget_min')
        elif sort_by == 'budget_desc':
            return self.filter.qs.order_by('-budget_min')
        elif sort_by == 'deadline_asc':
            return self.filter.qs.order_by('deadline')
        elif sort_by == 'deadline_desc':
            return self.filter.qs.order_by('-deadline')
        
        # Return the filtered queryset
        return self.filter.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add the filter to the context
        context['filter'] = self.filter
        
        # Preserve query parameters for pagination links
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = query_params.urlencode()
        
        return context
