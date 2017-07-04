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
        user_mean_s = obj.mean + 0.5 * obj.d_user * obj.sd
        user_mean_n = obj.mean - 0.5 * obj.d_user * obj.sd
        alert_mean_s = obj.mean + 0.5 * obj.d_alert * obj.sd
        alert_mean_n = obj.mean - 0.5 * obj.d_alert * obj.sd
        signals = [random.random() < obj.p_signal for i in range(obj.num_trials)]
        alert_distribution = [random.gauss(alert_mean_s, obj.sd) if s else random.gauss(alert_mean_n, obj.sd) for (i,s) in enumerate(signals)]
        c = (math.log(obj.beta_alert) / obj.d_alert)
        stimuli = [round(random.gauss(user_mean_s, obj.sd), obj.num_dec_places) if s else round(random.gauss(user_mean_n, obj.sd), obj.num_dec_places) for (i,s) in enumerate(signals)]
        alerts = [a > c for a in alert_distribution]
        context['signals'] = signals
        context['alerts'] = alerts
        context['stimuli'] = stimuli
        context['alert_dist'] = alert_distribution
        context['c'] = c
        context['data'] = json.dumps({"obj":serializers.serialize("json", [obj]),"signals":signals,"alerts":alerts,"stimuli":stimuli})
        return context