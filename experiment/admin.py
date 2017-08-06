from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin
from .models import *
import zipfile
from io import BytesIO
from django.http import HttpResponse

# Register your models here.
class QuestionAdmin(admin.ModelAdmin):
    fields = ('name', 'text', 'choices')

class BlockAdmin(admin.ModelAdmin):
    fieldsets = [
        (None ,{'fields':['name', 'num_trials']}),
        ('System Parameters' ,{'fields':['p_signal','d_user',('d_alert','beta_alert'),('mean','sd')]}),
        ('Payoff Matrix' ,{'fields':[('v_hit_s','v_hit_n','v_fa_s','v_fa_n','v_miss_s','v_miss_n','v_cr_s','v_cr_n')], 'classes':['matrix']}),
        (None,{'fields':['v_na']}),
        ('Display Parameters' ,{'fields':[('stimulus', 'num_dec_places'),('alert_signal_color','alert_noise_color'),('stimulus_duration','stimulus_delay'),('alert_duration','alert_delay'),('trial_duration','trial_delay'),('display_last_points', 'display_outcome', 'display_total_points','display_trial_num')]}),
    ]
    class Media:
        css = {
            "all": ("experiment/block_admin.css",)
        }
        js = ("experiment/block_admin.js",)

class OutputFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'download_url')
    actions = ['download_files']

    def download_files(self, request, queryset):
        s = BytesIO()
        zf = zipfile.ZipFile(s, "w")
        for output_file in queryset:
            zf.writestr(output_file.name, output_file.header + "\n" + output_file.text)
        zf.close()
        response = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename={}'.format('results.zip')
        return response

class ExperimentAdminSite(admin.AdminSite):
    site_header = 'Experiment Administration'
    site_title = 'Responsibility Experiment Administration'

admin_site = ExperimentAdminSite()
admin_site.register(Block, BlockAdmin)
admin_site.register(Questionnaire)
admin_site.register(Text)
admin_site.register(Example)
admin_site.register(Experiment)
admin_site.register(Question, QuestionAdmin)
admin_site.register(OutputFile, OutputFileAdmin)
# admin_site.register(QuestionResult)
# admin_site.register(QuestionnaireResult)
# admin_site.register(TrialResult)
# admin_site.register(BlockResult)
# admin_site.register(ExperimentResult)
