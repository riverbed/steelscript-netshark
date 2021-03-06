#!/usr/bin/env python

# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
This script contains several examples that show more advanced view creation
and data retrieval scenarios.
"""

import time
import datetime

from steelscript.netshark.core.app import NetSharkApp
from steelscript.netshark.core.types import Value, Key
from steelscript.netshark.core.filters import NetSharkFilter
from steelscript.netshark.core.viewutils import write_csv

###############################################################################
# Script setup
###############################################################################

CSV_FILE_NAME = "result.csv"


class CreateViewEXApp(NetSharkApp):
    def main(self):
        # Open the remote file
        source = self.netshark.get_file('/admin/noon.cap')

        ######################################################################
        # Applying a view asynchronously.
        # When the amount of packets processed by a view on a netshark
        # appliance is big, it could take minutes for the view data to be
        # generated. This example shows how to use the sync parameter of
        # create_view() to create a view asynchronously and inform the user
        # about the processing progress.
        ######################################################################

        # Specify the column list
        columns = [
            Key(self.netshark.columns.ip.src),
            Value(self.netshark.columns.generic.bytes)
        ]

        # Create the view, making sure that sync is set to False
        v = self.netshark.create_view(source, columns, sync=False)

        # Loop until the progress reaches 100%
        while True:
            p = v.get_progress()
            print p

            if p == 100:
                break

            time.sleep(.5)

        # Retrieve the view data.
        output = v.get_data(aggregated=True)

        # Print the data to the screen
        for sample in output:
            print sample["t"].strftime("%H:%M:%S")
            for vals in sample['vals']:
                print '\t{0}\t{1}'.format(vals[0], vals[1])

        v.close()

        ######################################################################
        # Using filters.
        # Compared to the example in create_view.py, here we add a port 80
        # filter to the view to create a "web top talkers".
        ######################################################################

        # Specify a NetShark filter for port 80 packets. The NetSharkFilter
        # class implements Pilot filters, which means that you can paste any
        # filter from Pilot to the line below. Other valid filter types are
        # WiresharkDisplayFilter (which supports any Wireshark display
        # filter), BpfFilter (for Wireshark capture filters) and TimeFilter
        # (for time-based filtering).
        filters = [NetSharkFilter('tcp.port_pair="80"')]

        # Specify the column list
        columns = [
            Key(self.netshark.columns.ip.src),
            Value(self.netshark.columns.generic.bytes),
        ]

        # The list of filters is passes as a parameter to create_view()
        v = self.netshark.create_view(source, columns, filters)

        # Retrieve the view data.
        output = v.get_data(aggregated=True)

        # Save the data to disk
        write_csv(CSV_FILE_NAME, v.get_legend(), output)

        v.close()

        ######################################################################
        # Time-based data and manual output parsing.
        # This view shows the number of http requests over time, in a format
        # suitable to be represented on a stripchart.
        ######################################################################

        # Specify the column list
        columns = [Value(self.netshark.columns.http.answered_requests)]

        # The list of filters is passes as a parameter to create_view()
        print source, columns
        v = self.netshark.create_view(source, columns)

        # Retrieve the view data.
        # View.get_iterdata() returns an iterator to the view output instead
        # of the full data. This is ideal when the data is very big, because
        # it makes it possible to process it while it's downloaded, saving
        # memory at the client side.
        # Note also that we don't specify aggregated=True. This means that
        # we will receive a sample for each second interval.
        output = v.get_iterdata()

        # Instad of using write_csv(), this time we manually parse the samples
        # in the output.
        # Each sample is a dictionary with the following remarkable fields:
        #  - time: the sample time as a datetime
        #  - vals: a list of tuples, containing the data for the sample
        # In this case, since our view doesn't have keys, each sample contains
        # exactly one value. The next example shows how to deal with multiple
        # values per sample.
        for sample in output:
            print '{0}\t{1}'.format(sample["t"], sample['vals'][0][0])

        # close the view
        v.close()

        ######################################################################
        # Advanced get_data() usage.
        # get_data() has some pretty powerful functionality for server-side
        # sorting and filtering of view output data.
        # This example splits the data in 1 minute intervals, and for each
        # interval it displays the top 3 talkers.
        ######################################################################

        # Specify the column list
        columns = [
            Key(self.netshark.columns.ip.src),
            Value(self.netshark.columns.generic.bytes)
        ]

        # The list of filters is passes as a parameter to create_view()
        v = self.netshark.create_view(source, columns)

        # Retrieve the view data.
        delta = datetime.timedelta(minutes=1)
        output = v.get_data(delta=delta,            # 1 minute samples
                            sortby=1,               # Sort by column 1 (bytes)
                            sorttype='descending',  # Sort from big to small
                            fromentry=0,            # For each 1 min sample,
                                                    # the first element to
                                                    # display is the biggest
                                                    # one.
                            toentry=2               # For each 1 min sample,
                                                    # the last element to
                                                    # display is the third
                                                    # biggest one.
                            )

        # Proceed printing the data to the screen
        for sample in output:
            print sample["t"]
            for vals in sample['vals']:
                print '\t{0}\t{1}'.format(vals[0], vals[1])

        v.close()


if __name__ == '__main__':
    NetSharkApp().run()
