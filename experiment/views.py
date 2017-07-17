from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.core import serializers
from .models import ExperimentCondition, Experiment, Questionnaire, TextBlock
import random
import math
import json

class IndexView(generic.ListView):
    template_name = "experiment/index.html"
    model = Experiment

class ExperimentView(generic.DetailView):
    template_name = "experiment/experiment.html"
    model = Experiment

    def get_context_data(self, **kwargs):
        context = super(ExperimentView, self).get_context_data(**kwargs)
        obj = context['object']
        modules = []
        for module in obj.modules.all():
            content = module.content_object
            if type(content) is ExperimentCondition:
                user_mean_s = content.mean + 0.5 * content.d_user * content.sd
                user_mean_n = content.mean - 0.5 * content.d_user * content.sd
                alert_mean_s = content.mean + 0.5 * content.d_alert * content.sd
                alert_mean_n = content.mean - 0.5 * content.d_alert * content.sd
                signals = [random.random() < content.p_signal for i in range(content.num_trials)]
                alert_distribution = [random.gauss(alert_mean_s, content.sd) if s else random.gauss(alert_mean_n, content.sd) for (i,s) in enumerate(signals)]
                c = (math.log(content.beta_alert) / content.d_alert)
                stimuli = [round(random.gauss(user_mean_s, content.sd), content.num_dec_places) if s else round(random.gauss(user_mean_n, content.sd), content.num_dec_places) for (i,s) in enumerate(signals)]
                alerts = [a > content.mean + c for a in alert_distribution]
                modules.append({"obj":json.loads(serializers.serialize("json", [content])),"signals":signals,"alerts":alerts,"stimuli":stimuli})
            elif type(content) is Questionnaire:
                questions = [[q.text, q.choices.split(",")] for q in content.questions.all()]
                modules.append({"obj":json.loads(serializers.serialize("json", [content])), "questions":questions})
            elif type(content) is TextBlock:
                modules.append(json.loads(serializers.serialize("json", [content])))
        context['modules'] = json.dumps(modules)
        return context