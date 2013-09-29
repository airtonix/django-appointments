from django.conf.urls.defaults import *
from django.views.generic import TemplateView
from django.contrib import admin

admin.autodiscover()
urlpatterns = patterns('',
                       url(r'^admin/doc/', include(
                           'django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^appointments/', include('appointments.urls')),
                       url(r'^$', TemplateView.as_view(
                           template_name="home.html"), name="home"),
                       )
