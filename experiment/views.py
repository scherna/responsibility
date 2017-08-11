from django.shortcuts import render
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.views import generic, View
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .models import *
import csv
import random
import math
import json
from datetime import datetime

class IndexView(generic.ListView):
    template_name = "experiment/index.html"
    model = Experiment

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ExperimentView(generic.DetailView):
    template_name = "experiment/experiment.html"
    model = Experiment

    def get_context_data(self, **kwargs):
        context = super(ExperimentView, self).get_context_data(**kwargs)
        obj = context['object']
        modules = []
        for module in obj.modules.all():
            content = module.content_object
            if type(content) is Block:
                user_mean_s = content.mean + 0.5 * content.d_user * content.sd
                user_mean_n = content.mean - 0.5 * content.d_user * content.sd
                alert_mean_s = content.mean + 0.5 * content.d_alert * content.sd
                alert_mean_n = content.mean - 0.5 * content.d_alert * content.sd
                signals = [random.random() < content.p_signal for i in range(content.num_trials)]
                alert_distribution = [random.gauss(alert_mean_s, content.sd) if s else random.gauss(alert_mean_n, content.sd) for (i,s) in enumerate(signals)]
                c = content.mean + ((math.log(content.beta_alert) * content.sd)  / content.d_alert)
                stimuli = [round(random.gauss(user_mean_s, content.sd), content.num_dec_places) if s else round(random.gauss(user_mean_n, content.sd), content.num_dec_places) for (i,s) in enumerate(signals)]
                alerts = [a > c for a in alert_distribution]
                modules.append({"obj":json.loads(serializers.serialize("json", [content])),"signals":signals,"alerts":alerts,"stimuli":stimuli})
            elif type(content) is Questionnaire:
                questions = [[q.text, q.choices.split(","), q.id] for q in content.questions.all()]
                modules.append({"obj":json.loads(serializers.serialize("json", [content])), "questions":questions})
            elif type(content) is Text:
                modules.append(json.loads(serializers.serialize("json", [content])))
            elif type(content) is Example:
                modules.append(json.loads(serializers.serialize("json", [content])))
        context['modules'] = json.dumps(modules)
        return context

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ResultsView(View):

    def post(self, request):
        data = request.POST
        experiment_i = Experiment.objects.get(pk=data['experiment_id'])
        experiment_result_i = ExperimentResult(experiment=experiment_i)
        experiment_result_i.save()
        blocks = json.loads(data['blocks'])
        questionnaires = json.loads(data['questionnaires'])
        for questionnaire in questionnaires:
            questionnaire_i = Questionnaire.objects.get(pk=questionnaire['id'])
            questionnaire_result_i = QuestionnaireResult(questionnaire=questionnaire_i, experiment_result=experiment_result_i)
            questionnaire_result_i.save()
            for question in questionnaire['questions']:
                question_i = Question.objects.get(pk=question['id'])
                question_result_i = QuestionResult(question=question_i, questionnaire_result=questionnaire_result_i, answer=question['answer'])
                question_result_i.save()
        for block in blocks:
            block_i = Block.objects.get(pk=block['id'])
            hit_list = [t for t in block['trials'] if t['outcome'][:-2] == 'hit']
            miss_list = [t for t in block['trials'] if t['outcome'][:-2] == 'miss']
            fa_list = [t for t in block['trials'] if t['outcome'][:-2] == 'fa']
            cr_list = [t for t in block['trials'] if t['outcome'][:-2] == 'cr']
            hit_alertsignal_list = [t for t in block['trials'] if t['outcome'] == 'hit_s']
            miss_alertsignal_list = [t for t in block['trials'] if t['outcome'] == 'miss_s']
            fa_alertsignal_list = [t for t in block['trials'] if t['outcome'] == 'fa_s']
            cr_alertsignal_list = [t for t in block['trials'] if t['outcome'] == 'cr_s']
            hit_alertnoise_list = [t for t in block['trials'] if t['outcome'] == 'hit_n']
            miss_alertnoise_list = [t for t in block['trials'] if t['outcome'] == 'miss_n']
            fa_alertnoise_list = [t for t in block['trials'] if t['outcome'] == 'fa_n']
            cr_alertnoise_list = [t for t in block['trials'] if t['outcome'] == 'cr_n']
            hits_i = len(hit_list)
            misses_i = len(miss_list)
            fa_i = len(fa_list)
            cr_i = len(cr_list)
            p_hit_i = float(hits_i) / (hits_i + misses_i) if (hits_i + misses_i > 0) else 0
            p_miss_i = float(misses_i) / (hits_i + misses_i) if (hits_i + misses_i > 0) else 0
            p_fa_i = float(fa_i) / (fa_i + cr_i) if (fa_i + cr_i > 0) else 0
            p_cr_i = float(cr_i) / (fa_i + cr_i) if (fa_i + cr_i > 0) else 0
            if 0 < p_hit_i < 1:
                z_hit_i = normal_CDF_inverse(p_hit_i)
            elif p_hit_i < 1:
                z_hit_i = normal_CDF_inverse(1.0/(2 * (hits_i + misses_i)))
            else:
                z_hit_i = normal_CDF_inverse(1 - 1.0/(2 * (hits_i + misses_i)))
            if 0 < p_fa_i < 1:
                z_fa_i = normal_CDF_inverse(p_fa_i)
            elif p_fa_i < 1:
                z_fa_i = normal_CDF_inverse(1.0/(2 * (fa_i + cr_i)))
            else:
                z_fa_i = normal_CDF_inverse(1 - 1.0/(2 * (fa_i + cr_i)))
            d_prime_i = z_hit_i - z_fa_i
            c_i = -0.5 * (z_hit_i + z_fa_i) * block_i.sd + block_i.mean
            beta_i = math.exp(d_prime_i * (c_i - block_i.mean) / block_i.sd)
            hits_alertsignal_i = len(hit_alertsignal_list)
            misses_alertsignal_i = len(miss_alertsignal_list)
            fa_alertsignal_i = len(fa_alertsignal_list)
            cr_alertsignal_i = len(cr_alertsignal_list)
            hits_alertnoise_i = len(hit_alertnoise_list)
            misses_alertnoise_i = len(miss_alertnoise_list)
            fa_alertnoise_i = len(fa_alertnoise_list)
            cr_alertnoise_i = len(cr_alertnoise_list)
            p_hit_alertsignal_i = float(hits_alertsignal_i) / (hits_alertsignal_i + misses_alertsignal_i) if (hits_alertsignal_i + misses_alertsignal_i > 0) else 0
            p_miss_alertsignal_i = float(misses_alertsignal_i) / (hits_alertsignal_i + misses_alertsignal_i) if (hits_alertsignal_i + misses_alertsignal_i > 0) else 0
            p_fa_alertsignal_i = float(fa_alertsignal_i) / (fa_alertsignal_i + cr_alertsignal_i) if (fa_alertsignal_i + cr_alertsignal_i > 0) else 0
            p_cr_alertsignal_i = float(cr_alertsignal_i) / (fa_alertsignal_i + cr_alertsignal_i) if (fa_alertsignal_i + cr_alertsignal_i > 0) else 0
            p_hit_alertnoise_i = float(hits_alertnoise_i) / (hits_alertnoise_i + misses_alertnoise_i) if (hits_alertnoise_i + misses_alertnoise_i > 0) else 0
            p_miss_alertnoise_i = float(misses_alertnoise_i) / (hits_alertnoise_i + misses_alertnoise_i) if (hits_alertnoise_i + misses_alertnoise_i > 0) else 0
            p_fa_alertnoise_i = float(fa_alertnoise_i) / (fa_alertnoise_i + cr_alertnoise_i) if (fa_alertnoise_i + cr_alertnoise_i > 0) else 0
            p_cr_alertnoise_i = float(cr_alertnoise_i) / (fa_alertnoise_i + cr_alertnoise_i) if (fa_alertnoise_i + cr_alertnoise_i > 0) else 0
            rt_hit_i = sum([float(t['response_time'])/1000 for t in hit_list])/hits_i if hits_i > 0 else 0
            rt_miss_i = sum([float(t['response_time'])/1000 for t in miss_list])/misses_i if misses_i > 0 else 0
            rt_fa_i = sum([float(t['response_time'])/1000 for t in fa_list])/fa_i if fa_i > 0 else 0
            rt_cr_i = sum([float(t['response_time'])/1000 for t in cr_list])/cr_i if cr_i > 0 else 0
            rt_hit_alertsignal_i = sum([float(t['response_time'])/1000 for t in hit_alertsignal_list])/hits_alertsignal_i if hits_alertsignal_i > 0 else 0
            rt_miss_alertsignal_i = sum([float(t['response_time'])/1000 for t in miss_alertsignal_list])/misses_alertsignal_i if misses_alertsignal_i > 0 else 0
            rt_fa_alertsignal_i = sum([float(t['response_time'])/1000 for t in fa_alertsignal_list])/fa_alertsignal_i if fa_alertsignal_i > 0 else 0
            rt_cr_alertsignal_i = sum([float(t['response_time'])/1000 for t in cr_alertsignal_list])/cr_alertsignal_i if cr_alertsignal_i > 0 else 0
            rt_hit_alertnoise_i = sum([float(t['response_time'])/1000 for t in hit_alertnoise_list])/hits_alertnoise_i if hits_alertnoise_i > 0 else 0
            rt_miss_alertnoise_i = sum([float(t['response_time'])/1000 for t in miss_alertnoise_list])/misses_alertnoise_i if misses_alertnoise_i > 0 else 0
            rt_fa_alertnoise_i = sum([float(t['response_time'])/1000 for t in fa_alertnoise_list])/fa_alertnoise_i if fa_alertnoise_i > 0 else 0
            rt_cr_alertnoise_i = sum([float(t['response_time'])/1000 for t in cr_alertnoise_list])/cr_alertnoise_i if cr_alertnoise_i > 0 else 0
            block_result_i = BlockResult(block=block_i, experiment_result=experiment_result_i, cum_score=block['score'], hits=hits_i, misses=misses_i, fa=fa_i, cr=cr_i, p_hit=p_hit_i, p_miss=p_miss_i, p_fa=p_fa_i, p_cr=p_cr_i, d_prime=d_prime_i, beta=beta_i, c=c_i, hits_alertsignal=hits_alertsignal_i, misses_alertsignal=misses_alertsignal_i, fa_alertsignal=fa_alertsignal_i, cr_alertsignal=cr_alertsignal_i, hits_alertnoise=hits_alertnoise_i, misses_alertnoise=misses_alertnoise_i, fa_alertnoise=fa_alertnoise_i, cr_alertnoise=cr_alertnoise_i, p_hit_alertsignal=p_hit_alertsignal_i, p_miss_alertsignal=p_miss_alertsignal_i, p_fa_alertsignal=p_fa_alertsignal_i, p_cr_alertsignal=p_cr_alertsignal_i, p_hit_alertnoise=p_hit_alertnoise_i, p_miss_alertnoise=p_miss_alertnoise_i, p_fa_alertnoise=p_fa_alertnoise_i, p_cr_alertnoise=p_cr_alertnoise_i, rt_hit=rt_hit_i, rt_miss=rt_miss_i, rt_fa=rt_fa_i, rt_cr=rt_cr_i, rt_hit_alertsignal=rt_hit_alertsignal_i, rt_miss_alertsignal=rt_miss_alertsignal_i, rt_fa_alertsignal=rt_fa_alertsignal_i, rt_cr_alertsignal=rt_cr_alertsignal_i, rt_hit_alertnoise=rt_hit_alertnoise_i, rt_miss_alertnoise=rt_miss_alertnoise_i, rt_fa_alertnoise=rt_fa_alertnoise_i, rt_cr_alertnoise=rt_cr_alertnoise_i)
            block_result_i.save()
            for trial in block['trials']:
                time_i = datetime.fromtimestamp(float(trial['time'])/1000)
                trial_result_i = TrialResult(block_result=block_result_i, experiment_result=experiment_result_i, num_trial=trial['trial_num'], time=time_i, response_time=float(trial['response_time'])/1000, signal=trial['signal'], alert=trial['alert'], response=trial['response'], outcome=trial['outcome'], points=trial['points'])
                trial_result_i.save()
        trial_output_header = "id,user id,experiment name,block name,trial num,datetime,response time,signal,alert,response,outcome,points"
        trial_output_text = "\n".join([",".join(str(v) for v in [i+1, experiment_result_i.id, experiment_i.name, t.block_result.block.name, t.num_trial, t.time, t.response_time, t.signal, t.alert, t.response, t.outcome, t.points]) for (i,t) in enumerate(TrialResult.objects.filter(experiment_result=experiment_result_i).order_by('id'))])
        trial_output_file = OutputFile(name="{}_Trials_{}.csv".format(experiment_i.name.replace(" ", "_"), experiment_result_i.id), text=trial_output_text, header=trial_output_header)
        block_output_header = "id,user id,experiment name,block name,cummulative score,hits,misses,fa,cr,p hit,p miss,p fa,p cr,d',beta,c,hits alertsignal,misses alertsignal,fa alertsignal,cr alertsignal,hits alertnoise,misses alertnoise,fa alertnoise,cr alertnoise,p hit alertsignal,p miss alertsignal,p fa alertsignal,p cr alertsignal,p hit alertnoise,p miss alertnoise,p fa alertnoise,p cr alertnoise,rt hit, rt miss,rt fa,rt cr,rt hit alertsignal, rt miss alertsignal,rt fa alertsignal,rt cr alertsignal,rt hit alertnoise, rt miss alertnoise,rt fa alertnoise,rt cr alertnoise"
        block_output_text = "\n".join([",".join(str(v) for v in [i+1, experiment_result_i.id, experiment_i.name, b.block.name, b.cum_score, b.hits, b.misses, b.fa, b.cr, b.p_hit, b.p_miss, b.p_fa, b.p_cr, b.d_prime, b.beta, b.c, b.hits_alertsignal, b.misses_alertsignal, b.fa_alertsignal, b.cr_alertsignal, b.hits_alertnoise, b.misses_alertnoise, b.fa_alertnoise, b.cr_alertnoise, b.p_hit_alertsignal, b.p_miss_alertsignal, b.p_fa_alertsignal, b.p_cr_alertsignal, b.p_hit_alertnoise, b.p_miss_alertnoise, b.p_fa_alertnoise, b.p_cr_alertnoise, b.rt_hit, b.rt_miss, b.rt_fa, b.rt_cr, b.rt_hit_alertsignal, b.rt_miss_alertsignal, b.rt_fa_alertsignal, b.rt_cr_alertsignal, b.rt_hit_alertnoise, b.rt_miss_alertnoise, b.rt_fa_alertnoise, b.rt_cr_alertnoise]) for (i,b) in enumerate(BlockResult.objects.filter(experiment_result=experiment_result_i).order_by('id'))])
        block_output_file = OutputFile(name="{}_Blocks_{}.csv".format(experiment_i.name.replace(" ", "_"), experiment_result_i.id), text=block_output_text, header=block_output_header)
        question_output_header = ','.join(['user id', 'experiment name'] + ['{}_{}'.format(q.questionnaire_result.questionnaire.name, q.question.name) for q in QuestionResult.objects.filter(questionnaire_result__experiment_result=experiment_result_i).order_by('id')])
        question_output_text = ",".join([str(experiment_result_i.id), experiment_i.name] + [q.answer for q in QuestionResult.objects.filter(questionnaire_result__experiment_result=experiment_result_i).order_by('id')])
        question_output_file = OutputFile(name="{}_Questions_{}.csv".format(experiment_i.name.replace(" ", "_"), experiment_result_i.id), text=question_output_text, header=question_output_header)
        trial_output_file.save()
        block_output_file.save()
        question_output_file.save()
        return HttpResponse('Success!')

