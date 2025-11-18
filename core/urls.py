from django.urls import path
from django.views.generic.base import TemplateView

from .views import (
    BountyBoardView,
    CreatorDashboardView,
    CustomLoginView,
    PostBountyView,
    SignUpView,
    ViewSubmissionsView,
    logout_view,
)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("bounty/post/", PostBountyView.as_view(), name="post_bounty"),
    path("dashboard/", CreatorDashboardView.as_view(), name="creator_dashboard"),
    path(
        "bounty/<int:bounty_id>/submissions/",
        ViewSubmissionsView.as_view(),
        name="view_submissions",
    ),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("bounty-board/", BountyBoardView.as_view(), name="bounty_board"),
]
