# updater.py

import paramiko

from printers.models import Area, Printer, Job

import datetime
import pytz
import re

SSH_SERVER = 'rcs-linux.rpi.edu'
SSH_USERNAME = 'so19'
SSH_PASSWORD = '4printqu'

# Customize these to your liking
UPDATE_INTERVAL_MINUTES = 2
UPDATE_INTERVAL_SECONDS = 0

def update(area):
	if not type(area) is Area:
		raise TypeError("area object is not of type printers.Area")

	if area.last_updated + datetime.timedelta(minutes = UPDATE_INTERVAL_MINUTES, seconds = UPDATE_INTERVAL_SECONDS) > datetime.datetime.now(pytz.utc):	# (That "None" means "not timezone aware".  Long story.  Leave that the way it is unless you can figure out how to preload the initial_data.json with timezone-aware data.)
		return	# It's not time to update yet

	rcs_ssh = paramiko.SSHClient()
	rcs_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	rcs_ssh.connect(SSH_SERVER, username = SSH_USERNAME, password = SSH_PASSWORD)

	all_printers = Printer.objects.filter(area = area)

	for printer in all_printers:
		inp, outp, err = rcs_ssh.exec_command("lpq -P " + printer.name)
		output = outp.readlines()

		if len(output) == 1 and "no entries" in output[0].lower():
			Job.objects.filter(printer = printer).delete()	# Statement evaluates to: get all jobs by this printer and then delete them.
			if printer.state != Printer.OPERATIONAL:
				printer.state = Printer.OPERATIONAL
				printer.save()

		elif len(output) == 1 and "printer not found" in output[0].lower():
			Job.objects.filter(printer = printer).delete()	# ...just in case.  For the most part, if it's not in lpq anymore, it won't ever have any jobs.

			printer.state = Printer.ERROR
			printer.error_message = "The queue of this printer is not available."

			printer.save()

		elif len(output) >= 1 and "printererror: check printer" in output[0].lower():
			Job.objects.filter(printer = printer).delete()

			printer.state = Printer.ERROR
			printer.error_message = "Printer is not printing.  Please check the printer for an error message."
			printer.save()
			if len(output) >= 3 and output[1].lower().split() == ['rank', 'owner', 'job', 'files', 'total', 'size']:
				parse_jobs(output[2:], printer)

		elif len(output) >= 1 and "is down:" in output[0].lower():
			Job.objects.filter(printer = printer).delete()

			printer.state = Printer.ERROR
			printer.error_message = output[0][(output[0].lower().find("down:") + 6):]

			if printer.error_message.strip() == "":
				printer.error_message = "Printer is down."
			printer.save()

			if len(output) >= 3 and output[1].lower().split() == ['rank', 'owner', 'job', 'files', 'total', 'size']:
				parse_jobs(output[2:], printer)
			elif len(output) >= 4 and output[2].lower().split() == ['rank', 'owner', 'job', 'files', 'total', 'size']:
				parse_jobs(output[3:], printer)

		elif len(output) >= 1 and "problems finding printer" in output[0].lower():
			Jobs.objects.filter(printer = printer).delete()

			printer.state = Printer.ERROR
			printer.error_message = "Printer is experiencing network problems."
			printer.save()

			if len(output) >= 3 and output[1].lower().split() == ['rank', 'owner', 'job', 'files', 'total', 'size']:
				parse_jobs(output[2:], printer)
			elif len(output) >= 4 and output[2].lower().split() == ['rank', 'owner', 'job', 'files', 'total', 'size']:
				parse_jobs(output[3:], printer)
			
			
		elif len(output) >= 2 and output[1].lower().split() == ['rank', 'owner', 'job', 'files', 'total', 'size']:
			if "status: busy" in output[0].lower():
				if printer.state != Printer.OPERATIONAL:
					printer.state = Printer.OPERATIONAL
					printer.save()
			else:
				if printer.state != Printer.ERROR:
					printer.state = Printer.ERROR

				if output[0].lower().find("status: ") != 0:
					printer.error_message = output[0][(output[0].lower().find("status: ") + 8):].strip()
				else:
					print "Unknown printer status condition:\n" + output[0]
				printer.save()

			if printer.state != Printer.OPERATIONAL:
				printer.state = Printer.OPERATIONAL
				printer.save()

			Job.objects.filter(printer = printer).delete()
			parse_jobs(output[2:], printer)
					
		else:
			print "Unexpected condition in lpq status report:"
			for line in output:
				print "\t" + line

	area.save()	# Just using save() should, in theory, update the last_updated time field in the database.  In theory.
	rcs_ssh.close()

def parse_jobs(jobs, printer):
	for job in jobs:
		output_tokens = job.split()
		newjob = Job()
		# Get the location in the printer's queue that this job is.  "active" == 0, "1st" will evaluate to 1, etc.
		if "active" in output_tokens[0]:
			newjob.position = 0
		else:
			newjob.position = int(re.findall('\d+', output_tokens[0])[0])
		# Get the username
		newjob.user_id = output_tokens[1]
		# Get the job ID #
		newjob.job_number = int(output_tokens[2])
		# Get the job name
		name_string = ""
		for piece in output_tokens[3:-2]:
			name_string += piece
		newjob.name = name_string
		# Identify the printer
		newjob.printer = printer
		# Finally, save the job to the db
		newjob.save()
	# Do this until jobs has been fully processed.
