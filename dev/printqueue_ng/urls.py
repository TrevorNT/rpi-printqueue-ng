from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'printqueue_ng.views.home'),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^([a-z]+)/$', 'printqueue_ng.views.area'),

    # Uncomment the next line to enable the admin:
)
