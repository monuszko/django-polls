from django.conf.urls import patterns, url

from . import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>\d+)/vote$', views.VotingForm.as_view(), name='voting_form'),
    url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<pk>\d+)/do_vote/$', views.vote, name='do_vote'),
    url(r'^create/$', views.create_poll, name='create'),
    url(r'^(?P<pk>\d+)/delete$', views.PollDelete.as_view(), name='delete'),
    url(r'^(?P<pk>\d+)/update$', views.update_poll, name='update'),
    ]
