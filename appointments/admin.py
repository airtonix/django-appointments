from django.contrib import admin

from . import models


class CalendarAdminOptions(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']


admin.site.register(models.Calendar, CalendarAdminOptions)
admin.site.register([models.Rule,
                     models.Event,
                     models.CalendarRelation])
