# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.common.app import Application
from steelscript.netshark.core import NetShark


class NetSharkApp(Application):
    """Simple class to wrap common command line parsing"""
    def __init__(self, *args, **kwargs):
        super(NetSharkApp, self).__init__(*args, **kwargs)
        self.netshark = None

    def parse_args(self):
        super(NetSharkApp, self).parse_args()

    def add_positional_args(self):
        self.add_positional_arg('host', 'NetShark hostname or IP address')

    def add_options(self, parser):
        super(NetSharkApp, self).add_options(parser)
        self.add_standard_options()

    def setup(self):
        self.netshark = NetShark(self.options.host, port=self.options.port,
                                 auth=self.auth,
                                 force_version=self.options.api_version)
