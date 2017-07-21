from django.conf.urls import url

from . import views

app_name = 'experiment'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.ExperimentView.as_view(), name='experiment'),
    url(r'^postresults/$', views.PostResultsView.as_view(), name='postresults'),
]