from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.core import serializers
from .models import ExperimentCondition
import random
import math
import json

class IndexView(generic.ListView):
    template_name = "experiment/index.html"
    model = ExperimentCondition

class ExperimentView(generic.DetailView):
    template_name = "experiment/experiment.html"
    model = ExperimentCondition

    def get_context_data(self, **kwargs):
        context = super(ExperimentView, self).get_context_data(**kwargs)
        obj = context['object']
        signals = [random.random() < obj.p_signal for i in range(obj.num_trials)]
        normal = [random.gauss(obj.mean, obj.sd) for i in range(obj.num_trials)]
        alert_distribution = [normal[i] + 0.5 * obj.d_alert * obj.sd if s else normal[i] - 0.5 * obj.d_alert * obj.sd for (i,s) in enumerate(signals)]
        c = (math.log(obj.beta_alert) * obj.sd / obj.d_alert) + (obj.sd * obj.d_alert / 2)
        stimuli = [normal[i] + 0.5 * obj.d_user * obj.sd if s else normal[i] - 0.5 * obj.d_user * obj.sd for (i,s) in enumerate(signals)]
        alerts = [s > (obj.mean + obj.sd * c) for s in alert_distribution]
        context['signals'] = signals
        context['alerts'] = alerts
        context['stimuli'] = stimuli
        context['alert_dist'] = alert_distribution
        context['c'] = c
        context['data'] = json.dumps({"obj":serializers.serialize("json", [obj]),"signals":signals,"alerts":alerts,"stimuli":stimuli})
        return context