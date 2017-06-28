from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin
from .models import ExperimentCondition, Questionnaire, Question, Choice
# Register your models here.
class ChoiceInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fields = ('name', 'text')
    inlines = [ChoiceInline]

class ExperimentConditionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None ,{'fields':['name', 'num_trials']}),
        ('System Parameters' ,{'fields':['p_signal','d_user',('d_alert','beta_alert'),('mean','sd')]}),
        ('Payoff Matrix' ,{'fields':[('v_hit_s','v_hit_n','v_fa_s','v_fa_n','v_miss_s','v_miss_n','v_cr_s','v_cr_n')], 'classes':['matrix']}),
        ('Display Parameters' ,{'fields':['stimulus',('alert_signal_color','alert_noise_color'),('stimulus_duration','stimulus_delay'),('alert_duration','alert_delay'),('trial_duration','trial_delay'),('display_last_points','display_total_points','display_trial_num')]}),
    ]
    class Media:
        css = {
            "all": ("experiment/experiment_condition_admin.css",)
        }
        js = ("experiment/experiment_condition_admin.js",)

class ExperimentAdminSite(admin.AdminSite):
    site_header = 'Experiment Administration'
    site_title = 'Responsibility Experiment Administration'

admin_site = ExperimentAdminSite()
admin_site.register(ExperimentCondition, ExperimentConditionAdmin)
admin_site.register(Questionnaire)
admin_site.register(Question, QuestionAdmin)
