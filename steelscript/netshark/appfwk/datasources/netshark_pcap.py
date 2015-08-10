# Copyright (c) 2013-2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from __future__ import division

import time
import math
import copy
import pandas
import logging
import datetime
import subprocess
import multiprocessing

from django import forms
from functools import wraps

from steelscript.netshark.core.filters import TimeFilter
from steelscript.netshark.core._class_mapping import path_to_class

from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.apps.datasource.models import \
    Column, TableField, Table
from steelscript.appfwk.apps.datasource.forms import \
    fields_add_time_selection, fields_add_resolution
from steelscript.appfwk.libs.fields import Function
from steelscript.wireshark.appfwk.datasources.wireshark_source import \
    fields_add_filterexpr
from steelscript.wireshark.core.pcap import PcapFile
from steelscript.appfwk.apps.datasource.modules.analysis import \
    AnalysisQuery, AnalysisException, AnalysisTable
from steelscript.appfwk.apps.jobs import \
    Job, QueryContinue, QueryComplete
from steelscript.netshark.appfwk.datasources.netshark import \
    netshark_source_name_choices
from steelscript.netshark.core.filters import BpfFilter

logger = logging.getLogger(__name__)

# decorator for bounded methods
# "http://stackoverflow.com/questions/306130
# /python-decorator-makes-function-forget-that-it-belongs-to-a-class"


SPLIT_DIR_PREFIX = '/tmp/splits_'


def logtime(func):
    @wraps(func)
    def inner(*args, **kwargs):
        logger.debug("NetSharkPcapQuery: %s starting" % func.__name__)
        start_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        logger.debug("NetSharkPcapQuery: %s finished. It took %s."
                     % (func.__name__,
                        datetime.timedelta(0, end_time - start_time)))
        return ret
    return inner


class NetSharkPcapColumn(Column):
    class Meta:
        proxy = True

    COLUMN_OPTIONS = {'field': None,
                      'operation': 'sum'}


class NetSharkPcapTable(AnalysisTable):

    class Meta:
        proxy = True

    _column_class = 'NetSharkPcapColumn'
    _query_class = 'NetSharkPcapQuery'

    TABLE_OPTIONS = {'aggregated': False,
                     'include_files': False,
                     'include_interfaces': False,
                     'include_persistent': False,
                     'filters': None,
                     'split_threshold': 0,
                     }

    FIELD_OPTIONS = {'resolution': '1s',
                     'resolutions': ('1s', '1m', '15min', '1h')}

    @classmethod
    def create(cls, name, wireshark_table, **kwargs):
        kwargs['tables'] = {}
        kwargs['related_tables'] = {'basetable': wireshark_table}
        return super(NetSharkPcapTable, cls).create(name, **kwargs)

    def post_process_table(self, field_options):
        self.copy_columns(self.options['related_tables']['basetable'])

        fields_add_device_selection(self, keyword='netshark_device',
                                    label='NetShark', module='netshark',
                                    enabled=True)
        fields_add_time_selection(self, show_start=True,
                                  initial_start_time='now-1m',
                                  show_end=True,
                                  show_duration=False)

        fields_add_resolution(self,
                              initial=field_options['resolution'],
                              resolutions=field_options['resolutions'])

        func = Function(netshark_source_name_choices, self.options)
        TableField.create(keyword='netshark_source_name', label='Source',
                          obj=self,
                          field_cls=forms.ChoiceField,
                          parent_keywords=['netshark_device'],
                          dynamic=True,
                          pre_process_func=func)

        fields_add_filterexpr(obj=self)


class NetSharkPcapQuery(AnalysisQuery):

    @logtime
    def download(self, export):
        export.download(self.filename, overwrite=True)

    @logtime
    def split_pcap(self):
        cpu_num = multiprocessing.cpu_count()
        per_file = int(math.ceil(self.pkt_num/cpu_num))

        subprocess.Popen('rm -rf %s' % self.output_dir, shell=True).wait()

        subprocess.Popen('mkdir %s' % self.output_dir, shell=True).wait()
        cmd = 'editcap -c %s %s %s/%s' % (per_file, self.filename,
                                          self.output_dir, self.export_name)
        logger.debug("NetSharkPcapQuery: %s" % cmd)
        subprocess.Popen(cmd, shell=True).wait()

    def analyze(self, jobs):

        criteria = self.job.criteria

        criteria.entire_pcap = True

        netshark = DeviceManager.get_device(criteria.netshark_device)

        self.export_name = str(path_to_class(netshark,
                                             criteria.netshark_source_name))

        source = netshark.get_capture_job_by_name(self.export_name)

        timefilter = TimeFilter(criteria.starttime, criteria.endtime)

        self.filename = '%s_export.pcap' % self.export_name

        filters = [BpfFilter(filt) for filt in self.table.options.filters]

        with netshark.create_export(source, timefilter, filters=filters) as e:
            self.download(e)

        pcap = PcapFile(self.filename)

        try:
            pcap_info = pcap.info()
        except ValueError:
            raise AnalysisException("No packets in %s" % self.filename)

        logger.debug("%s NetSharkPcapQuery: File info %s" % (self, pcap_info))

        self.pkt_num = int(pcap_info['Number of packets'])

        min_pkt_num = self.table.options.split_threshold

        basetable = Table.from_ref(
            self.table.options.related_tables['basetable']
        )

        depjobs = {}

        self.output_dir = SPLIT_DIR_PREFIX + self.filename

        if self.pkt_num < min_pkt_num:
            # No need to split the pcap file
            criteria.pcapfilename = self.filename
            job = Job.create(table=basetable, criteria=criteria,
                             update_progress=False, parent=self.job)

            depjobs[job.id] = job

            logger.debug("NetSharkPcapQuery starting single job")
            return QueryContinue(self.collect, depjobs)

        self.split_pcap()

        split_files = subprocess.check_output('ls %s' % self.output_dir,
                                              shell=True).split()

        if not split_files:
            raise AnalysisException('No pcap file found after splitting %s'
                                    % self.filename)

        for split in split_files:
            # use wireshark table
            criteria = copy.copy(self.job.criteria)
            criteria.pcapfilename = '/'.join([self.output_dir, split])

            job = Job.create(table=basetable, criteria=criteria,
                             update_progress=False, parent=self.job)

            depjobs[job.id] = job

        logger.debug("NetSharkPcapQuery starting multiple jobs")

        return QueryContinue(self.collect, jobs=depjobs)

    def collect(self, jobs=None):
        dfs = []
        for jid, job in jobs.iteritems():
            if job.status == Job.ERROR:
                raise AnalysisException("%s for pcap file %s failed: %s"
                                        % (job, job.criteria.pcapfilename,
                                           job.message))
            subdf = job.data()
            if subdf is None:
                continue
            dfs.append(subdf)

        if not dfs:
            logger.debug("NetSharkPcapQuery: no data is collected")
            return QueryComplete(None)

        df = pandas.concat(dfs, ignore_index=True)

        logger.debug("NetSharkPcapQuery: Query ended.")

        return QueryComplete(df)
