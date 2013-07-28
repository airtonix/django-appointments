from tastypie import fields
from tastypie.resources import ModelResource, ALL

from ..models import Event


class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'


EnabledResources = (
    EventResource,
)
