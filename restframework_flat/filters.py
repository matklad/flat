from rest_framework.filters import BaseFilterBackend


class IdListFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        Filters posts/?ids[]=1&ids[]=2&ids[]=3.
        """
        key = "ids[]"
        ids = request.GET.getlist(key)
        if ids:
            queryset = queryset.filter(id__in=ids)
        return queryset
