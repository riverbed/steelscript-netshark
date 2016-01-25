# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from __future__ import division

import os
import re
import time
import pandas
import logging
import datetime

from django import forms
from functools import wraps
from django.conf import settings


from steelscript.netshark.core.filters import TimeFilter
from steelscript.netshark.core._class_mapping import path_to_class

from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.apps.datasource.models import \
    TableField, DatasourceTable, TableQueryBase
from steelscript.appfwk.apps.datasource.forms import \
    fields_add_time_selection, fields_add_resolution
from steelscript.appfwk.libs.fields import Function
from steelscript.wireshark.appfwk.datasources.wireshark_source import \
    fields_add_filterexpr
from steelscript.appfwk.apps.jobs import \
    Job, QueryComplete
from steelscript.netshark.appfwk.datasources.netshark import \
    netshark_source_name_choices
from steelscript.netshark.core.filters import BpfFilter

logger = logging.getLogger(__name__)

PCAP_DIR = os.path.join(settings.DATA_CACHE, 'pcaps')


def add_pcap_dir(f):
    return os.path.join(PCAP_DIR, f)


# decorator for bounded methods
# "http://stackoverflow.com/questions/306130
# /python-decorator-makes-function-forget-that-it-belongs-to-a-class"

def logtime(func):
    @wraps(func)
    def inner(*args, **kwargs):
        logger.debug("%s starting" % func.__name__)
        start_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        logger.debug("%s finished. It took %s."
                     % (func.__name__,
                        datetime.timedelta(0, end_time - start_time)))
        return ret
    return inner


class PcapDownloadTable(DatasourceTable):
    class Meta:
        proxy = True

    _query_class = 'PcapDownloadQuery'

    TABLE_OPTIONS = {'aggregated': False,
                     'include_files': False,
                     'include_interfaces': False,
                     'include_persistent': False,
                     'filters': [],
                     'wait_for_data': False,
                     'wait_duration': 10
                     }

    FIELD_OPTIONS = {'resolution': '1s',
                     'resolutions': ('1s', '1m', '15min', '1h')}

    def post_process_table(self, field_options):
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
        self.add_column('filename', datatype='string')


class PcapDownloadQuery(TableQueryBase):

    @logtime
    def download(self, export):
        export.download(self.filename, overwrite=True)

    @property
    def all_pcap_size(self):
        total = 0
        for f in os.listdir(PCAP_DIR):
            if f.endswith('.pcap'):
                try:
                    total += os.path.getsize(add_pcap_dir(f))
                except OSError:
                    logger.warning("Failed to read size of file %s" % f)
        return total

    def delete_oldest_pcap(self):

        oldest_time = 0
        oldest_pcap = None

        for f in os.listdir(PCAP_DIR):
            if f.endswith('.pcap'):
                try:
                    file_time = os.stat(add_pcap_dir(f)).st_mtime
                except OSError:
                    logger.warning("Failed to get time of file %s" % f)
                    continue

                if oldest_time == 0:
                    oldest_time = file_time
                    oldest_pcap = f
                elif file_time < oldest_time:
                    oldest_time = file_time
                    oldest_pcap = f

        if oldest_pcap is None:
            return

        try:
            os.unlink(add_pcap_dir(oldest_pcap))
        except OSError:
            logger.warning("Failed to remove oldest file %s" % oldest_pcap)

        handle = re.sub('\.pcap$', '', oldest_pcap)

        jobs = Job.objects.filter(handle=handle)
        if jobs:
            jobs.delete()

    def run(self):
        criteria = self.job.criteria

        netshark = DeviceManager.get_device(criteria.netshark_device)

        self.export_name = str(path_to_class(netshark,
                                             criteria.netshark_source_name))

        source = netshark.get_capture_job_by_name(self.export_name)

        timefilter = TimeFilter(criteria.starttime, criteria.endtime)

        handle = Job._compute_handle(self.table, criteria)

        # check if pcaps directory exists, if not make the directory
        if not os.path.exists(PCAP_DIR):
            os.mkdir(PCAP_DIR)

        while self.all_pcap_size > settings.PCAP_SIZE_LIMIT:
            self.delete_oldest_pcap()

        self.filename = add_pcap_dir('%s.pcap' % handle)

        filters = ([BpfFilter(filt) for filt in self.table.options.filters]
                   or None)
        with netshark.create_export(
                source, timefilter, filters=filters,
                wait_for_data=self.table.options.wait_for_data,
                wait_duration=self.table.options.wait_duration) as e:
            self.download(e)

        return QueryComplete(pandas.DataFrame([dict(filename=self.filename)]))
