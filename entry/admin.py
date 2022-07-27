from django.contrib import admin

from entry.models import Entry, Point, Lap
from entry.services.entry_fit import EntryFit


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('customer',)
    ordering = ('-created',)
    raw_id_fields = ('customer',)

    def has_change_permission(self, request, obj=None): return False


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'latitude',
        'longitude',
        'lap_number',
        'altitude',
        'timestamp',
        'heart_rate',
        'cadence',
        'speed'
    )
    list_filter = ('user', 'entry', 'timestamp')
    search_fields = ('user',)
    ordering = ('-timestamp',)
    fieldsets = (
        ('Point', {
            'fields': (
                'user', 'latitude', 'longitude',
                'lap_number', 'altitude', 'timestamp',
                'heart_rate', 'cadence', 'speed')
        }),
        ('Created', {
            'fields': ('created', 'modified')
        }),
    )
    raw_id_fields = ('user',)


@admin.register(Lap)
class LapAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'number',
        'start_time',
        'total_distance',
        'total_elapsed_time',
        'max_speed',
        'max_heart_rate',
        'avg_heart_rate'
    )
    list_filter = ('user', 'number')
    search_fields = ('user',)
    ordering = ('-start_time',)
    fieldsets = (
        ('Lap', {
            'fields': (
                'user', 'number', 'start_time',
                'total_distance', 'total_elapsed_time',
                'max_speed', 'max_heart_rate', 'avg_heart_rate')
        }),
        ('Created', {
            'fields': ('created', 'modified')
        }),
    )
    raw_id_fields = ('user',)
