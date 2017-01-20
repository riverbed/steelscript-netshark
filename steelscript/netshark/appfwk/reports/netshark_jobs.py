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


report.add_widget(tables.TableWidget, t, 'netshark-jobs', width=12)
