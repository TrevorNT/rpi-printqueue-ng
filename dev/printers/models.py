from django.db import models

# Create your models here.
class Area(models.Model):
	name = models.CharField(max_length = 32)
	friendly_name = models.CharField(max_length = 128)
	last_updated = models.DateTimeField(auto_now = True, auto_now_add = True)

	def get_active_html(self):
		return '<li class="active"><a href="/' + self.name + '/">' + self.friendly_name + '</a></li>'

	def get_inactive_html(self):
		return '<li><a href="/' + self.name + '/">' + self.friendly_name + '</a></li>'

	def __unicode__(self):
		return self.friendly_name

class Printer(models.Model):
	OPERATIONAL = 0
	ERROR = 1
	states = (
		(OPERATIONAL, "Operational"),
		(ERROR, "Error")
	)

	name = models.CharField(max_length = 32, unique = True)
	friendly_name = models.CharField(max_length = 128)
	state = models.IntegerField(choices = states)
	error_message = models.CharField(max_length = 64, null = True, blank = True)
	area = models.ForeignKey(Area)

	def __unicode__(self):
		return self.name

class Job(models.Model):
	job_number = models.IntegerField()
	position = models.IntegerField()
	user_id = models.CharField(max_length = 9)
	name = models.CharField(max_length = 128)
	printer = models.ForeignKey(Printer)

	def __unicode__(self):
		return self.name
