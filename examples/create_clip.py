#!/usr/bin/env python

# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.



"""
This simple script creates a trace clip on the first available job, with the
following properties:
 - time range is the last 30 minutes
 - the clip contains only packets for the IP address 192.168.0.1
"""

from steelscript.netshark.core.app import NetSharkApp
from steelscript.netshark.core.filters import TimeFilter, NetSharkFilter


def main(app):
    # Get the list of jobs
    jobs = app.shark.get_capture_jobs()
    if len(jobs) == 0:
        print ("No jobs on the appliance, you can create jobs using the "
               "'create_job.py' and start/stop them using the 'control_job.py' script.")
        return 0

    # Pick the first job
    job = jobs[0]
    print 'creating a 30 minutes clip on job {0}'.format(job.name)

    # set the filters
    filters = (
        # Time filter: keep the last 30 minutes
        TimeFilter.parse_range("last 30 m"),

        # IP address filter: keep only 192.168.0.1
        NetSharkFilter('ip.src="192.168.0.1"')
    )

    # Create the clip
    clip = job.add_clip(filters, "a_test_clip")

    print 'Clip with the following properties created:'
    print ''
    print 'ID: %s' % clip.id
    print 'Description: %s' % clip.description
    print 'Source Path: %s' % clip.source_path
    print 'Size: %s' % clip.size


if __name__ == '__main__':
    NetSharkApp(main).run()
