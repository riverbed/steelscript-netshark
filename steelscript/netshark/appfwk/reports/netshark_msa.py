# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.raw as raw

from steelscript.netshark.appfwk.datasources.netshark_msa import \
    MSADownloadTable

#
# Download PCAPs from two NetSharks and upload to a third for MSA analysis
#

report = Report.create('NetShark MSA Download', position=10)

report.add_section()

t = MSADownloadTable.create(name='MultiSegment Table')
t.add_column('results', label='Results', iskey=True)

report.add_widget(raw.TableWidget, t, 'MSA Results', width=12, height=400)
