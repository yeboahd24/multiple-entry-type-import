from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.translation import ugettext_lazy as _


class Entry(models.Model):
    """Entry model
    user fitness tracker export file upload and processing
    """
    file = models.FileField(
        _('File'),
        upload_to='entry/files/',
        validators=[
            FileExtensionValidator(allowed_extensions=['csv', 'fit', 'gpx', 'kml', 'tcx'])
        ]
    )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Customer'))
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    modified = models.DateTimeField(_('Modified'), auto_now=True)

    def __str__(self):
        return 'Entry {}'.format(self.file.name)

    class Meta:
        verbose_name = _('Entry')
        verbose_name_plural = _('Entries')
        ordering = ('-created',)


class Point(models.Model):
    """Point model
    fitness tracker each point record data
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, verbose_name=_('Entry'))
    latitude = models.FloatField(_('Latitude'), null=True, blank=True)
    longitude = models.FloatField(_('Longitude'), null=True, blank=True)
    lap_number = models.IntegerField(
        _('Lap number'), help_text=_('NOTE: It is not unique, just useful in multiple laps'),
        null=True, blank=True)
    altitude = models.FloatField(_('Altitude'), null=True, blank=True)
    timestamp = models.DateTimeField(_('Timestamp'), null=True, blank=True)
    heart_rate = models.FloatField(_('Heart rate'), null=True, blank=True)
    cadence = models.FloatField(_('cadence'), null=True, blank=True)
    speed = models.FloatField(_('Speed'), null=True, blank=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    modified = models.DateTimeField(_('Modified'), auto_now=True)

    def __str__(self):
        return 'Point {} - {}'.format(self.latitude, self.longitude)

    class Meta:
        verbose_name = _('Point')
        verbose_name_plural = _('Points')
        ordering = ('-created',)


class Lap(models.Model):
    """Lap model
    fitness tracker each lap data
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, verbose_name=_('Entry'))
    number = models.IntegerField(
        _('Number'), help_text=_('NOTE: It is not unique, just useful in multiple laps'),
        null=True, blank=True)
    start_time = models.DateTimeField(_('Start time'), null=True, blank=True)
    total_distance = models.FloatField(_('Total distance'), null=True, blank=True)
    total_elapsed_time = models.FloatField(_('Total elapsed time'), null=True, blank=True)
    max_speed = models.FloatField(_('Max speed'), null=True, blank=True)
    max_heart_rate = models.FloatField(_('Max heart rate'), null=True, blank=True)
    avg_heart_rate = models.FloatField(_('Avg heart rate'), null=True, blank=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    modified = models.DateTimeField(_('Modified'), auto_now=True)

    def __str__(self):
        return 'Lap {}'.format(self.entry.file.name)

    class Meta:
        verbose_name = _('Lap')
        verbose_name_plural = _('Laps')
        ordering = ('-created',)
