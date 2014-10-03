#!/usr/bin/env python

# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
This script can be used to view the amount of traffic reaching a given
NetShark. You can also provide a traffic expression and/or time filter to
limit the traffic counted in the results. A CSV config file may also be
provided to view results for multiple NetSharks at a time.
"""

import operator
import csv

from datetime import datetime

from steelscript.common.app import Application
from steelscript.netshark.core import NetShark
from steelscript.netshark.core.filters import NetSharkFilter, TimeFilter
from steelscript.netshark.core.types import Value
from steelscript.common.datautils import Formatter
from steelscript.common.service import UserAuth
from steelscript.common.timeutils import TimeParser


class SharkFinderApp(Application):
    def add_options(self, parser):
        super(SharkFinderApp, self).add_options(parser)

        parser.add_option('-H', '--host',
                          help='NetShark hostname or IP address')
        parser.add_option('-u', '--username', help="Username to connect with")
        parser.add_option('-p', '--password', help="Password to connect with")
        parser.add_option('-f', '--file', help=("CSV config file in format "
                                                "netshark, username, "
                                                "password"))

        parser.add_option('--starttime',
                          help=("Analyze traffic starting at this time "
                                "(timestamp format)"))
        parser.add_option('--endtime',
                          help=("Analyze traffic ending at this time "
                                "(timestamp format)"))
        parser.add_option(
            '--timerange',
            help=("Time range to analyze (defaults to \"last 1 hour\") "
                  "other valid formats are: \"4/21/13 4:00 to 4/21/13 5:00\" "
                  "or \"16:00:00 to 21:00:04.546\""))

        parser.add_option('--filter', dest='filters', action='append',
                          default=[],
                          help=("Filter to apply to analysis; can be repeated "
                                "as many times as desired"))

    def validate_args(self):
        super(SharkFinderApp, self).validate_args()

        if (self.options.timerange is not None and
                (self.options.starttime is not None
                 or self.options.endtime is not None)):
            self.parser.error("Can't use --timerange and --starttime/"
                              "--endtime together.")

        if self.options.file is not None and self.options.host is not None:
            self.parser.error(("When using a CSV file, you cannot specify a "
                               "NetShark on the command line."))
        elif self.options.host is None and self.options.file is None:
            self.parser.error("You must either specify a NetShark on the "
                              "command line or a config file with --file.")

    def get_jobs_bytes(self, shark, filters):
        """ Takes a shark and filters; returns an array of
            [(job_name, bytes), ...] or None if the shark returned no data
        """
        out = []
        for job in shark.get_capture_jobs():
            columns = [Value(shark.columns.generic.bytes)]

            with shark.create_view(job, columns, filters=filters) as view:
                data = view.get_data(aggregated=True)

            if data:
                job_bytes = data[0]['vals'][0][0]

                out.append((job.name, job_bytes))
        return out

    def get_csv_sharks_info(self, filename):
        with open(filename) as configfile:
            return [row for row in csv.reader(configfile)]

    def main(self):
        if self.options.timerange is not None:
            try:
                timefilter = TimeFilter.parse_range(self.options.timerange)
            except ValueError:
                print "Could not parse time filter expression."
                return
        elif (self.options.starttime is not None or
              self.options.endtime is not None):
            timeparser = TimeParser()

            if self.options.starttime is None:
                start_time = datetime.min
            else:
                try:
                    start_time = timeparser.parse(self.options.starttime)
                except ValueError:
                    print "Could not parse start timestamp"
                    return

            if self.options.endtime is None:
                end_time = datetime.now()
            else:
                try:
                    end_time = timeparser.parse(self.options.endtime)
                except ValueError:
                    print "Could not parse end timestamp"
                    return
            timefilter = TimeFilter(start_time, end_time)
        else:
            timefilter = None

        filters = [NetSharkFilter(f) for f in self.options.filters]
        if timefilter is not None:
            filters.append(timefilter)

        if self.options.file is None:
            sharks_info = [[self.options.host, self.options.username,
                            self.options.password]]
        else:
            sharks_info = self.get_csv_sharks_info(self.options.file)

        out_table = []
        for host, username, password in sharks_info:
            shark = NetShark(host, auth=UserAuth(username, password))

            jobs_bytes = self.get_jobs_bytes(shark, filters)
            if not jobs_bytes:
                print "(No data returned from NetShark {0}.)".format(host)
            else:
                for job_name, job_bytes in self.get_jobs_bytes(shark, filters):
                    out_table.append([host, job_name, job_bytes])

        if not out_table:
            print "No data found by any NetShark."
        else:
            out_table_sorted = sorted(out_table, reverse=True,
                                      key=operator.itemgetter(2))

            heads = ["NetShark", "Job", "Total bytes"]
            Formatter.print_table(out_table_sorted, heads)

if __name__ == '__main__':
    SharkFinderApp().run()
