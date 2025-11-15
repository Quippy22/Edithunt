from django import forms
from django.contrib.auth.forms import UserCreationForm
from datetime import date, datetime, timedelta
from django.forms import widgets
import calendar

from .models import Bounty, CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("role",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-input"


class DateTimeSelectWidget(widgets.MultiWidget):
    template_name = 'core/widgets/datetime_select.html'

    def __init__(self, attrs=None):
        month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]
        _widgets = (
            widgets.Select(attrs=attrs, choices=[(i, i) for i in range(1, 32)]), # Day
            widgets.Select(attrs=attrs, choices=month_choices), # Month
            widgets.Select(attrs=attrs, choices=[(i, i) for i in range(date.today().year, date.today().year + 11)]), # Year
            widgets.Select(attrs=attrs, choices=[(i, f"{i:02d}") for i in range(24)]),  # Hour
            widgets.Select(attrs=attrs, choices=[(i, f"{i:02d}") for i in range(0, 60, 5)]),  # Minute
        )
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if isinstance(value, datetime):
            return [value.day, value.month, value.year, value.hour, value.minute]
        if isinstance(value, date):
            return [value.day, value.month, value.year, 0, 0]
        return [None, None, None, None, None]

class DateTimeMultiValueField(forms.MultiValueField):
    widget = DateTimeSelectWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(), # Day
            forms.IntegerField(), # Month
            forms.IntegerField(), # Year
            forms.IntegerField(), # Hour
            forms.IntegerField(), # Minute
        )
        super().__init__(fields=fields, require_all_fields=True, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            try:
                return datetime(
                    year=data_list[2],
                    month=data_list[1],
                    day=data_list[0],
                    hour=data_list[3],
                    minute=data_list[4]
                )
            except (ValueError, TypeError):
                raise forms.ValidationError("Invalid date or time.", code='invalid')
        return None


class BountyForm(forms.ModelForm):
    deadline = DateTimeMultiValueField(
        initial=lambda: date.today() + timedelta(days=1)
    )

    class Meta:
        model = Bounty
        fields = ["title", "description", "footage_link", "budget_min", "budget_max", "deadline"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ["deadline", "budget_min", "budget_max"]:
                field.widget.attrs["class"] = "form-input"
