# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This file defines a data source for querying data.

There are three parts to defining a data source:

* Defining column options via a Column class
* Defining table options via a DatasourceTable
* Defining the query mechanism via TableQuery

Note that you can define multiple Column and Table classes
in the same file, but only one TableQuery.  If you need
to define multiple types of queries, create multiple
files in this directory named accordingly.

"""

import copy
import logging
import datetime

import pandas

from steelscript.appfwk.apps.datasource.models import Table
from steelscript.appfwk.apps.jobs import \
    Job, QueryContinue, QueryComplete
from steelscript.appfwk.apps.datasource.modules.analysis import \
    AnalysisTable, AnalysisQuery
from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.devices.models import Device

logger = logging.getLogger(__name__)


class SharksTable(AnalysisTable):
    class Meta:
        proxy = True

    _query_class = 'SharksQuery'

    @classmethod
    def create(cls, name, basetable, **kwargs):
        kwargs['related_tables'] = {'basetable': basetable}
        return super(SharksTable, cls).create(name, **kwargs)


class SharksQuery(AnalysisQuery):
    def analyze(self, jobs):
        criteria = self.job.criteria

        sharks_query_table = Table.from_ref(
            self.table.options.related_tables['basetable'])

        depjobs = {}

        # For every (shark, job), we spin off a new job to grab the data, then
        # merge everything into one dataframe at the end.
        for s in Device.objects.filter(module='netshark', enabled=True):
            shark = DeviceManager.get_device(s.id)

            for capjob in shark.get_capture_jobs():
                # Start with criteria from the primary table -- this gives us
                # endtime, duration and netshark_filterexpr.
                bytes_criteria = copy.copy(criteria)
                bytes_criteria.netshark_device = s.id
                bytes_criteria.netshark_source_name = 'jobs/' + capjob.name
                bytes_criteria.resolution = datetime.timedelta(0, 1)
                bytes_criteria.aggregated = True

                job = Job.create(table=sharks_query_table,
                                 criteria=bytes_criteria)

                depjobs[job.id] = job

        return QueryContinue(self.collect, depjobs)

    def collect(self, jobs=None):

        out = []
        for jid, job in jobs.iteritems():
            sharkdata = job.data()
            if sharkdata is not None:
                s = Device.objects.get(id=job.criteria.netshark_device)
                out.append([s.name,
                            s.host,
                            job.criteria.netshark_source_name[5:],
                            sharkdata['generic_bytes']])

        columns = ['name', 'host', 'capjob', 'bytes']
        df = pandas.DataFrame(out, columns=columns)
        return QueryComplete(df)
