from django.conf.urls import *
from django.contrib import admin

admin.autodiscover()


#regex to view function mapping
urlpatterns = patterns('roommeet.views',
    url(r'^$', 'meet'),
    url(r'^meet/$', 'meet'),
    url(r'^/$', 'talk'),
	url(r'^get_marks/$', 'get_marks'),
    url(r'^meet_person/$', 'meet_person'),
    url(r'^remove_person/$', 'remove_person'),
    url(r'^admin/', include(admin.site.urls)),
)

#CAS
urlpatterns += patterns('',
    url(r'^accounts/login/$', 'django_cas.views.login'),
    url(r'^accounts/logout/$', 'django_cas.views.logout'),
    #url(r'^facebook/', include('django_facebook.urls')),
    #url(r'^fbaccounts/', include('django_facebook.auth_urls')),
)
