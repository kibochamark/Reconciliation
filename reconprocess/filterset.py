from random import choices

from django_filters import rest_framework as filters

from reconprocess.models import ReconResult, ReconTask


class ReconFilter(filters.FilterSet):
    status = filters.ChoiceFilter(field_name="status", choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    created_at = filters.DateFilter(field_name='created_at', lookup_expr='exact')
    created_at_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = ReconTask
        fields = ['status', 'created_at']



