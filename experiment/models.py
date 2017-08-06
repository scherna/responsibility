from django.db import models
from datetime import timedelta
from colorfield.fields import ColorField
from sortedm2m.fields import SortedManyToManyField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields
from django.urls import reverse
from django.utils.html import format_html

class Experiment(models.Model):
    name = models.CharField('Name of Experiment', max_length=200)
    modules = SortedManyToManyField('Module')

    def __str__(self):
        return self.name 

class Module(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.content_object.name 

class Text(models.Model):
    name = models.CharField('Name of Text', max_length=200)
    text = models.TextField()
    module = fields.GenericRelation(Module)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            super(Text, self).save(*args, **kwargs)
            m = Module(content_object=self)
            m.save()
        super(Text, self).save(*args, **kwargs)

class Block(models.Model):
    name = models.CharField('Name of Experiment Block', max_length=200)
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
    display_outcome = models.BooleanField('Display Points from Last Trial', default=True)
    display_total_points = models.BooleanField('Display Cumulative Points', default=True)
    display_trial_num = models.BooleanField('Display Number of Trial in Block', default=True)
    module = fields.GenericRelation(Module)

    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        if not self.pk:
            super(Block, self).save(*args, **kwargs)
            m = Module(content_object=self)
            m.save()
        super(Block, self).save(*args, **kwargs)

class Example(models.Model):
    name = models.CharField('Name of Example', max_length=200)
    num_trial = models.IntegerField('Trial Number')
    alert_color = ColorField('Color of Alert (green default is #4ef442)', default="#f44141")
    points = models.FloatField('Points from Last Trial')
    score = models.FloatField('Score')
    outcome = models.CharField('Outcome from Last Trial', max_length=200)
    stimulus_choices = (('num', 'Numbers'), ('rect', 'Rectangles'))
    stimulus = models.CharField('Choice of Stimulus', max_length=200, choices=stimulus_choices, default='num')
    val = models.FloatField('Value of Stimulus (rectangle value is percent of box height)')
    module = fields.GenericRelation(Module)

    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        if not self.pk:
            super(Example, self).save(*args, **kwargs)
            m = Module(content_object=self)
            m.save()
        super(Example, self).save(*args, **kwargs)

class Questionnaire(models.Model):
    name = models.CharField('Name of Questionnaire', max_length=200)
    questions = SortedManyToManyField('Question')
    module = fields.GenericRelation(Module)

    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        if not self.pk:
            super(Questionnaire, self).save(*args, **kwargs)
            m = Module(content_object=self)
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
    experiment_result = models.ForeignKey('ExperimentResult')
    num_trial = models.IntegerField('# of Trial in Block')
    time = models.DateTimeField('DateTime at End of Trial')
    response_time = models.FloatField('Response Time (in seconds)')
    signal = models.BooleanField('Stimulus Signal/Noise')
    alert = models.BooleanField('Alert Signal/Noise')
    response = models.CharField('User Response Signal/Noise', max_length=200)
    outcome = models.CharField('Outcome (Hit/Miss/CR/FA)', max_length=200)
    points = models.FloatField('Points from Trial')

    def __str__(self):
        return str(self.id)

class BlockResult(models.Model):
    block = models.ForeignKey('Block')
    experiment_result = models.ForeignKey('ExperimentResult')
    cum_score = models.FloatField('Cumulative Score')
    hits = models.IntegerField('# Hits')
    misses = models.IntegerField('# Misses')
    fa = models.IntegerField('# FA')
    cr = models.IntegerField('# CR')
    p_hit = models.FloatField('Proportion of Hits (out of all signals)')
    p_miss = models.FloatField('Proportion of Misses (out of all signals)')
    p_fa = models.FloatField('Proportion of FA (out of all noise)')
    p_cr = models.FloatField('Proportion of CR (out of all noise)')
    d_prime = models.FloatField("Calculated User d'")
    beta = models.FloatField("Calculated User beta")
    c = models.FloatField("Calculated User c'")
    hits_alertsignal = models.IntegerField('# Hits With Alert=Signal')
    misses_alertsignal = models.IntegerField('# Misses With Alert=Signal')
    fa_alertsignal = models.IntegerField('# FA With Alert=Signal')
    cr_alertsignal = models.IntegerField('# CR With Alert=Signal')
    hits_alertnoise = models.IntegerField('# Hits With Alert=Noise')
    misses_alertnoise = models.IntegerField('# Misses With Alert=Noise')
    fa_alertnoise = models.IntegerField('# FA With Alert=Noise')
    cr_alertnoise = models.IntegerField('# CR With Alert=Noise')
    p_hit_alertsignal = models.FloatField('Proportion of Hits (out of all signals) With Alert=Signal')
    p_miss_alertsignal = models.FloatField('Proportion of Misses (out of all signals) With Alert=Signal')
    p_fa_alertsignal = models.FloatField('Proportion of FA (out of all noise) With Alert=Signal')
    p_cr_alertsignal = models.FloatField('Proportion of CR (out of all noise) With Alert=Signal')
    p_hit_alertnoise = models.FloatField('Proportion of Hits (out of all signals) With Alert=Noise')
    p_miss_alertnoise = models.FloatField('Proportion of Misses (out of all signals) With Alert=Noise')
    p_fa_alertnoise = models.FloatField('Proportion of FA (out of all noise) With Alert=Noise')
    p_cr_alertnoise = models.FloatField('Proportion of CR (out of all noise) With Alert=Noise')
    rt_hit = models.FloatField('Average Response Time for Hit')
    rt_miss = models.FloatField('Average Response Time for Miss')
    rt_fa = models.FloatField('Average Response Time for FA')
    rt_cr = models.FloatField('Average Response Time for CR')
    rt_hit_alertsignal = models.FloatField('Average Response Time for Hit With Alert=Signal')
    rt_miss_alertsignal = models.FloatField('Average Response Time for Miss With Alert=Signal')
    rt_fa_alertsignal = models.FloatField('Average Response Time for FA With Alert=Signal')
    rt_cr_alertsignal = models.FloatField('Average Response Time for CR With Alert=Signal')
    rt_hit_alertnoise = models.FloatField('Average Response Time for Hit With Alert=Noise')
    rt_miss_alertnoise = models.FloatField('Average Response Time for Miss With Alert=Noise')
    rt_fa_alertnoise = models.FloatField('Average Response Time for FA With Alert=Noise')
    rt_cr_alertnoise = models.FloatField('Average Response Time for CR With Alert=Noise')

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

class OutputFile(models.Model):
    name = models.CharField('Name of File', max_length=200)
    header = models.CharField('CSV Headers', max_length=400)
    text = models.CharField('CSV Text', max_length=20000)

    def __str__(self):
        return self.name

    def download_url(self):
        return format_html('<a href="{}">Download</a>', reverse('experiment:output', args=[self.id]))