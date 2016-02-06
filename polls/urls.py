from django.conf.urls import patterns, url

from . import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^create/$', views.create_poll, name='create'),
    url(r'^delete/(?P<pk>\d+)/$', views.PollDelete.as_view(), name='delete'),
    url(r'^update/(?P<pk>\d+)/$', views.update_poll, name='update'),
    ]
