from datetime import timedelta

import django_filters
from django import forms
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Bounty, Tag


class BountyFilter(django_filters.FilterSet):
    """
    A custom filter set for the Bounty model to enable complex filtering on the bounty board.
    Uses 'django-filter' to automatically generate form fields for querying the queryset.
    """
    
    # Text Search Filter
    search = django_filters.CharFilter(
        method="filter_by_search",
        label=_("Search"),
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": _("Search bounties...")}),
    )

    # Tag Filter
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        label=_("Tags"),
        widget=forms.SelectMultiple(attrs={"class": "form-input h-32"}), # Simple multi-select box
    )

    # Budget Filtering Logic
    budget_min = django_filters.NumberFilter(
        label=_("Min Budget"),
        method=lambda qs, n, v: qs,
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
    )
    budget_max = django_filters.NumberFilter(
        label=_("Max Budget"),
        method=lambda qs, n, v: qs,
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
    )

    # Posted Within Logic
    posted_within = django_filters.NumberFilter(
        method="filter_by_posted_within",
        label=_("Posted within"),
        widget=forms.NumberInput(
            attrs={"class": "form-input", "placeholder": "e.g., 3"}
        ),
    )
    
    # Unit Selector for 'Posted Within'
    posted_within_unit = django_filters.ChoiceFilter(
        choices=[("days", _("Days")), ("hours", _("Hours"))],
        method=lambda qs, n, v: qs,
        label=_("Time unit"),
        empty_label=None,
        initial="days",
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    class Meta:
        model = Bounty
        fields = ["search", "tags", "budget_min", "budget_max", "posted_within", "posted_within_unit"]

    def filter_by_search(self, queryset, name, value):
        """
        Filters the queryset by title, description, or tag name.
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) | 
            Q(description__icontains=value) |
            Q(tags__name__icontains=value)
        ).distinct()

    def filter_queryset(self, queryset):
        """
        Overrides the main filter loop to inject custom budget overlap logic.
        """
        queryset = super().filter_queryset(queryset)

        # Annotate 'high_price' to handle fixed-price bounties
        queryset = queryset.annotate(high_price=Coalesce("budget_max", "budget_min"))

        budget_min = self.form.cleaned_data.get("budget_min")
        budget_max = self.form.cleaned_data.get("budget_max")

        if budget_min is not None and budget_max is not None:
            queryset = queryset.filter(
                budget_min__lte=budget_max, high_price__gte=budget_min
            )
        elif budget_min is not None:
            queryset = queryset.filter(high_price__gte=budget_min)
        elif budget_max is not None:
            queryset = queryset.filter(budget_min__lte=budget_max)

        return queryset

    def filter_by_posted_within(self, queryset, name, value):
        """
        Custom method for the 'posted_within' filter.
        """
        if value is None:
            return queryset

        unit = self.request.GET.get("posted_within_unit")

        try:
            value = int(value)
        except (ValueError, TypeError):
            return queryset

        if unit == "hours":
            delta = timedelta(hours=value)
        elif unit == "days":
            delta = timedelta(days=value)
        else:
            return queryset

        cutoff_time = timezone.now() - delta
        return queryset.filter(created_at__gte=cutoff_time)
