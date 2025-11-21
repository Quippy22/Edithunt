from datetime import timedelta

import django_filters
from django import forms
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import Bounty


class BountyFilter(django_filters.FilterSet):
    """
    A custom filter set for the Bounty model to enable complex filtering on the bounty board.
    """

    # NOTE: The budget filters use a no-op lambda for their method because the default
    # 'gte' and 'lte' lookups are insufficient for range overlap. The actual filtering
    # logic is deferred to the custom `filter_queryset` method below.
    budget_min = django_filters.NumberFilter(
        label="Min Budget",
        method=lambda qs, n, v: qs,  # Defer to filter_queryset
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
    )
    budget_max = django_filters.NumberFilter(
        label="Max Budget",
        method=lambda qs, n, v: qs,  # Defer to filter_queryset
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
    )

    posted_within = django_filters.NumberFilter(
        method="filter_by_posted_within",
        label="Posted within",
        widget=forms.NumberInput(
            attrs={"class": "form-input", "placeholder": "e.g., 3"}
        ),
    )
    # This filter's method is a no-op because this field is not for filtering directly.
    # It only provides data ('days' or 'hours') for the `posted_within` filter's method.
    # It is included here so that `django-filter` correctly renders it in the form.
    posted_within_unit = django_filters.ChoiceFilter(
        choices=[("days", "Days"), ("hours", "Hours")],
        method=lambda qs, n, v: qs,
        label="Time unit",
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    class Meta:
        model = Bounty
        fields = ["budget_min", "budget_max", "posted_within", "posted_within_unit"]

    def filter_queryset(self, queryset):
        """
        Overrides the default filter method to implement custom budget filtering logic.
        """
        # This will call the methods for filters that have one, like 'posted_within',
        # but not for the budget filters, which have a no-op lambda.
        queryset = super().filter_queryset(queryset)

        # To handle bounties with a fixed price (where `budget_max` is null),
        # we create an 'effective high price' by taking budget_max if it exists,
        # or falling back to budget_min.
        queryset = queryset.annotate(high_price=Coalesce("budget_max", "budget_min"))

        budget_min = self.form.cleaned_data.get("budget_min")
        budget_max = self.form.cleaned_data.get("budget_max")

        if budget_min is not None and budget_max is not None:
            # Case: User provides a min and max budget.
            # A bounty is a match if its budget range overlaps with the user's specified range.
            # The overlap condition is: (BountyStart <= UserMax) AND (BountyEnd >= UserMin)
            queryset = queryset.filter(
                budget_min__lte=budget_max, high_price__gte=budget_min
            )
        elif budget_min is not None:
            # Case: User provides only a min budget.
            # A bounty is a match if its effective high price is at least the user's min.
            queryset = queryset.filter(high_price__gte=budget_min)
        elif budget_max is not None:
            # Case: User provides only a max budget.
            # A bounty is a match if its starting price is no more than the user's max.
            queryset = queryset.filter(budget_min__lte=budget_max)

        return queryset

    def filter_by_posted_within(self, queryset, name, value):
        """
        Filters bounties posted within a certain number of days or hours.
        """
        if value is None:
            return queryset

        unit = self.request.GET.get("posted_within_unit")

        # The `value` from a NumberFilter is a Decimal. `timedelta` requires an int or float.
        try:
            value = int(value)
        except (ValueError, TypeError):
            return queryset  # Ignore if value is not a valid integer

        if unit == "hours":
            delta = timedelta(hours=value)
        elif unit == "days":
            delta = timedelta(days=value)
        else:
            # If a value is given but the unit is invalid/missing, don't filter.
            return queryset

        return queryset.filter(created_at__gte=timezone.now() - delta)
