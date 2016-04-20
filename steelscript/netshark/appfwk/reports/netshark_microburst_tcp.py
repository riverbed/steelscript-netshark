# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import steelscript.appfwk.apps.report.modules.yui3 as yui3
from steelscript.appfwk.apps.report.models import Report
from steelscript.netshark.appfwk.datasources.netshark import \
    NetSharkTable
from steelscript.appfwk.apps.datasource.modules.analysis import \
    FocusedAnalysisTable

#
# Define a NetShark Report and Table
#
report = Report.create('NetShark Microburst and TCP Errors', position=10)
report.add_section()

# Summary Microbursts Graph for NetShark
t = NetSharkTable.create(name='MicroburstsTime', duration=1,
                         resolution='1sec', aggregated=False)

t.add_column('time', label='Time', iskey=True,
             extractor='sample_time', datatype='time')

t.add_column('max_microburst_1ms_bits', label='uBurst 1ms',
             extractor='generic.max_microburst_1ms.bits',
             operation='max', units='B')

t.add_column('max_microburst_10ms_bits', label='uBurst 10ms',
             extractor='generic.max_microburst_10ms.bits',
             operation='max', units='B')

t.add_column('max_microburst_100ms_bits', label='uBurst 100ms',
             extractor='generic.max_microburst_100ms.bits',
             operation='max', units='B')

report.add_widget(yui3.TimeSeriesWidget, t,
                  'Microburst Timeseries (1s resolution)', width=6)
report.add_widget(yui3.TableWidget, t,
                  'Microburst Bits Summary', width=6)


# Detailed Microburst Template Table
# This uses finer grained microburst extractors
z = NetSharkTable.create(name='MicroburstsFocused', aggregated=False)

z.add_column('time', label='Time', iskey=True,
             extractor='sample_time', datatype='time')

z.add_column('max_microburst_10us_bits', label='uBurst 10us',
             extractor='generic.max_microburst_10us.bits',
             operation='max', units='B')

z.add_column('max_microburst_100us_bits', label='uBurst 100us',
             extractor='generic.max_microburst_100us.bits',
             operation='max', units='B')

z.add_column('max_microburst_1ms_bits', label='uBurst 1ms',
             extractor='generic.max_microburst_1ms.bits',
             operation='max', units='B')

# Local Max Microburst detail
a = FocusedAnalysisTable.create(name='max-focused-table-microburst',
                                max=True,
                                zoom_duration='1s',
                                zoom_resolution='1ms',
                                tables={'source': t},
                                related_tables={'template': z})
report.add_widget(yui3.TimeSeriesWidget, a,
                  'Max Microburst Timeseries (1ms resolution)', width=6)
report.add_widget(yui3.TableWidget, a,
                  'Max Microburst Bits Summary', width=6)

# TCP Errors Template Table
tcp = NetSharkTable.create(name='TCPErrors', aggregated=True)

tcp.add_column('error_type', label='TCP Error Type', iskey=True,
               extractor='tcp.error_type', datatype='string')
tcp.add_column('errors', label='TCP Errors', sortdesc=True,
               extractor='tcp.errors', datatype='integer',
               operation='sum', default_value=0)

# Local Min Microburst detail
a = FocusedAnalysisTable.create(name='max-focused-table-tcp',
                                max=True,
                                zoom_duration='1s',
                                zoom_resolution='1ms',
                                tables={'source': t},
                                related_tables={'template': tcp})
report.add_widget(yui3.BarWidget, a,
                  'TCP Errors @ Peak 1s Microburst', width=6, height=400)
report.add_widget(yui3.TableWidget, a,
                  'TCP Errors Table @ Peak 1s Microburst', width=6, height=400)
