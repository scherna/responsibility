from django.db import models
from datetime import timedelta
from colorfield.fields import ColorField
from sortedm2m.fields import SortedManyToManyField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields

class Experiment(models.Model):
    name = models.CharField('Name of Experiment', max_length=200)
    modules = SortedManyToManyField('Module')

    def __str__(self):
        return self.name 

class Module(models.Model):
    name = models.CharField('Name of Module', max_length=200)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.name 

class TextBlock(models.Model):
    name = models.CharField('Name of Text Block', max_length=200)
    text = models.TextField()
    module = fields.GenericRelation(Module)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            super(TextBlock, self).save(*args, **kwargs)
            m = Module(content_object=self, name=self.name)
            m.save()
        super(TextBlock, self).save(*args, **kwargs)

class ExperimentCondition(models.Model):
    name = models.CharField('Name of Experiment Condition', max_length=200)
    num_trials = models.IntegerField('# Trials', default=5)
    p_signal = models.FloatField('Probability of Signal', default=0.5)
    v_hit_s = models.FloatField(default=1.0)
    v_hit_n = models.FloatField(default=1.5)
    v_miss_s = models.FloatField(default=-1.5)
    v_miss_n = models.FloatField(default=-1.0)
    v_cr_s = models.FloatField(default=0.0)
    v_cr_n = models.FloatField(default=0.0)
    v_fa_s = models.FloatField(default=0.0)
    v_fa_n = models.FloatField(default=0.0)
    d_user = models.FloatField("User Sensitivity (d')", default=1.0)
    d_alert = models.FloatField("Alert Sensitivity (d')", default=1.0)
    beta_alert = models.FloatField("Alert Criterion (beta)", default=0.5)
    mean = models.FloatField('Mean (between signal/noise distributions)', default=5.0)
    sd = models.FloatField('Standard Deviation', default=0.5)
    stimulus_choices = (('num', 'Numbers'), ('rect', 'Rectangles'))
    stimulus = models.CharField('Choice of Stimulus', max_length=200, choices=stimulus_choices, default='num')
    num_dec_places = models.IntegerField('# Decimal Places to Use for Stimulus', default=1)
    alert_signal_color = ColorField('Alert Color for Signal', default="#f44141")
    alert_noise_color = ColorField('Alert Color for Noise', default="#4ef442")
    stimulus_duration = models.FloatField('Stimulus Duration (seconds)', default=5.0)
    stimulus_delay = models.FloatField('Stimulus Delay (seconds)', default=0.0)
    alert_duration = models.FloatField('Alert Duration (seconds)', default=5.0)
    alert_delay = models.FloatField('Alert Delay (seconds)', default=0.0)
    trial_duration = models.FloatField('Total Trial Duration (seconds)', default=5.0)
    trial_delay = models.FloatField('Delay Between Trials (seconds)', default=3.0)
    display_last_points = models.BooleanField('Display Points from Last Trial', default=True)
    display_total_points = models.BooleanField('Display Cumulative Points', default=True)
    display_trial_num = models.BooleanField('Display Number of Trial in Block', default=True)
    module = fields.GenericRelation(Module)

    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        if not self.pk:
            super(ExperimentCondition, self).save(*args, **kwargs)
            m = Module(content_object=self, name=self.name)
            m.save()
        super(ExperimentCondition, self).save(*args, **kwargs)

class Questionnaire(models.Model):
    name = models.CharField('Name of Questionnaire', max_length=200)
    questions = SortedManyToManyField('Question')
    module = fields.GenericRelation(Module)

    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        if not self.pk:
            super(Questionnaire, self).save(*args, **kwargs)
            m = Module(content_object=self, name=self.name)
            m.save()
        super(Questionnaire, self).save(*args, **kwargs)

class Question(models.Model):
    name = models.CharField('Name of Question', max_length=200)
    text = models.CharField('Question Text', max_length=200)
    choices = models.CharField('Answer Choices (separated by commas) / leave blank for open answer', max_length=200, blank=True)

    def __str__(self):
        return self.name 

class TrialResult(models.Model):
    block_result = models.ForeignKey('BlockResult')
    num_trial = models.IntegerField('# of Trial in Block')
    time = models.DateTimeField('DateTime at End of Trial')
    response_time = models.FloatField('Response Time (in seconds)')
    signal = models.BooleanField('Stimulus Signal/Noise')
    alert = models.BooleanField('Alert Signal/Noise')
    response = models.BooleanField('User Response Signal/Noise')
    outcome = models.CharField('Outcome (Hit/Miss/CR/FA)', max_length=200)

    def __str__(self):
        return str(self.id)

class BlockResult(models.Model):
    experiment_condition = models.ForeignKey('ExperimentCondition')
    experiment_result = models.ForeignKey('ExperimentResult')
    score = models.FloatField('Cumulative Score')
    hit_alert = models.IntegerField('# Hits With Correct Alert')
    miss_alert = models.IntegerField('# Misses With Correct Alert')
    fa_alert = models.IntegerField('# FA With Correct Alert')
    cr_alert = models.IntegerField('# CR With Correct Alert')
    hit_no_alert = models.IntegerField('# Hits With Incorrect Alert')
    miss_no_alert = models.IntegerField('# Misses With Incorrect Alert')
    fa_no_alert = models.IntegerField('# FA With Incorrect Alert')
    cr_no_alert = models.IntegerField('# CR With Incorrect Alert')
    p_hit_alert = models.FloatField('Proportion of Hits (out of all signals) With Correct Alert')
    p_fa_alert = models.FloatField('Proportion of FA (out of all noise) With Correct Alert')
    p_hit_no_alert = models.FloatField('Proportion of Hits (out of all signals) With Incorrect Alert')
    p_fa_no_alert = models.FloatField('Proportion of FA (out of all noise) With Incorrect Alert')
    rt_hit = models.FloatField('Average Response Time for Hit')
    rt_miss = models.FloatField('Average Response Time for Miss')

    def __str__(self):
        return str(self.id)

class QuestionResult(models.Model):
    question = models.ForeignKey('Question')
    questionnaire_result = models.ForeignKey('QuestionnaireResult')
    answer = models.CharField('User Response', max_length=200)

    def __str__(self):
        return str(self.id)

class QuestionnaireResult(models.Model):
    questionnaire = models.ForeignKey('Questionnaire')
    experiment_result = models.ForeignKey('ExperimentResult')

    def __str__(self):
        return str(self.id)

class ExperimentResult(models.Model):
    experiment = models.ForeignKey('Experiment')

    def __str__(self):
        return str(self.id)
