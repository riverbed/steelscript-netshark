# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import steelscript.appfwk.apps.report.modules.c3 as c3
from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.tables as tables
from steelscript.netshark.appfwk.datasources.netshark import \
    NetSharkTable

#
# Define a NetShark Report and Table
#
report = Report.create('NetShark TCP Errors', position=10)
report.add_section()

tcp = NetSharkTable.create(name='TCPErrors', aggregated=True)

tcp.add_column('error_type', label='TCP Error Type', iskey=True,
               extractor='tcp.error_type', datatype='string')
tcp.add_column('errors', label='TCP Errors', sortdesc=True,
               extractor='tcp.errors', datatype='integer', operation='sum',
               default_value=0)

report.add_widget(c3.BarWidget, tcp,
                  'TCP Errors', width=6, height=400)
report.add_widget(tables.TableWidget, tcp,
                  'TCP Errors Table', width=6, height=400)
