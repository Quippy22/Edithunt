import django_filters
from .models import Bounty
from .forms import BountyFilterForm

class BountyFilter(django_filters.FilterSet):
    deadline_start = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='gte')
    deadline_end = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='lte')

    class Meta:
        model = Bounty
        form = BountyFilterForm
        fields = ['budget_min', 'budget_max', 'deadline_start', 'deadline_end']
