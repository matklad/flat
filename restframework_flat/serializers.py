import collections

from django.core.paginator import Page

from django.db.models.manager import BaseManager
import inflection


class FlatSerializerMixin(object):
    @property
    def type_name(self):
        try:
            return inflection.pluralize(self.opts.model.__name__.lower())
        except AttributeError:
            raise NotImplementedError


class SerializerDataDecorator(object):
    def __init__(self, wrapped_serializer_instance):
        self._wrapped_instance = wrapped_serializer_instance

    def __getattr__(self, name):
        assert name != 'data', '`AttributeError` in data!'
        return getattr(self._wrapped_instance, name)

    @property
    def data(self):
        return self.decorate_data(self._wrapped_instance.data)

    def decorate_data(self, old_data):
        return old_data


class SideloadDecorator(SerializerDataDecorator):
    def __init__(self, wrapped_serializer_instance, sideload_relations):
        super().__init__(wrapped_serializer_instance)
        self._sideload_relations = sideload_relations

    def decorate_data(self, old_data):
        payload = collections.OrderedDict()
        payload[self.type_name] = old_data

        objects = self.object
        if not self.many:
            objects = [objects]

        sideload = {}
        for rel_name, serializer_class in self._sideload_relations:
            try:
                relations = [getattr(x, rel_name) for x in objects]
            except AttributeError:
                raise Exception("No relation {rel}!".format(rel=rel_name))

            def rel_to_list(rel):
                if isinstance(rel, collections.Iterable):
                    return list(rel)
                if isinstance(rel, BaseManager):
                    return list(rel.all())
                return [rel]

            instance = [x for rel in relations for x in rel_to_list(rel)]
            base_serializer = serializer_class(many=True, instance=instance)

            # TODO: nested sideloads!!
            serializer = SideloadDecorator(base_serializer, ())
            sideload.update(serializer.data)

        payload.update(sideload)

        return payload


class PaginationDecorator(SerializerDataDecorator):
    def decorate_data(self, old_data):
        meta = {
            'page': 1,
            'has_next': False,
            'has_previous': False
        }
        if isinstance(self.object, Page):
            meta['page'] = self.object.number
            meta['has_next'] = self.object.has_next()
            meta['has_previous'] = self.object.has_previous()
        ret = collections.OrderedDict(meta=meta)
        ret.update(old_data)
        return ret