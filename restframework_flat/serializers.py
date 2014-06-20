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
    def __init__(self, wrapped_serializer_instance, sideload_relations, top_level=False):
        super().__init__(wrapped_serializer_instance)
        self._sideload_relations = sideload_relations
        self._top_level = top_level

    def decorate_data(self, old_data):
        payload = collections.OrderedDict()
        sideload = collections.OrderedDict()

        if self._top_level:
            payload[self.type_name] = old_data
        else:
            sideload[self.type_name] = sorted(old_data, key=sideload_sort_key)

        objects = self.object
        if not self.many:
            objects = [objects]

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

            instance = {x for rel in relations for x in rel_to_list(rel)}
            base_serializer = serializer_class(many=True, instance=instance)

            # TODO: nested sideloads!!
            serializer = SideloadDecorator(base_serializer, ())
            sideload = merge_sideloads(sideload, serializer.data)

        if self._top_level and self.type_name in sideload:
            sideload.pop(self.type_name)  # =(

        payload.update(sideload)

        return payload


def sideload_sort_key(item):
    return item['id']


def get_id_map(items):
    return {item['id']: item for item in items}


def merge_sideloads(left, right):
    ret = {}
    for key, items in right.items():
        if key not in left:
            ret[key] = items
        else:
            left_items = left[key]
            union = get_id_map(left_items)
            union.update(get_id_map(right))
            ret[key] = sorted(union.values(), key=sideload_sort_key)

    ret = collections.OrderedDict(sorted(ret.items(), key=lambda x: x[0]))
    return ret


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
