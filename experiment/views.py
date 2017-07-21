from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic, View
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .models import *
import random
import math
import json
from datetime import datetime

class IndexView(generic.ListView):
    template_name = "experiment/index.html"
    model = Experiment

@method_decorator(ensure_csrf_cookie, name="dispatch")
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
                questions = [[q.text, q.choices.split(","), q.id] for q in content.questions.all()]
                modules.append({"obj":json.loads(serializers.serialize("json", [content])), "questions":questions})
            elif type(content) is TextBlock:
                modules.append(json.loads(serializers.serialize("json", [content])))
        context['modules'] = json.dumps(modules)
        return context

class PostResultsView(View):
    def post(self, request):
        data = request.POST
        print(data)
        experiment_instance = Experiment.objects.get(pk=data['experiment_id'])
        experiment_result_instance = ExperimentResult(experiment=experiment_instance)
        experiment_result_instance.save()
        experiment_blocks = json.loads(data['experiment_blocks'])
        questionnaires = json.loads(data['questionnaires'])
        for questionnaire in questionnaires:
            questionnaire_instance = Questionnaire.objects.get(pk=questionnaire['id'])
            questionnaire_result_instance = QuestionnaireResult(questionnaire=questionnaire_instance, experiment_result=experiment_result_instance)
            questionnaire_result_instance.save()
            for question in questionnaire['questions']:
                question_instance = Question.objects.get(pk=question['id'])
                question_result_instance = QuestionResult(question=question_instance, questionnaire_result=questionnaire_result_instance, answer=question['answer'])
                question_result_instance.save()
        for experiment_block in experiment_blocks:
            experiment_condition_instance = ExperimentCondition.objects.get(pk=experiment_block['id'])
            hit_alert_i = sum([1 if t['outcome'] == 'hit_s' else 0 for t in experiment_block['trials']])
            miss_alert_i = sum([1 if t['outcome'] == 'miss_s' else 0 for t in experiment_block['trials']])
            fa_alert_i = sum([1 if t['outcome'] == 'fa_n' else 0 for t in experiment_block['trials']])
            cr_alert_i = sum([1 if t['outcome'] == 'cr_n' else 0 for t in experiment_block['trials']])
            hit_no_alert_i = sum([1 if t['outcome'] == 'hit_n' else 0 for t in experiment_block['trials']])
            miss_no_alert_i = sum([1 if t['outcome'] == 'miss_n' else 0 for t in experiment_block['trials']])
            fa_no_alert_i = sum([1 if t['outcome'] == 'fa_s' else 0 for t in experiment_block['trials']])
            cr_no_alert_i = sum([1 if t['outcome'] == 'cr_s' else 0 for t in experiment_block['trials']])
            p_hit_alert_i = float(hit_alert_i) / (hit_alert_i + miss_alert_i) if (hit_alert_i + miss_alert_i > 0) else 0
            p_fa_alert_i = float(fa_alert_i) / (fa_alert_i + cr_alert_i) if (fa_alert_i + cr_alert_i > 0) else 0
            p_hit_no_alert_i = float(hit_no_alert_i) / (hit_no_alert_i + miss_no_alert_i) if (hit_no_alert_i + miss_no_alert_i > 0) else 0
            p_fa_no_alert_i = float(fa_no_alert_i) / (fa_no_alert_i + cr_no_alert_i) if (fa_no_alert_i + cr_no_alert_i > 0) else 0
            rt_hit_i = sum([float(t['response_time'])/1000 if t['outcome'][:-2] == 'hit' else 0 for t in experiment_block['trials']])/len(experiment_block['trials'])
            rt_miss_i = sum([float(t['response_time'])/1000 if t['outcome'][:-2] == 'miss' else 0 for t in experiment_block['trials']])/len(experiment_block['trials'])
            block_result_instance = BlockResult(experiment_condition=experiment_condition_instance, experiment_result=experiment_result_instance, score=experiment_block['score'], hit_alert=hit_alert_i, miss_alert=miss_alert_i, fa_alert=fa_alert_i, cr_alert=cr_alert_i, hit_no_alert=hit_no_alert_i, miss_no_alert=miss_no_alert_i, fa_no_alert=fa_no_alert_i, cr_no_alert=cr_no_alert_i, p_hit_alert=p_hit_alert_i, p_fa_alert=p_fa_alert_i, p_hit_no_alert=p_hit_no_alert_i, p_fa_no_alert=p_fa_no_alert_i, rt_hit=rt_hit_i, rt_miss=rt_miss_i)
            block_result_instance.save()
            for trial in experiment_block['trials']:
                time_i = datetime.fromtimestamp(float(trial['time'])/1000)
                trial_result_instance = TrialResult(block_result=block_result_instance, num_trial=trial['trial_num'], time=time_i, response_time=float(trial['response_time'])/1000, signal=trial['signal'], alert=trial['alert'], response=trial['response'], outcome=trial['outcome'])
                trial_result_instance.save()
        return HttpResponse('Success!')