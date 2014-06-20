from rest_framework.response import Response

from restframework_flat import FlatSerializerMixin
from restframework_flat.filters import IdListFilterBackend
from restframework_flat.serializers import SideloadDecorator, PaginationDecorator


class FlatViewSetMixin(object):
    def get_filter_backends(self):
        return [IdListFilterBackend] + super().get_filter_backends()

    def get_sideload_relations(self):
        try:
            return self.sideload_relations
        except AttributeError:
            return []

    def get_serializer(self, instance=None, data=None, files=None, many=False,
                       partial=False, allow_add_remove=False):
        base_serializer = super().get_serializer(instance, data, files, many, partial, allow_add_remove)
        assert isinstance(base_serializer, FlatSerializerMixin)
        if instance is None or not many:
            return base_serializer
        return PaginationDecorator(SideloadDecorator(base_serializer, self.get_sideload_relations()))

    def get_pagination_serializer(self, page):
        return self.get_serializer(instance=page, many=True)

    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer([self.object], many=True)
        return Response(serializer.data)

