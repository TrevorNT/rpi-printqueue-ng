from django.contrib import admin
from printers.models import Area, Printer, Job

# Register your models here.

admin.site.register(Area)
admin.site.register(Printer)
admin.site.register(Job)
