# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import steelscript.appfwk.apps.report.modules.tables as tables
import steelscript.netshark.appfwk.datasources.netshark_scanner_source as \
    scanner

from steelscript.appfwk.apps.report.models import Report
from steelscript.netshark.appfwk.datasources.netshark import NetSharkTable

# Import the datasource module for this plugin (if needed)


report = Report.create("NetShark Scanner", field_order=['endtime', 'duration'],
                       hidden_fields=['netshark_device',
                                      'netshark_source_name', 'resolution'])
report.add_section()

# Create base table
shark_bytes_table = NetSharkTable.create(name='shark_bytes', aggregated=True)
shark_bytes_table.add_column('generic_bytes', label='Bytes', iskey=False,
                             extractor='generic.bytes', operation='sum')

# Make
table = scanner.SharksTable.create(name='sharks',
                                   basetable=shark_bytes_table)
table.add_column('name', "Name", datatype='string')
table.add_column('host', "Host", datatype='string')
table.add_column('capjob', "Capture Job", datatype='string')
table.add_column('bytes', "Bytes")

report.add_widget(tables.TableWidget, table, "Shark Capture Jobs Found",
                  width=12, height=200)
