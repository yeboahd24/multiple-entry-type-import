from django.dispatch import receiver
from django.db.models.signals import post_save

from entry.models import Entry
from entry.services.entry_csv import EntryCsv
from entry.services.entry_fit import EntryFit
from entry.services.entry_gpx import EntryGpx
from entry.services.entry_tcx import EntryTcx


@receiver(post_save, sender=Entry)
def entry_post_save(sender, instance, created, **kwargs):
    if created:
        file_extension = instance.file.name.split('.')[-1]
        if file_extension == 'csv':
            entry_csv = EntryCsv(instance)
            entry_csv.run()
        elif file_extension == 'fit':
            entry_fit = EntryFit(instance)
            entry_fit.run()
        elif file_extension == 'gpx':
            entry_gpx = EntryGpx(instance)
            entry_gpx.run()
        elif file_extension == 'tcx':
            entry_tcx = EntryTcx(instance)
            entry_tcx.run()
        else:
            raise Exception('File extension not supported')