class OutputView(View):

    def get(self, request, output_id):
        output_file = OutputFile.objects.get(id=output_id)
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename={}'.format(output_file.name)
        writer = csv.writer(response)
        response.write(u'\ufeff'.encode('utf8'))
        writer.writerow(output_file.header.split(","))
        for row in output_file.text.split("\n"):
            writer.writerow(row.split(","))
        return response

#code borrowed from https://www.johndcook.com/blog/python_phi_inverse/
def rational_approximation(t):
 
    # Abramowitz and Stegun formula 26.2.23.
    # The absolute value of the error should be less than 4.5 e-4.
    c = [2.515517, 0.802853, 0.010328]
    d = [1.432788, 0.189269, 0.001308]
    numerator = (c[2]*t + c[1])*t + c[0]
    denominator = ((d[2]*t + d[1])*t + d[0])*t + 1.0
    return t - numerator / denominator
 
#code borrowed from https://www.johndcook.com/blog/python_phi_inverse/
def normal_CDF_inverse(p):
 
    assert p > 0.0 and p < 1
 
    # See article above for explanation of this section.
    if p < 0.5:
        # F^-1(p) = - G^-1(p)
        return -rational_approximation( math.sqrt(-2.0*math.log(p)) )
    else:
        # F^-1(p) = G^-1(1-p)
        return rational_approximation( math.sqrt(-2.0*math.log(1.0-p)) )