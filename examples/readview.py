#!/usr/bin/env python

# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
This script demonstrates how to use the View class to do two
simple and common tasks:
1. enumerate all the existing views on a netshark (the -l command line option)
2. attach to an existing view, extract a section of data from it, and
   write it to a CSV file
"""

from steelscript.netshark.core.app import NetSharkApp
from steelscript.netshark.core import viewutils


class ReadView(NetSharkApp):

    def add_options(self, parser):
        super(ReadView, self).add_options(parser)
        parser.add_option('-l', '--listviews', action="store_true",
                          default=False, help='print a list of running views')
        parser.add_option('-v', '--viewname', default=None,
                          help='view name to read')
        parser.add_option('-f', '--filename', default=None,
                          help='write CSV file to given file name')
        parser.add_option('-o', '--output', default=None,
                          help='retrieve only the specified output field')

    def validate_args(self):
        super(ReadView, self).validate_args()
        if self.options.listviews:
            # list views ignores other options
            return

        if not self.options.viewname:
            self.parser.error('view name required, use "-v" option to specify')

    def _do_one_output(self, output):
        legend = output.get_legend()
        data = output.get_iterdata()

        # If the -f option has been used, we save the data to disk as csv,
        # otherwise we print it to the screen.
        if self.options.filename is not None:
            viewutils.write_csv(self.options.filename, legend, data)
        else:
            viewutils.print_data(legend, data)

    def main(self):
        if self.options.listviews:
            # If -l is specified, we show the list of views running on the
            # appliance, and the outputs for each of them,
            views = self.netshark.get_open_views()
            if len(views) == 0:
                print 'there are no views!'
            for view in views:
                print view.handle
                for output in view.all_outputs():
                    print '  {0}'.format(output.id)
            return

        # Retrieve details about a specific view
        try:
            view = self.netshark.get_open_view_by_handle(self.options.viewname)
        except KeyError:
            print 'cannot find view {0}'.format(self.options.viewname)
            return -1

        # A view can have one or more outputs. Each output corresponds to one
        # of the charts that can be seend when opening the view in Pilot.
        # If an output name is specified, we will print (or save) the data for
        # that output only.
        # Otherwise, we merge all the outputs and print them all.
        if self.options.output is not None:
            self._do_one_output(view.get_output(self.options.output))
        else:
            outputs = view.all_outputs()
            if len(outputs) > 1:
                try:
                    mixer = viewutils.OutputMixer()
                    for o in outputs:
                        mixer.add_source(o, '')
                    self._do_one_output(mixer)
                    outputs = []
                except NotImplementedError:
                    pass

            # we can end up here if there is just one output or if
            # we can't mix multiple outputs
            if len(outputs) > 0:
                for o in outputs:
                    print 'Output %s' % o.id
                    self._do_one_output(o)


if __name__ == '__main__':
    ReadView().run()
