# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from django.contrib import admin
from steelscript.netshark.appfwk.models import (PcapFilter, SplitThresh,
                                                JobsStartTime)


class PcapFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'filter')

admin.site.register(PcapFilter, PcapFilterAdmin)


class SplitThreshAdmin(admin.ModelAdmin):
    list_display = ('min_pkt_num',)

admin.site.register(SplitThresh, SplitThreshAdmin)


class JobsStartTimeAdmin(admin.ModelAdmin):
    list_display = ('jobs_start_time')

admin.site.register(JobsStartTime, JobsStartTimeAdmin)
