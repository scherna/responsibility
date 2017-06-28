from django.db import models
from datetime import timedelta
from colorfield.fields import ColorField
from sortedm2m.fields import SortedManyToManyField

class ExperimentCondition(models.Model):
    def __str__(self):
        return self.name 

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
    mean = models.FloatField('Mean', default=5.0)
    sd = models.FloatField('Standard Deviation', default=0.5)
    stimulus_choices = (('num', 'Numbers'), ('rect', 'Rectangles'))
    stimulus = models.CharField('Choice of Stimulus', max_length=200, choices=stimulus_choices, default='num')
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

class Questionnaire(models.Model):
    def __str__(self):
        return self.name 

    name = models.CharField('Name of Questionnaire', max_length=200)
    questions = SortedManyToManyField('Question')

class Question(models.Model):
    def __str__(self):
        return self.name 
        
    name = models.CharField('Name of Question', max_length=200)
    text = models.CharField('Question Text', max_length=200)
    answer = models.CharField('User Response', max_length=200)

class Choice(models.Model):
    text = models.CharField('Choice Text', max_length=200)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)

    class Meta(object):
        ordering = ('order',)