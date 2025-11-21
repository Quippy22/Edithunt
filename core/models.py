from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Represents a user of the platform.
    Extends Django's built-in AbstractUser to add a `role` field,
    distinguishing between 'creators' who post bounties and 'editors' who
    fulfill them.
    """

    ROLE_CHOICES = (
        ("creator", "Creator"),
        ("editor", "Editor"),
    )
    # The role of the user, determining their permissions and available actions.
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="editor")


class Bounty(models.Model):
    """
    Represents a video editing request posted by a Creator.
    This is the central object that editors will browse and submit work for.
    It contains all the details about the job, including the budget, deadline,
    and links to footage.
    """

    STATUS_CHOICES = (
        ("active", "Active"),
        ("in_review", "In Review"),
        ("completed", "Completed"),
    )
    # The creator who posted this bounty.
    creator = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="bounties"
    )
    # The title of the editing request.
    title = models.CharField(max_length=255)
    # A detailed description of the editing work required.
    description = models.TextField()
    # A URL pointing to the raw footage for editors to download.
    footage_link = models.URLField()
    # The minimum budget for the bounty. Used for filtering and display.
    budget_min = models.DecimalField(max_digits=8, decimal_places=2)
    # The maximum budget, for bounties offered as a range. Can be null.
    budget_max = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    # The date and time by which all submissions are due.
    deadline = models.DateTimeField()
    # The current status of the bounty in its lifecycle.
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    # The timestamp when the bounty was first created.
    created_at = models.DateTimeField(auto_now_add=True)
    # The timestamp of the last update to the bounty.
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of a Bounty object."""
        return self.title


class Submission(models.Model):
    """
    Represents an editor's submission for a specific bounty.
    This links an editor's work to the bounty they are competing for.
    """

    # The bounty this submission is for.
    bounty = models.ForeignKey(
        Bounty, on_delete=models.CASCADE, related_name="submissions"
    )
    # The editor who created this submission.
    editor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="submissions"
    )
    # A URL to the final edited video file.
    file_link = models.URLField()
    # A flag to indicate if this submission was chosen as the winner.
    is_winner = models.BooleanField(default=False)
    # The timestamp when the submission was made.
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation of a Submission object."""
        return f"Submission for '{self.bounty.title}' by {self.editor.username}"
