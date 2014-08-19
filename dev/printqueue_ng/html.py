# html.py
from printers.models import Area

def navbar(active_tab, last_update):
	return_value = """
		<div class="navbar navbar-default navbar-static-top" role="navigation">
			<div class="container">
				<div class="navbar-header">
					<button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
						<span class="sr-only">Toggle navigation</span>
						<span class="icon-bar"></span>
						<span class="icon-bar"></span>
						<span class="icon-bar"></span>
					</button>
					<a class="navbar-brand" href="/">HD Print Queue</a>
				</div>
				<div class="navbar-collapse collapse">
					<ul class="nav navbar-nav">"""

	all_areas = Area.objects.all().order_by("id")

	active_is_a_main_tab = False
	if not active_tab:
		active_is_a_main_tab = True

	for area in all_areas:
		if area.id < 8:
			if active_tab == area.name:
				return_value += area.get_active_html()
				active_is_a_main_tab = True
			else:
				return_value += area.get_inactive_html()
		elif area.id == 8:
			if not active_is_a_main_tab:
				return_value += "<li class='dropdown active'>"
			else:
				return_value += "<li class='dropdown'>"
			return_value += "<a href='#' class='dropdown-toggle' data-toggle='dropdown'>Other Areas <b class='caret'></b></a>"
			return_value += "<ul class='dropdown-menu'>"
			if active_tab == area.name:
				return_value += area.get_active_html()
			else:
				return_value += area.get_inactive_html()
		else:
			if active_tab == area.name:
				return_value += area.get_active_html()
			else:
				return_value += area.get_inactive_html()

	return_value += "</ul>"
	return_value += "</li>"
	return_value += "</ul>"

	if last_update:
		return_value += """
					<ul class="nav navbar-nav navbar-right">
						<li><a href="#">Updated: %s</a></li>
					</ul>""" % last_update
	return_value += """
				</div>
			</div>
		</div>
	"""

	return return_value

def footer():
	return """
	<div id="footer">
		<div class="container">
			<p class="text-muted"><span>Created by <a href="mailto:trevt93@gmail.com">Trevor Toryk</a>, for Rensselaer Polytechnic Institute.</span>
			<span style="float: right;">Maintained by the <a href="http://helpdesk.rpi.edu/">VCC Help Desk</a> (x7777 or (518) 276-7777).</span></p>
		</div>
	</div>"""
