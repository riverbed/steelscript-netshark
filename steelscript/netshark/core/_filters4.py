# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from __future__ import absolute_import

import datetime
try:
    from steelscript.common.datetime import datetimeng
    datetimeng_available = True
except:
    datetimeng_available = False

from steelscript.common import timeutils


class TimeFilter(object):
    def __init__(self, start, end):
        if start is not None:
            self.start = timeutils.force_to_utc(start)
        else:
            self.start = 0

        if end is not None:
            self.end = timeutils.force_to_utc(end)
        else:
            self.end = 0

    def __unicode__(self):
        return '<TimeFilter - start: {}, end: {}>'.format(self.start, self.end)

    def to_dict(self):
        return {
            'type': 'TIME',
            'value': str(timeutils.datetime_to_nanoseconds(self.start)) +
            ', ' + str(timeutils.datetime_to_nanoseconds(self.end))
            }


class NetSharkFilter(object):
    def __init__(self, string):
        self.string = string

    def __unicode__(self):
        return '<{} - filter: {}>'.format(self.__class__, self.string)

    def to_dict(self):
        return {
            'type': 'SHARK',
            'value': self.string
            }


class BpfFilter(object):
    def __init__(self, string):
        self.string = string

    def __unicode__(self):
        return '<{} - filter: {}>'.format(self.__class__, self.string)

    def to_dict(self):
        return {
            'type': 'BPF',
            'value': self.string
            }
