import datetime

from django.utils import timezone
from rest_framework import filters
from utils.helpers import convert_str_to_date


class Relatedtable1IDFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        try:
            return queryset.filter(relatedtable1_id=request.GET['related_table1_id']).distinct()
        except Exception:
            return queryset


class TimeFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        try:
            hrs_filter = request.GET.get('hrs', None)
            if hrs_filter:
                last_hrs = timezone.now() - datetime.timedelta(hours=int(hrs_filter))
                return queryset.filter(created_at__gte=last_hrs).distinct()

            mins_filter = request.GET.get('mins', None)
            if mins_filter:
                last_mins = timezone.now() - datetime.timedelta(minutes=int(mins_filter))
                return queryset.filter(created_at__gte=last_mins).distinct()

            range_filter = request.GET.get('range', None)
            if range_filter:
                splitted_range = range_filter.split(',')
                start_date = convert_str_to_date(splitted_range[0])
                end_date = convert_str_to_date(splitted_range[1])
                return queryset.filter(created_at__date__range=[start_date, end_date]).distinct()

            return queryset
        except Exception:
            return queryset



