# -*- coding: utf-8 -*-
# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript-portal/blob/master/LICENSE ('License').
# This software is distributed 'AS IS' as set forth in the License.

from steelscript.appfw.core.apps.report.models import Report
import steelscript.appfw.core.apps.report.modules.yui3 as yui3

from steelscript.shark.appfw.datasources.shark import SharkTable
#
# Define a Shark Report and Table
#

report = Report.create('Shark', position=3)

report.add_section()

### Shark Time Series

t = SharkTable.create(name='Total Traffic Bytes',
                      duration=1, resolution='1sec', aggregated=False)

t.add_column('time', label='Time', iskey=True,
             extractor='sample_time', datatype='time')
t.add_column('generic_bytes', label='Bytes', iskey=False,
             extractor='generic.bytes', operation='sum')

report.add_widget(yui3.TimeSeriesWidget, t, 'Overall Bandwidth (Bytes)',
                  width=12)

### Table for Shark
t = SharkTable.create(name='Packet Traffic', duration=1, aggregated=False)

t.add_column('ip_src', label='Source IP', iskey=True, extractor='ip.src',
             datatype='string')
t.add_column('ip_dst', label='Dest IP', iskey=True, extractor='ip.dst',
             datatype='string')
t.add_column('generic_bytes', label='Bytes', iskey=False,
             extractor='generic.bytes', operation='sum', units='B',
             issortcol=True)
t.add_column('generic_packets', label='Packets', iskey=False,
             extractor='generic.packets', operation='sum')

report.add_widget(yui3.TableWidget, t, 'Packets', width=12)

### Microbursts Graph for Shark
t = SharkTable.create(name='MicroburstsTime', duration=1, aggregated=False)

t.add_column('time', label='Time (ns)', iskey=True,
             extractor='sample_time', datatype='time')

t.add_column('max_microburst_1ms_bytes', label='uBurst 1ms',
             extractor='generic.max_microburst_1ms.bytes',
             operation='max', units='B')

t.add_column('max_microburst_10ms_bytes', label='uBurst 10ms',
             extractor='generic.max_microburst_10ms.bytes',
             operation='max', units='B')

t.add_column('max_microburst_100ms_bytes', label='uburst 100ms',
             extractor='generic.max_microburst_100ms.bytes',
             operation='max', units='B')

report.add_widget(yui3.TimeSeriesWidget, t, 'Microbursts Summary Bytes', width=6)

### Microbursts Table for Shark
t = SharkTable.create(name='MicroburstsTable', duration=1, aggregated=False)

t.add_column('max_microburst_1ms_bytes', label='uBurst 1ms',
             extractor='generic.max_microburst_1ms.bytes',
             operation='max', units='B')

t.add_column('max_microburst_10ms_bytes', label='uBurst 10ms',
             extractor='generic.max_microburst_10ms.bytes',
             operation='max', units='B')

t.add_column('max_microburst_100ms_bytes', label='uburst 100ms',
             extractor='generic.max_microburst_100ms.bytes',
             operation='max', units='B')

report.add_widget(yui3.TableWidget, t, 'Microbursts Bytes Summary', width=6)

### Table and Widget 2

t = SharkTable.create(name='Traffic by TCP/UDP', duration=1, aggregated=False)

t.add_column('time', label='Time (ns)', iskey=True,
             extractor='sample_time', datatype='time')
t.add_column('udp_bytes', label='UDP Bytes', iskey=False,
             extractor='udp.bytes', operation='sum', default_value=0)
t.add_column('tcp_bytes', label='TCP Bytes', iskey=False,
             extractor='tcp.bytes', operation='sum', default_value=0)

report.add_widget(yui3.TimeSeriesWidget, t, 'Traffic By Type (Bytes)', width=12)
