# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import steelscript.appfwk.apps.report.modules.c3 as c3
from steelscript.appfwk.apps.report.models import Report

from steelscript.netshark.appfwk.datasources.netshark_msa import \
    MSATable

#
# Run a latency report against a MSA datasource
#

report = Report.create('NetShark MSA Segment Delay Report', position=10)

report.add_section()

# NetShark Time Series report with min/avg/max
t = MSATable.create(name='MultiSegment Table', resolution='1sec',
                    aggregated=False)
t.add_column('time', label='Time', iskey=True,
             extractor='sample_time', datatype='time')
t.add_column('msa_delay_min', label='Segment Delay (Min)', iskey=False,
             extractor='multi_segment.delay', operation='min')
t.add_column('msa_delay', label='Segment Delay (Avg)', iskey=False,
             extractor='multi_segment.delay', operation='avg')
t.add_column('msa_delay_max', label='Segment Delay (Max)', iskey=False,
             extractor='multi_segment.delay', operation='max')

report.add_widget(c3.TimeSeriesWidget, t, 'MSA Results', width=12)
