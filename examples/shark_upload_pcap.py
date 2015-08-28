#!/usr/bin/env python

# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os

from steelscript.netshark.core.app import NetSharkApp


class UploadPcap(NetSharkApp):
    def add_options(self, parser):
        super(UploadPcap, self).add_options(parser)
        parser.add_option('--filepath',
                          help='path to pcap tracefile to upload')
        parser.add_option('--destname', default=None,
                          help='location to store on server, defaults to '
                               '<username>/<basename of filepath>')

    def validate_args(self):
        super(UploadPcap, self).validate_args()

        basedir = '/' + self.options.username

        if not self.options.destname:
            dst = os.path.join(basedir,
                               os.path.basename(self.options.filepath))
            self.options.destname = dst

    def main(self):
        self.netshark.upload_trace_file(
            path=self.options.destname,
            local_file=self.options.filepath
        )


if __name__ == "__main__":
    app = UploadPcap()
    app.run()
