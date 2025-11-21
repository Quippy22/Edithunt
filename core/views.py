from re import sub

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, View
from django.views.generic.edit import FormMixin

from .filters import BountyFilter
from .forms import BountyForm, CustomUserCreationForm, SubmissionForm
from .models import Bounty, Submission


class SignUpView(CreateView):
    """
    Handles user registration.
    Uses a custom form `CustomUserCreationForm` to include the 'role' field.
    Redirects to the login page upon successful registration.
    """

    form_class = CustomUserCreationForm
    # Redirect to login page after successful registration
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class CustomLoginView(LoginView):
    """
    Handles user login.
    Redirects authenticated users away from the login page.
    """

    template_name = "registration/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        """Redirects to the home page upon successful login."""
        return reverse_lazy("home")


def logout_view(request):
    """Logs the user out and redirects to the login page."""
    logout(request)
    return redirect("login")


@method_decorator(login_required, name="dispatch")
class PostBountyView(CreateView):
    """
    Allows logged-in users (creators) to post a new bounty.
    The view automatically assigns the logged-in user as the bounty's creator.
    """

    model = Bounty
    form_class = BountyForm
    template_name = "core/post_bounty.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """
        Sets the creator of the bounty to the currently logged-in user before saving.
        """
        form.instance.creator = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class CreatorDashboardView(ListView):
    """
    Displays a list of bounties created by the currently logged-in user.
    """

    model = Bounty
    template_name = "core/creator_dashboard.html"
    context_object_name = "bounties"

    def get_queryset(self):
        """
        Filters the queryset to only include bounties created by the current user.
        """
        return Bounty.objects.filter(creator=self.request.user)


@method_decorator(login_required, name="dispatch")
class ViewSubmissionsView(View):
    """
    Displays all submissions for a specific bounty owned by the current user.
    Ensures that creators can only view submissions for their own bounties.
    """

    def get(self, request, bounty_id, *args, **kwargs):
        """Handles GET requests to show submissions for a bounty."""
        bounty = get_object_or_404(Bounty, id=bounty_id, creator=request.user)
        submissions = Submission.objects.filter(bounty=bounty)
        context = {
            "bounty": bounty,
            "submissions": submissions,
        }
        return render(request, "core/view_sumbissions.html", context)


@method_decorator(login_required, name="dispatch")
class BountyBoardView(ListView):
    """
    Displays a filterable and sortable list of all active bounties.
    This is the main page for editors to find work.
    """

    model = Bounty
    template_name = "core/bounty_board.html"
    context_object_name = "bounties"

    def get_paginate_by(self, queryset):
        """
        Determines the number of items per page from a URL query parameter.
        Defaults to 10 if the parameter is not provided.
        """
        return self.request.GET.get("paginate_by", 10)

    def get_queryset(self):
        """
        Builds the queryset for the bounty board.
        It applies filtering and sorting based on URL query parameters.
        """
        queryset = super().get_queryset()

        # Apply filters from the BountyFilter class
        self.filter = BountyFilter(
            self.request.GET, queryset=queryset, request=self.request
        )
        filtered_qs = self.filter.qs

        # Apply sorting based on user selection, defaulting to 'deadline_asc'
        sort_by = self.request.GET.get("sort", "deadline_asc")
        if sort_by == "budget_asc":
            return filtered_qs.order_by("budget_min")
        elif sort_by == "budget_desc":
            return filtered_qs.order_by("-budget_min")
        elif sort_by == "created_at_asc":
            return filtered_qs.order_by("created_at")
        elif sort_by == "created_at_desc":
            return filtered_qs.order_by("-created_at")
        elif sort_by == "deadline_desc":
            return filtered_qs.order_by("-deadline")
        elif sort_by == "deadline_asc":
            return filtered_qs.order_by("deadline")

        # Fallback to the default sorting
        return filtered_qs.order_by("deadline")

    def get_context_data(self, **kwargs):
        """
        Adds the filter object and pagination query parameters to the context.
        """
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter

        # Preserve all query parameters for pagination links, except for the 'page' param itself.
        query_params = self.request.GET.copy()
        if "page" in query_params:
            del query_params["page"]
        context["query_params"] = query_params.urlencode()

        return context


@method_decorator(login_required, name="dispatch")
class BountyDetailView(FormMixin, DetailView):
    """
    Displays the details of a single bounty and handles the submission form.
    Inherits from FormMixin to allow form processing within a DetailView.
    """

    model = Bounty
    template_name = "core/bounty_detail.html"
    context_object_name = "bounty"
    form_class = SubmissionForm

    def get_success_url(self):
        """
        Returns the URL to redirect to after a successful form submission.
        Redirects back to the same bounty detail page.
        """
        return reverse_lazy("bounty_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        """Adds the submission form to the context."""
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, processing the submission form.
        """
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        Handles a valid form submission.
        - Assigns the bounty and editor to the submission.
        - Implements the 'instant winner' logic for expired bounties.
        """
        submission = form.save(commit=False)
        submission.bounty = self.object
        submission.editor = self.request.user

        # If the deadline has passed, the first person to submit wins instantly.
        if self.object.deadline < timezone.now():
            submission.is_winner = True
            # Mark the bounty as completed to prevent further submissions or winner changes.
            self.object.status = "completed"
            self.object.save()

        submission.save()
        return super().form_valid(form)
