# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.tables as tables

from steelscript.netshark.appfwk.datasources.netshark import \
    NetSharkJobsTable

report = Report.create('NetShark Capture Jobs', position=10)

report.add_section()

# Table for NetShark
t = NetSharkJobsTable.create(name='Netshark Capture Jobs', cacheable=False)

t.add_column('netshark', label='NetShark', datatype='string', iskey=True)
t.add_column('job_name', label='Job Name', datatype='string')
t.add_column('job_id', label='Job ID', datatype='string', iskey=True)

t.add_column('interface', label='Interface', datatype='string')
t.add_column('bpf_filter', label='BPF Filter', datatype='string')
t.add_column('dpi_enabled', label='Enable DPI', datatype='string')
t.add_column('index_enabled', label='Enable Indexing', datatype='string')
t.add_column('state', label='Status', datatype='string')

t.add_column('start_time', label='Start Time', datatype='string')
t.add_column('end_time', label='End Time', datatype='string')

t.add_column('size', label='Packet Capture Size (Bytes)', datatype='integer')

t.add_column('last_sec_written', label='Last Second Written (Bytes)',
             datatype='integer')
t.add_column('last_min_written', label='Last Minute Written (Bytes)',
             datatype='integer')
t.add_column('last_hr_written', label='Last Hour Written (Bytes)',
             datatype='integer')
t.add_column('last_sec_dropped', label='Last Second Dropped (Bytes)',
             datatype='integer')
t.add_column('last_min_dropped', label='Last Minute Dropped (Bytes)',
             datatype='integer')
t.add_column('last_hr_dropped', label='Last Hour Dropped (Bytes)',
             datatype='integer')

report.add_widget(tables.TableWidget, t, 'netshark-jobs', width=12,
                  height=0, searching=True)
