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
        self.optparse.set_usage('%prog NETSHARK_HOSTNAME <options>')
        self.netshark = None

    def setup(self):
        self.netshark = NetShark(self.args[0], port=self.options.port,
                                 auth=self.auth,
                                 force_version=self.options.api_version)

    def validate_args(self):
        if len(self.args) < 1:
            self.optparse.error('missing NETSHARK_HOSTNAME')
