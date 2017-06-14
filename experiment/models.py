from django.db import models

class ExperimentCondition(models.Model):
    name = models.CharField('Name of Experiment Condition', max_length=200)
    num_trials = models.IntegerField('# Trials')
    p_signal = models.FloatField('Probability of Signal')
    d_user = models.FloatField("User Sensitivity (d')")
    d_alert = models.FloatField("Alert Sensitivity (d')")
    beta_alert = models.FloatField("Alert Criterion (beta)")
    mean = models.FloatField('Mean')
    sd = models.FloatField('Standard Deviation')
    

# Create your models here.
