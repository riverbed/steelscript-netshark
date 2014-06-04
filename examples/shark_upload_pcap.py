#!/usr/bin/env python

# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.netshark.core.app import NetSharkApp


class UploadPcap(NetSharkApp):
    def add_option(self, parser):
        super(UploadPcap, self).add_options(parser)
        parser.set_usage('%prog SHARK FILE DEST')

    def validate_args(self):
        super(UploadPcap, self).validate_args()
        if len(self.args) != 3:
            self.parser.error('wrong number of arguments')

    def main(self):
        self.netshark.upload_trace_file(self.args[2], self.args[1])


if __name__ == "__main__":
    app = UploadPcap()
    app.run()
