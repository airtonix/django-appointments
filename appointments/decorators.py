from django.db.models.loading import get_model
from django.http import HttpResponseRedirect

from .conf import settings


Event = get_model('appointments', 'Event')


def check_event_permissions(func):

    def inner(self, request, *args, **kwargs):
        try:
            event = Event.objects.get(pk=kwargs.get('pk', None))
        except Event.DoesNotExist:
            event = None

        if not settings.APPOINTMENTS_CHECK_PERMISSION_FUNC(event, request.user):
            return HttpResponseRedirect(settings.LOGIN_URL)

        return self.func(request, *args, **kwargs)
