from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from tastypie import http


class ContainsNestedResourcesMixin(object):

    def get_obj_detail(self, request, **kwargs):
        """
        Returns a single serialized resource.

        Calls ``cached_obj_get/obj_get`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        basic_bundle = self.build_bundle(request=request)

        try:
            obj = self.cached_obj_get(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        return obj

    def get_child_list(self, request, resource, **kwargs):
        """
        reqest
            standard request
        resource
            the nested resource
        kwargs.queryset_filter
            a complex queryset filter

        Returns a serialized list of resources.

        Note
            This method exists soley to grab a list of related files which have no
            direct ORM relationship, except via generic foreign keys. By passing Q() filters,
            the queryset can be restricted.

            This is because there doesn't seem to be a tastypie resource method that allows you to
            simply pass in complex queryset filters.

        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).


        """
        # TODO: Uncached for now. Invalidation that works for everyone may be
        #       impossible.
        base_bundle = resource.build_bundle(request=request)
        objects = resource.obj_get_list(bundle=base_bundle, **resource.remove_api_resource_names(kwargs))

        queryset_filter = kwargs.pop('queryset_filter')
        if queryset_filter:
            objects = objects.filter(queryset_filter)

        sorted_objects = resource.apply_sorting(objects, options=request.GET)

        paginator = resource._meta.paginator_class(request.GET, sorted_objects,
                                                   resource_uri=resource.get_resource_uri(),
                                                   limit=resource._meta.limit,
                                                   max_limit=resource._meta.max_limit,
                                                   collection_name=resource._meta.collection_name)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = []

        for obj in to_be_serialized[resource._meta.collection_name]:
            bundle = resource.build_bundle(obj=obj, request=request)
            bundles.append(resource.full_dehydrate(bundle))

        to_be_serialized[resource._meta.collection_name] = bundles
        to_be_serialized = resource.alter_list_data_to_serialize(request, to_be_serialized)
        return resource.create_response(request, to_be_serialized)
