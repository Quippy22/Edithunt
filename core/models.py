from django.contrib.auth.models import AbstractUser
from django.db import models


# This is our custom user profile.
# It extends Django's default user, allowing us to add specific roles.
class CustomUser(AbstractUser):
    # Choices for the user's role (either a Creator or an Editor)
    ROLE_CHOICES = (
        ("creator", "Creator"),
        ("editor", "Editor"),
    )
    # The role of the user in the Edithunt platform
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='editor')


# This model represents a video editing request posted by a Creator.
class Bounty(models.Model):
    # Possible states for a bounty (e.g., active, under review, completed)
    STATUS_CHOICES = (
        ("active", "Active"),
        ("in_review", "In Review"),
        ("completed", "Completed"),
    )
    # Link to the user who created this bounty
    creator = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="bounties"
    )
    # Title of the editing request
    title = models.CharField(max_length=255)
    # Detailed description of what needs to be edited
    description = models.TextField()
    # Link to the raw footage for editors to download
    footage_link = models.URLField()
    # The amount of money offered for the winning edit
    budget_min = models.DecimalField(max_digits=8, decimal_places=2)
    budget_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # The date and time by which submissions are due
    deadline = models.DateTimeField()
    # Current status of the bounty
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    # When the bounty was first posted
    created_at = models.DateTimeField(auto_now_add=True)
    # When the bounty was last updated
    updated_at = models.DateTimeField(auto_now=True)

    # How a Bounty object is represented as a string (e.g., in admin panel)
    def __str__(self):
        return self.title


# This model represents an editor's submission for a specific bounty.
class Submission(models.Model):
    # Link to the bounty this submission is for
    bounty = models.ForeignKey(
        Bounty, on_delete=models.CASCADE, related_name="submissions"
    )
    # Link to the user (editor) who made this submission
    editor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="submissions"
    )
    # URL where the edited video file can be accessed
    file_link = models.URLField()
    # Flag to mark if this submission was chosen as the winner
    is_winner = models.BooleanField(default=False)
    # When the submission was made
    submitted_at = models.DateTimeField(auto_now_add=True)

    # How a Submission object is represented as a string
    def __str__(self):
        return f"Submission for '{self.bounty.title}' by {self.editor.username}"

