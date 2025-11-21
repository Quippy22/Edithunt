import calendar
from datetime import date, datetime, timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import widgets

from .models import Bounty, CustomUser, Submission


class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users, extending Django's default UserCreationForm
    to include our custom 'role' field.
    """

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Add the 'role' field to the default fields from UserCreationForm.
        fields = UserCreationForm.Meta.fields + ("role",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply a consistent CSS class to all form fields for styling.
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-input"


class DateTimeSelectWidget(widgets.MultiWidget):
    """
    A custom widget to render a DateTimeField as a set of dropdowns for
    day, month, year, hour, and minute. This provides a more user-friendly
    way to select a specific point in time than a simple text input.
    """

    template_name = "core/widgets/datetime_select.html"

    def __init__(self, attrs=None):
        # Define common attrs for the select widgets
        select_attrs = {"class": "form-input"}
        if attrs:
            select_attrs.update(attrs)

        month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]
        _widgets = (
            # The list of widgets that make up the MultiWidget.
            # They correspond to day, month, year, hour, minute.
            widgets.Select(attrs=select_attrs, choices=[(i, i) for i in range(1, 32)]),
            widgets.Select(attrs=select_attrs, choices=month_choices),
            widgets.Select(
                attrs=select_attrs,
                choices=[
                    (i, i) for i in range(date.today().year, date.today().year + 11)
                ],
            ),
            widgets.Select(
                attrs=select_attrs, choices=[(i, f"{i:02d}") for i in range(24)]
            ),
            widgets.Select(
                attrs=select_attrs, choices=[(i, f"{i:02d}") for i in range(0, 60, 5)]
            ),
        )
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        """
        Takes a single Python datetime value and splits it into a list of
        values [day, month, year, hour, minute] for each of the sub-widgets.
        """
        if isinstance(value, datetime):
            return [value.day, value.month, value.year, value.hour, value.minute]
        if isinstance(value, date):
            return [value.day, value.month, value.year, 0, 0]
        return [None, None, None, None, None]


class DateTimeMultiValueField(forms.MultiValueField):
    """
    A custom form field that works with the DateTimeSelectWidget.
    It combines the multiple values from the widget into a single datetime object.
    """

    widget = DateTimeSelectWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(),  # Day
            forms.IntegerField(),  # Month
            forms.IntegerField(),  # Year
            forms.IntegerField(),  # Hour
            forms.IntegerField(),  # Minute
        )
        super().__init__(fields=fields, require_all_fields=False, *args, **kwargs)

    def compress(self, data_list):
        """
        Takes the list of cleaned values from the sub-fields and "compresses"
        them into a single Python datetime object.
        """
        if data_list and all(data_list):
            try:
                return datetime(
                    year=data_list[2],
                    month=data_list[1],
                    day=data_list[0],
                    hour=data_list[3],
                    minute=data_list[4],
                )
            except (ValueError, TypeError):
                # Catches errors like invalid day for a month (e.g., Feb 30).
                raise forms.ValidationError("Invalid date or time.", code="invalid")
        return None


class BountyFilterForm(forms.Form):
    """
    A form used to provide the fields for the BountyFilter FilterSet.
    This form is not intended to be saved to the database directly but rather
    to collect the user's filtering criteria.
    """

    budget_min = forms.DecimalField(
        required=False, widget=forms.NumberInput(attrs={"step": "0.01"})
    )
    budget_max = forms.DecimalField(
        required=False, widget=forms.NumberInput(attrs={"step": "0.01"})
    )
    posted_within = forms.IntegerField(
        required=False,
        label="Posted within",
        widget=forms.NumberInput(attrs={"placeholder": "e.g., 3"}),
    )
    posted_within_unit = forms.ChoiceField(
        required=False,
        choices=[("days", "Days"), ("hours", "Hours")],
        label="Time unit",
    )


class BountyForm(forms.ModelForm):
    """
    A form for creating and updating Bounty objects.
    """

    # Override the 'deadline' field to use our custom widget and set a default
    # initial value of one day from now.
    deadline = DateTimeMultiValueField(initial=lambda: date.today() + timedelta(days=1))

    class Meta:
        model = Bounty
        fields = [
            "title",
            "description",
            "footage_link",
            "budget_min",
            "budget_max",
            "deadline",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply a consistent CSS class to all fields for styling,
        # except those with custom widget layouts.
        for field_name, field in self.fields.items():
            if field_name not in ["deadline", "budget_min", "budget_max"]:
                field.widget.attrs["class"] = "form-input"


class SubmissionForm(forms.ModelForm):
    """
    A form for editors to submit their work for a specific bounty.
    It only includes the fields an editor should provide.
    """

    class Meta:
        model = Submission
        fields = ["file_link"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add styling, explicit text colors to the file_link input.
        self.fields['file_link'].widget.attrs.update({
            'class': 'form-input text-gray-900 dark:text-white',
        })
