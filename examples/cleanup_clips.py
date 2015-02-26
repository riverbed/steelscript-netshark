#!/usr/bin/env python

# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
This script lists out and optionally deletes all clips on a NetShark.
"""

import sys

from steelscript.netshark.core.app import NetSharkApp
from steelscript.commands.steel import prompt_yn


class CreateView(NetSharkApp):
    def add_options(self, parser):
        super(CreateView, self).add_options(parser)
        parser.add_option('--force',
                          help='Delete all clips without prompting',
                          default=False)

    def validate_args(self):
        """Validate arguments if needed"""
        super(CreateView, self).validate_args()

    def main(self):
        clips = self.netshark.get_clips(force_refetch=True)

        if clips:
            for i, c in enumerate(clips):
                print '%3d) %s - %s' % (i, c, c.data['config']['description'])

            if not self.options.force:
                if not prompt_yn('Delete all these clips?',
                                 default_yes=False):
                    print 'Okay, exiting.'
                    sys.exit(0)

            for c in clips:
                c.delete()

            print 'Deleted.'
        else:
            print 'No trace clips found on NetShark.'


if __name__ == '__main__':
    CreateView().run()
