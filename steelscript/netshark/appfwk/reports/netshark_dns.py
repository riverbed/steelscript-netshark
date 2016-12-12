# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import steelscript.appfwk.apps.report.modules.c3 as c3
from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.tables as tables

from steelscript.netshark.appfwk.datasources.netshark import NetSharkTable
#
# Define a NetShark Report and Table
#

report = Report.create('NetShark DNS', position=10)

report.add_section()


# DNS Queries Over time
name = 'DNS Queries and Response Time Over Time'
s = NetSharkTable.create(name, duration=15,
                         resolution='1min', aggregated=False)

s.add_column('time', label='Time', iskey=True, datatype='time',
             extractor='sample_time')
s.add_column('dns_count', label='DNS Query Count', datatype='integer',
             extractor='dns.query.count', operation='sum')
s.add_column('dns_response_time', label='DNS Response Time (ns)',
             units='ms', extractor='dns.response_time', operation='none')
report.add_widget(c3.TimeSeriesWidget, s, name, width=12,
                  altaxis=['dns_response_time'])

# DNS Response Code List for NetShark 1
name = 'DNS Response Codes'
s = NetSharkTable.create(name, duration=15, aggregated=True)

s.add_column('dns_is_success_str', label='DNS Success', iskey=True,
             datatype='string', extractor='dns.is_success_str',
             operation='none')
s.add_column('dns_total_queries', label='DNS Total Queries',
             datatype='integer', extractor='dns.query.count',
             operation='sum', sortdesc=True)

report.add_widget(c3.PieWidget, s, name, width=6)

# DNS Query Type for NetShark 1
name = 'DNS Query Type'
s = NetSharkTable.create(name, duration=15, aggregated=True)

s.add_column('dns_query_type', label='DNS Query Type', iskey=True,
             datatype='string', extractor='dns.query.type', operation='none')
s.add_column('dns_total_queries', label='DNS Total Queries',
             datatype='integer', extractor='dns.query.count',
             operation='sum', sortdesc=True)

report.add_widget(c3.PieWidget, s, name, width=6)

# DNS Request Details Table for NetShark 1
name = 'Top 100 DNS Requests'
s = NetSharkTable.create(name, duration=15, aggregated=True, rows=100)

s.add_column('dns_query_name', label='DNS Request', iskey=True,
             datatype='string', extractor='dns.query.name')
s.add_column('dns_is_success_str', label='Query Result', iskey=True,
             datatype='string', extractor='dns.is_success_str',
             operation='none')
s.add_column('dns_query_type', label='# Requests',
             datatype='string', extractor='dns.query.count',
             operation='sum', sortdesc=True)
report.add_widget(tables.TableWidget, s, name, width=12)
