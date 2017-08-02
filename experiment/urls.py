from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'experiment'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.ExperimentView.as_view(), name='experiment'),
    url(r'^results/$', views.ResultsView.as_view(), name='results'),
    url(r'^output/(?P<output_id>[0-9]+)/$', login_required(views.OutputView.as_view()), name='output'),
]