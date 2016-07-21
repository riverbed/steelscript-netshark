#!/usr/bin/env python

# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
This script prints out the jobs on a given shark.
"""

from steelscript.netshark.core.app import NetSharkApp
from steelscript.common.datautils import Formatter


class ListJobs(NetSharkApp):
    def add_options(self, parser):
        super(ListJobs, self).add_options(parser)

    def validate_args(self):
        """ Ensure columns are included """
        super(ListJobs, self).validate_args()

    def console(self, header, data):
        print ''
        print header
        print '-' * len(header)

        Formatter.print_table(data, ('id', 'source', 'source_path'))

    def main(self):

        # Get capture jobs
        jobs = self.netshark.get_capture_jobs()
        data = [(x, job.name, job.source_path) for x, job in enumerate(jobs)]
        self.console('Capture Jobs', data)

        clips = self.netshark.get_clips()
        data = [(x, 'Clip: ' + c.description, c.source_path)
                for x, c in enumerate(clips)]
        self.console('Clips', data)

        files = self.netshark.get_files()
        data = [(x, 'File: ' + f.path, f.source_path)
                for x, f in enumerate(files)]
        self.console('Uploaded Files/PCAPs', data)


if __name__ == '__main__':
    ListJobs().run()
