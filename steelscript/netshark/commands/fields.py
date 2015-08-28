#!/usr/bin/env python

# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
List all the key and column fields that the given NetShark appliance supports.
"""

import optparse

from steelscript.netshark.core.app import NetSharkApp
from steelscript.common.datautils import Formatter


class Command(NetSharkApp):
    help = 'List available NetShark extractor fields'

    def add_options(self, parser):
        super(Command, self).add_options(parser)
        group = optparse.OptionGroup(parser, "Column output options")
        group.add_option('--truncate', default=False, action='store_true',
                         help="truncate description column, don't wrap")
        group.add_option('-w', '--table-width', default=120,
                         help="max char width of table output, default: 120")
        parser.add_option_group(group)

    def main(self):
        headers = ['ID', 'Description', 'Type']
        data = [(f.id, f.description, f.type)
                for f in self.netshark.get_extractor_fields()]
        data.sort()
        Formatter.print_table(data,
                              headers,
                              padding=2,
                              max_width=int(self.options.table_width),
                              long_column=1,
                              wrap_columns=(not self.options.truncate))
