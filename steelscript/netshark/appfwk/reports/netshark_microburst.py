# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.yui3 as yui3

from steelscript.netshark.appfwk.datasources.netshark import NetSharkTable

#
# Define a NetShark Report and Table
#
report = Report.create('NetShark Microburst Summary', position=10)
report.add_section()

# Microbursts Graph for NetShark
t = NetSharkTable.create(name='MicroburstsTime', duration=1, aggregated=False)

t.add_column('time', label='Time (ns)', iskey=True,
             extractor='sample_time', datatype='time')

t.add_column('max_microburst_1ms_bits', label='uBurst 1ms',
             extractor='generic.max_microburst_1ms.bits',
             operation='max', units='B')

t.add_column('max_microburst_10ms_bits', label='uBurst 10ms',
             extractor='generic.max_microburst_10ms.bits',
             operation='max', units='B')

t.add_column('max_microburst_100ms_bits', label='uburst 100ms',
             extractor='generic.max_microburst_100ms.bits',
             operation='max', units='B')

report.add_widget(yui3.TimeSeriesWidget, t,
                  'Microbursts Summary Bits', width=6)
report.add_widget(yui3.TableWidget, t,
                  'Microbursts Bits Summary', width=6)
