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
                c = (math.log(content.beta_alert) / content.d_alert)
                stimuli = [round(random.gauss(user_mean_s, content.sd), content.num_dec_places) if s else round(random.gauss(user_mean_n, content.sd), content.num_dec_places) for (i,s) in enumerate(signals)]
                alerts = [a > content.mean + c for a in alert_distribution]
                modules.append({"obj":json.loads(serializers.serialize("json", [content])),"signals":signals,"alerts":alerts,"stimuli":stimuli})
            elif type(content) is Questionnaire:
                questions = [[q.text, q.choices.split(","), q.id] for q in content.questions.all()]
                modules.append({"obj":json.loads(serializers.serialize("json", [content])), "questions":questions})
            elif type(content) is Text:
                modules.append(json.loads(serializers.serialize("json", [content])))
        context['modules'] = json.dumps(modules)
        return context

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
                z_hit_i = normal_CDF_inverse(0.001)
            else:
                z_hit_i = normal_CDF_inverse(0.999)
            if 0 < p_fa_i < 1:
                z_fa_i = normal_CDF_inverse(p_fa_i)
            elif p_fa_i < 1:
                z_fa_i = normal_CDF_inverse(0.001)
            else:
                z_fa_i = normal_CDF_inverse(0.999)
            d_prime_i = z_hit_i - z_fa_i
            c_i = -0.5 * (z_hit_i + z_fa_i)
            beta_i = math.exp(d_prime_i * c_i)
            hits_alertcorrect_i = sum([1 if t['outcome'] == 'hit_s' else 0 for t in block['trials']])
            misses_alertcorrect_i = sum([1 if t['outcome'] == 'miss_s' else 0 for t in block['trials']])
            fa_alertcorrect_i = sum([1 if t['outcome'] == 'fa_n' else 0 for t in block['trials']])
            cr_alertcorrect_i = sum([1 if t['outcome'] == 'cr_n' else 0 for t in block['trials']])
            hits_alertincorrect_i = sum([1 if t['outcome'] == 'hit_n' else 0 for t in block['trials']])
            misses_alertincorrect_i = sum([1 if t['outcome'] == 'miss_n' else 0 for t in block['trials']])
            fa_alertincorrect_i = sum([1 if t['outcome'] == 'fa_s' else 0 for t in block['trials']])
            cr_alertincorrect_i = sum([1 if t['outcome'] == 'cr_s' else 0 for t in block['trials']])
            p_hit_alertcorrect_i = float(hits_alertcorrect_i) / (hits_alertcorrect_i + misses_alertcorrect_i) if (hits_alertcorrect_i + misses_alertcorrect_i > 0) else 0
            p_fa_alertcorrect_i = float(fa_alertcorrect_i) / (fa_alertcorrect_i + cr_alertcorrect_i) if (fa_alertcorrect_i + cr_alertcorrect_i > 0) else 0
            p_hit_alertincorrect_i = float(hits_alertincorrect_i) / (hits_alertincorrect_i + misses_alertincorrect_i) if (hits_alertincorrect_i + misses_alertincorrect_i > 0) else 0
            p_fa_alertincorrect_i = float(fa_alertincorrect_i) / (fa_alertincorrect_i + cr_alertincorrect_i) if (fa_alertincorrect_i + cr_alertincorrect_i > 0) else 0
            rt_hit_i = sum([float(t['response_time'])/1000 for t in hit_list])/hits_i if hits_i > 0 else 0
            rt_miss_i = sum([float(t['response_time'])/1000 for t in miss_list])/misses_i if misses_i > 0 else 0
            rt_fa_i = sum([float(t['response_time'])/1000 for t in fa_list])/fa_i if fa_i > 0 else 0
            rt_cr_i = sum([float(t['response_time'])/1000 for t in cr_list])/cr_i if cr_i > 0 else 0
            block_result_i = BlockResult(block=block_i, experiment_result=experiment_result_i, cum_score=block['score'], hits=hits_i, misses=misses_i, fa=fa_i, cr=cr_i, p_hit=p_hit_i, p_miss=p_miss_i, p_fa=p_fa_i, p_cr=p_cr_i, d_prime=d_prime_i, beta=beta_i, c=c_i, hits_alertcorrect=hits_alertcorrect_i, misses_alertcorrect=misses_alertcorrect_i, fa_alertcorrect=fa_alertcorrect_i, cr_alertcorrect=cr_alertcorrect_i, hits_alertincorrect=hits_alertincorrect_i, misses_alertincorrect=misses_alertincorrect_i, fa_alertincorrect=fa_alertincorrect_i, cr_alertincorrect=cr_alertincorrect_i, p_hit_alertcorrect=p_hit_alertcorrect_i, p_fa_alertcorrect=p_fa_alertcorrect_i, p_hit_alertincorrect=p_hit_alertincorrect_i, p_fa_alertincorrect=p_fa_alertincorrect_i, rt_hit=rt_hit_i, rt_miss=rt_miss_i, rt_fa=rt_fa_i, rt_cr=rt_cr_i)
            block_result_i.save()
            for trial in block['trials']:
                time_i = datetime.fromtimestamp(float(trial['time'])/1000)
                trial_result_i = TrialResult(block_result=block_result_i, experiment_result=experiment_result_i, num_trial=trial['trial_num'], time=time_i, response_time=float(trial['response_time'])/1000, signal=trial['signal'], alert=trial['alert'], response=trial['response'], outcome=trial['outcome'], points=trial['points'])
                trial_result_i.save()
        trial_output_header = "id,experiment name,block name,trial num,datetime,response time,signal,alert,response,outcome,points"
        trial_output_text = ";".join([",".join(str(v) for v in [i, experiment_i.name, t.block_result.block.name, t.num_trial, t.time, t.response_time, t.signal, t.alert, t.response, t.outcome, t.points]) for (i,t) in enumerate(TrialResult.objects.filter(experiment_result=experiment_result_i))])
        trial_output_file = OutputFile(name="{}_Trials_{}.csv".format(experiment_i.name.replace(" ", "_"), experiment_result_i.id), text=trial_output_text, header=trial_output_header)
        block_output_header = "id,experiment name,block name,cummulative score,hits,misses,fa,cr,p hit,p miss,p fa,p cr,d',beta,c,hits alertcorrect,misses alertcorrect,fa alertcorrect,cr alertcorrect,hits alertincorrect,misses alertincorrect,fa alertincorrect,cr alertincorrect,p hit alertcorrect,p fa alertcorrect,p hit alertincorrect,p fa alertincorrect,rt hit, rt miss,rt fa,rt cr"
        block_output_text = ";".join([",".join(str(v) for v in [i, experiment_i.name, b.block.name, b.cum_score, b.hits, b.misses, b.fa, b.cr, b.p_hit, b.p_miss, b.p_fa, b.p_cr, b.d_prime, b.beta, b.c, b.hits_alertcorrect, b.misses_alertcorrect, b.fa_alertcorrect, b.cr_alertcorrect, b.hits_alertincorrect, b.misses_alertincorrect, b.fa_alertincorrect, b.cr_alertincorrect, b.p_hit_alertcorrect, b.p_fa_alertcorrect, b.p_hit_alertincorrect, b.p_fa_alertincorrect, b.rt_hit, b.rt_miss, b.rt_fa, b.rt_cr]) for (i,b) in enumerate(BlockResult.objects.filter(experiment_result=experiment_result_i))])
        block_output_file = OutputFile(name="{}_Blocks_{}.csv".format(experiment_i.name.replace(" ", "_"), experiment_result_i.id), text=block_output_text, header=block_output_header)
        question_output_header = "id,experiment name,questionnaire name,question name,answer"
        question_output_text = ";".join([",".join(str(v) for v in [i, experiment_i.name, q.questionnaire_result.questionnaire.name, q.question.name, q.answer]) for (i,q) in enumerate(QuestionResult.objects.filter(questionnaire_result__experiment_result=experiment_result_i))])
        question_output_file = OutputFile(name="{}_Questions_{}.csv".format(experiment_i.name.replace(" ", "_"), experiment_result_i.id), text=question_output_text, header=question_output_header)
        trial_output_file.save()
        block_output_file.save()
        question_output_file.save()
        return HttpResponse('Success!')

class OutputView(View):

    def get(self, request, output_id):
        output_file = OutputFile.objects.get(id=output_id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}'.format(output_file.name)
        writer = csv.writer(response)
        # Write headers to CSV file
        writer.writerow(output_file.header.split(","))
        # Write data to CSV file
        for row in output_file.text.split(";"):
            writer.writerow(row.split(","))
        # Return CSV file to browser as download
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