#!/usr/bin/env python

# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
This script can be used to export a filtered set of packets from Trace Files,
Capture Jobs or Trace clips on a Shark Appliance.
"""

from steelscript.netshark.core.app import NetSharkApp
from steelscript.netshark.core.filters import NetSharkFilter, TimeFilter
from steelscript.common.timeutils import datetime_to_seconds, string_to_datetime


class DownloadApp(NetSharkApp):
    def add_options(self, parser):
        super(DownloadApp, self).add_options(parser)
        parser.add_option('--filename', dest="filename", default=None,
                          help='local filename to store export')

        parser.add_option('--jobname', dest="jobname", default=None,
                          help='job ID to export')
        parser.add_option('--clipname', dest="clipname", default=None,
                          help='clip ID to export')

        parser.add_option('--starttime', dest="start_time", default=None,
                          help='start time for export (timestamp format)')
        parser.add_option('--endtime', dest="end_time", default=None,
                          help='end time for export (timestamp format)')
        parser.add_option('--timerange', dest="timerange", default=None,
                          help='Time range to analyze (defaults to "last 1 hour") '
                               'other valid formats are: "4/21/13 4:00 to 4/21/13 5:00" '
                               'or "16:00:00 to 21:00:04.546"')

        parser.add_option('--filter', dest="filters", action="append",
                          help='filter to apply to export, can be repeated as '
                               'many times as desired')

    def validate_args(self):
        """ Ensure either jobname or clipname provided
        """
        super(DownloadApp, self).validate_args()

        if ( (self.options.jobname and self.options.clipname) or
             (not self.options.jobname and not self.options.clipname)):
            self.parser.error('Select one of either --jobname or --clipname')

    def main(self):
        if self.options.jobname:
            export_name = self.options.jobname
            source = self.netshark.get_capture_job_by_name(export_name)
            create_export = self.netshark.api.jobs.create_export
            status_export = self.netshark.api.jobs.get_export_details
            download_export = self.netshark.api.jobs.get_packets_from_export
            delete_export = self.netshark.api.jobs.delete_export
        elif self.options.clipname:
            export_name = self.options.clipname
            source = self.netshark.get_trace_clip_by_description(export_name)
            create_export = self.netshark.api.clips.create_export
            status_export = self.netshark.api.clips.get_export_details
            download_export = self.netshark.api.clips.get_packets_from_export
            delete_export = self.netshark.api.clips.delete_export

        filename = self.options.filename
        if not filename:
            filename = '%s_export.pcap' % export_name

        if self.options.timerange:
            timefilter = TimeFilter.parse_range(self.options.timerange)
        elif self.options.start_time and self.options.end_time:
            start = string_to_datetime(float(self.options.start_time))
            end = string_to_datetime(float(self.options.end_time))
            timefilter = TimeFilter(start, end)
        else:
            self.optparse.error('Select either --timerange or --start and --end times')

        config = {
            #'output_filename': filename,
            'output_format': 'PCAP_US',
            'start_time': datetime_to_seconds(timefilter.start),
            'end_time': datetime_to_seconds(timefilter.end),
        }

        if self.options.filters:
            filters = [f.split('=') for f in self.options.filters]
            filters = [r'%s="%s"' % (k, v) for k, v in filters]
            config['filters'] = [NetSharkFilter(filt).bind(self.netshark) for filt in filters]

        try:
            export_id = create_export(source.id, config=config)

            print 'Export created with ID: %s' % export_id

            status = status_export(source.id, export_id['id'])

            print 'Current status of export is:\n%s' % status

            if status['status']['state'] == 'RUNNING':
                print 'beginning download to file %s' % filename
                download_export(source.id, export_id['id'], filename)
        finally:
            try:
                print 'Trying to delete export ... ',
                delete_export(source.id, export_id['id'])
                print 'deleted.'
            except:
                print 'Error when trying to delete export.  Ignoring.'
                pass


if __name__ == '__main__':
    DownloadApp().run()
