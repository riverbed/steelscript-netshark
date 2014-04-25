# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.


"""
Filters can be use to reduce the traffic that is fed to NetShark views, and are
basic tools when doing data analysis with a NetShark appliance.
NetShark supports 4 main classes of filters: the native NetShark filters, Time
filters, BPF filters (also known as Wireshark capture filters) and Wireshark
display filters.
"""

from __future__ import absolute_import

from steelscript.common import timeutils
from steelscript.netshark.core._api4 import API4_0
from steelscript.netshark.core._api5 import API5_0
from steelscript.netshark.core import _filters4
from steelscript.netshark.core.netshark import FILTERS_MAP

FILTERS_MAP.update({
        API4_0: _filters4,
        API5_0: _filters4
        })


__all__ = [ 'TimeFilter', 'NetSharkFilter', 'WiresharkDisplayFilter', 'BpfFilter' ]

class Filter(object):
    def __init__(self, *args, **kwargs):
        super(Filter, self).__init__(*args, **kwargs)

    def bind(self, shark):
        """Get the correct version of the filter based on the netshark version
        """
        mod = FILTERS_MAP[shark.api.__class__]
        try:
            cls = getattr(mod, self.__class__.__name__)
        except AttributeError:
            return self

        return cls(**self.__dict__)



class TimeFilter(Filter):
    def __init__(self, start, end, gmtoffset=0):
        super(TimeFilter, self).__init__()
        self.start = start
        self.end = end
        self.gmtoffset = gmtoffset

    @classmethod
    def parse_range(cls, string, offset = 0):
        (start, end) = timeutils.parse_range(string)
        return cls(start, end, offset)


class NetSharkFilter(Filter):
    def __init__(self, string):
        super(NetSharkFilter, self).__init__()
        self.string = string


class WiresharkDisplayFilter(Filter):
    def __init__(self, string):
        super(WiresharkDisplayFilter, self).__init__()
        self.string = string


class BpfFilter(Filter):
    def __init__(self, string):
        super(BpfFilter, self).__init__()
        self.string = string
