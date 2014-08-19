# views.py

from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render
import printqueue_ng.html as pq_html
import printqueue_ng.updater as updater

from pytz import timezone

from printers.models import Area, Printer, Job

from django.db.models import Count

HEAVY_LOAD_STATE_THRESHOLD = 7

def home(request):
	return render(request, 'home.html', {'navbar': pq_html.navbar(False, False), 'footer': pq_html.footer(), 'server': request.META['SERVER_NAME'] + ":8000"})

def area(request, name):
	this_area = None
	try:
		this_area = Area.objects.get(name = name)
	except:
		raise Http404

	updater.update(this_area)

	printers = []
	area_printers = Printer.objects.filter(area = this_area).annotate(num_jobs = Count('job')).order_by('-num_jobs')
	for printer in area_printers:
		printer_jobs = Job.objects.filter(printer = printer).order_by("position")
		state = "inactive"
		if printer.state == 1:
			state = "error"
		elif len(printer_jobs) > 0 and len(printer_jobs) < HEAVY_LOAD_STATE_THRESHOLD:
			state = "active"
		elif len(printer_jobs) >= HEAVY_LOAD_STATE_THRESHOLD:
			state = "heavy_load"
		printers.append({'printer': printer, 'jobs': printer_jobs, 'state': state,})

	update_time = this_area.last_updated.astimezone(timezone('US/Eastern'))
	hour = update_time.hour % 12
	minute = ""
	ampm = " AM"
	if hour == 0:
		hour = 12
	if update_time.hour >= 12:
		ampm = " PM"
	if update_time.minute < 10:
		minute = "0" + str(update_time.minute)
	else:
		minute = str(update_time.minute)
	update_time_string = str(update_time.month) + "/" + str(update_time.day) + ", " + str(hour) + ":" + str(minute) + ampm
	
	return render(request, 'area.html', {'navbar': pq_html.navbar(name, update_time_string), 'footer': pq_html.footer(), 'server': request.META['SERVER_NAME'] + ":8000", 'area': name, 'printers': printers,})
