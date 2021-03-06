#!/usr/bin/env python

# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.



"""
This script connects to a NetShark appliance, collects a bounch of information
about it, and prints it the screen.
"""

from steelscript.netshark.core.app import NetSharkApp
from steelscript.common.datautils import bytes2human


class NetSharkInfo(NetSharkApp):

    def main(self):
        # Print the high level netshark info
        print 'APPLIANCE INFO:'

        info = self.netshark.get_serverinfo()
        print '\tAppliance Version: ' + info['version']
        print '\tAppliance Hostname: ' + info['hostname']
        print '\tUptime: ' + str(info['uptime'])
        print '\tWeb UI TCP Port: {0}'.format(info['webui_port'])

        stats = self.netshark.get_stats()
        print '\tPacket Storage: {0} total, {1} free, status:{2}'.format(
            bytes2human(stats['storage']['packet_storage']['total']),
            bytes2human(stats['storage']['packet_storage']['unused']),
            stats['storage']['packet_storage']['status'])
        print '\tIndex Storage: {0} total, {1} free, status:{2}'.format(
            bytes2human(stats['storage']['os_storage']['index_storage']['total']),
            bytes2human(stats['storage']['os_storage']['index_storage']['unused']),
            stats['storage']['os_storage']['status'])
        print '\tOS File System: {0} total, {1} free, status:{2}'.format(
            bytes2human(stats['storage']['os_storage']['disk_storage']['total']),
            bytes2human(stats['storage']['os_storage']['disk_storage']['unused']),
            stats['storage']['os_storage']['status'])
        print '\tmemory: {0} total, {1} free, status:{2}'.format(
            bytes2human(stats['memory']['total']),
            bytes2human(stats['memory']['available']),
            stats['memory']['status'])

        # Print the list of interfaces
        print 'INTERFACES:'
        for i in self.netshark.get_interfaces():
            print '\t{0} (OS name: {1})'.format(i, i.name)

        # Print the list of trace files
        print 'TRACE FILES:'
        for f in self.netshark.get_files():
            print '\t{0} ({1} bytes, created: {2})'.format(f, f.size, f.created)

        # Print the list of capture jobs
        print 'JOBS:'
        jobs = self.netshark.get_capture_jobs()
        for j in jobs:
            print '\t{0} (size: {1}, src interface: {2})'.format(j, j.size_limit, j.interface)

        # Print the list of trace clips
        print 'TRACE CLIPS:'
        for c in self.netshark.get_clips():
            if c.description == "":
                print '\t{0} ({1} bytes)'.format(c, c.size)
            else:
                print '\t{0}, {1} ({2} bytes)'.format(c.description, c, c.size)

        # Print the list of open views
        print 'OPEN VIEWS:'
        for view in self.netshark.get_open_views():
            print '\t{0}'.format(view.handle)
            for output in view.all_outputs():
                print '\t\t{0}'.format(output.id)


if __name__ == '__main__':
    NetSharkInfo().run()
