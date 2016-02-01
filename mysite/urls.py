from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url('^', include('django.contrib.auth.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
