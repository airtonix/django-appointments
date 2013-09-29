import oembed
from oembed.providers import DjangoProvider
from omebed.resources import OEmbedResource


class ScheduleResource(OEmbedResource):
    pass


class EntryProvider(DjangoProvider):
    resource_type = 'rich'
