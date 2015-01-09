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

report = Report.create('NetShark', position=10)

report.add_section()

# NetShark Time Series
t = NetSharkTable.create(name='Total Traffic Bits',
                         duration=1, resolution='1sec', aggregated=False)

t.add_column('time', label='Time', iskey=True,
             extractor='sample_time', datatype='time')
t.add_column('generic_bits', label='Bits', iskey=False,
             extractor='generic.bits', operation='sum')

report.add_widget(yui3.TimeSeriesWidget, t, 'Overall Bandwidth (Bits)',
                  width=12)

# Table for NetShark
t = NetSharkTable.create(name='Packet Traffic', duration=1, aggregated=True,
                         rows=100)

t.add_column('ip_src', label='Source IP', iskey=True, extractor='ip.src',
             datatype='string')
t.add_column('ip_dst', label='Dest IP', iskey=True, extractor='ip.dst',
             datatype='string')
t.add_column('generic_bits', label='Bits', iskey=False,
             extractor='generic.bits', operation='sum', units='B')
t.add_column('generic_packets', label='Packets', iskey=False, sortdesc=True,
             extractor='generic.packets', operation='sum')

report.add_widget(yui3.TableWidget, t, 'Top 100 Conversations', width=12)

# TCP/UDP Traffic tables
t = NetSharkTable.create(name='Traffic by TCP/UDP', duration=1,
                         aggregated=False)

t.add_column('time', label='Time (ns)', iskey=True,
             extractor='sample_time', datatype='time')
t.add_column('udp_bits', label='UDP Bits', iskey=False,
             extractor='udp.bits', operation='sum', default_value=0)
t.add_column('tcp_bits', label='TCP Bits', iskey=False,
             extractor='tcp.bits', operation='sum', default_value=0)

report.add_widget(yui3.TimeSeriesWidget, t, 'Traffic By Type (Bits)', width=12)
