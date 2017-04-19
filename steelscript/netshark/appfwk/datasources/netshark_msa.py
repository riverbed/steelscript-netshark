# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import os

import copy
import logging
import pprint

from django import forms

from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.common import datetime_to_seconds
from steelscript.common.exceptions import RvbdHTTPException
from steelscript.netshark.appfwk.datasources.netshark import NetSharkTable, \
    fields_add_bpf_filterexpr, NetSharkQuery, NetSharkColumn
from steelscript.netshark.appfwk.datasources.netshark_pcap import \
    PcapDownloadTable

from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.apps.datasource.modules.analysis import \
    AnalysisTable, AnalysisQuery
from steelscript.appfwk.apps.datasource.models import TableField, Table
from steelscript.appfwk.apps.datasource.forms import \
    fields_add_time_selection, IDChoiceField, fields_add_resolution
from steelscript.appfwk.libs.fields import Function
from steelscript.wireshark.appfwk.datasources.wireshark_source import \
    fields_add_filterexpr
from steelscript.appfwk.apps.jobs import QueryComplete, QueryContinue
from steelscript.appfwk.apps.jobs.models import Job


logger = logging.getLogger(__name__)


def check_netshark_file(netshark, fname, remove=False):
    """Check for existance of file on NetShark, optionally removing."""
    if netshark.exists(fname):
        if remove:
            logger.info("Removing existing file: %s" % fname)
            f = netshark.get_file(fname)
            f.remove()
        return True
    return False


def netshark_source_choices(form, id_, field_kwargs, params):
    """Query netshark for available capture jobs / trace clips."""
    # simplified clone from base netshark datasource that allows for
    # custom field names

    netshark_device = form.get_field_value(params['field'], id_)
    if netshark_device == '':
        choices = [('', '<No netshark device>')]
    else:
        netshark = DeviceManager.get_device(netshark_device)

        choices = []

        for job in netshark.get_capture_jobs():
            choices.append((job.source_path, job.name))

        for clip in netshark.get_clips():
            choices.append((clip.source_path, 'Clip: ' + clip.description))

    field_kwargs['choices'] = choices


def netshark_msa_file_choices(form, id_, field_kwargs, params):
    """Query netshark for available MSA files."""

    netshark_device = form.get_field_value('netshark_device', id_)
    if netshark_device == '':
        choices = [('', '<No netshark device>')]
    else:
        netshark = DeviceManager.get_device(netshark_device)

        choices = []

        # TODO - this enables automatic refresh
        # whenever the report or criteria get reloaded, but
        # it will cause some extra load when the report runs
        # since each time a TableForm gets created all the files
        # will be re-queried
        for f in netshark.get_files(force_refetch=True):
            if hasattr(f, 'list_linked_files'):
                choices.append((f.source_path, 'MSA File: ' + f.path))

    field_kwargs['choices'] = choices


class MSADownloadTable(AnalysisTable):
    class Meta:
        proxy = True
        app_label = 'steelscript.netshark.appfwk'

    _query_class = 'MSADownloadQuery'

    TABLE_OPTIONS = {'msa_folder': None,
                     'overwrite_folder': True}

    @classmethod
    def create(cls, name, **kwargs):
        download_table = PcapDownloadTable.create(name + '-download')
        kwargs['related_tables'] = {'download_table': download_table}
        return super(MSADownloadTable, cls).create(name, **kwargs)

    def post_process_table(self, field_options):
        fields_add_device_selection(self, keyword='netshark_device_src',
                                    label='NetShark Source', module='netshark',
                                    enabled=True)
        fields_add_device_selection(self, keyword='netshark_device_dst',
                                    label='NetShark Dest', module='netshark',
                                    enabled=True)

        fields_add_device_selection(self, keyword='netshark_device_upload',
                                    label='NetShark MSA', module='netshark',
                                    enabled=True)
        TableField.create(
            keyword='netshark_source_name_src',
            label='Source Capture Job',
            obj=self,
            field_cls=forms.ChoiceField,
            field_kwargs={'widget_attrs': {'class': 'form-control'}},
            parent_keywords=['netshark_device_src'],
            dynamic=True,
            pre_process_func=Function(netshark_source_choices,
                                      {'field': 'netshark_device_src'})
        )
        TableField.create(
            keyword='netshark_source_name_dst',
            label='Dest Capture Job',
            obj=self,
            field_cls=forms.ChoiceField,
            field_kwargs={'widget_attrs': {'class': 'form-control'}},
            parent_keywords=['netshark_device_dst'],
            dynamic=True,
            pre_process_func=Function(netshark_source_choices,
                                      {'field': 'netshark_device_dst'})
        )

        fields_add_time_selection(self, show_start=True,
                                  initial_start_time='now-1m',
                                  show_end=True,
                                  show_duration=False)

        fields_add_filterexpr(obj=self)


class MSADownloadQuery(AnalysisQuery):

    def analyze(self, jobs=None):

        download_table = Table.from_ref(
            self.table.options.related_tables['download_table']
        )

        # Create source and destination download jobs
        depjobs = {}

        c = self.job.criteria
        sharks = [
            ('1-source', c.netshark_device_src, c.netshark_source_name_src),
            ('2-dest', c.netshark_device_dst, c.netshark_source_name_dst)
        ]

        for shark in sharks:
            sc = copy.copy(c)
            name, device, source = shark
            sc.netshark_device = device
            sc.netshark_source_name = source
            sc.segment = name

            job = Job.create(table=download_table, criteria=sc,
                             update_progress=True, parent=self.job)
            logger.debug("Created %s: %s download job with criteria %s"
                         % (job, name, sc))
            depjobs[job.id] = job

        return QueryContinue(self.collect, depjobs)

    def collect(self, jobs=None):
        logger.info('%s: MSADownload.collect: %s' % (self, jobs))

        c = self.job.criteria
        s = DeviceManager.get_device(c.netshark_device_upload)

        if self.table.options.msa_folder is None:
            upload_dir = ('/%s/msa-%s' %
                          (s.auth.username,
                           datetime_to_seconds(c.endtime)))
        else:
            upload_dir = self.table.options.msa_folder

        # check upload dir and delete if option set
        try:
            s.create_dir(upload_dir)
        except RvbdHTTPException:
            if self.table.options.overwrite_folder:
                logger.info('MSA Directory %s already created, '
                            'deleting and creating a new one.' % upload_dir)
                d = s.get_dir(upload_dir)
                d.remove()
                s.create_dir(upload_dir)
            else:
                logger.info('MSA Directory %s already created, skipping'
                            % upload_dir)

        # upload pcaps to upload dir, overwriting if needed
        filepaths = []

        for jid, job in jobs.iteritems():
            localfile = job.data()['filename'][0]

            # example naming: "1-source-6-jobs_00001E3"
            fname = '{}-{}-{}'.format(
                job.criteria.segment,
                job.criteria.netshark_device,
                job.criteria.netshark_source_name.replace('/', '_')
            )

            remotefile = os.path.join(upload_dir, fname)
            check_netshark_file(s, remotefile, remove=True)

            logger.info('Uploading new PCAP %s to %s' % (localfile,
                                                         remotefile))
            s.upload_trace_file(remotefile, localfile)

            filepaths.append((remotefile, localfile))

        # create msa from those files
        filepaths.sort()
        flist = [s.get_file(rfile) for rfile, _ in filepaths]

        msafile = os.path.join(upload_dir, 'msa_file.pvt')
        check_netshark_file(s, msafile, remove=True)

        # create the aggregated file and initiate a timeskew calculation
        msa = s.create_multisegment_file(msafile, flist)

        # pick arbitrary number 10,000 for number of pkts
        # to use for timeskew calculation
        msa.calculate_timeskew(10000)

        result = ['<strong>Done</strong> - PCAPs successfully downloaded '
                  'from source NetSharks and uploaded for analysis']
        result.append('')
        for remote, local in filepaths:
            result.append(
                '<strong>Uploaded file path:</strong> %s' % remote
            )
        result.append('')

        config = pprint.pformat(msa.get_info()).splitlines()
        result.append('<strong>MSA file created with config:</strong> '
                      '<br>'
                      '<pre>'
                      '{}'
                      '</pre>'.format('<br>'.join(config)))
        return QueryComplete(['<br>'.join(result)])


class MSATable(NetSharkTable):
    class Meta:
        proxy = True
        app_label = 'steelscript.netshark.appfwk'

    _query_class = 'MSAQuery'

    TABLE_OPTIONS = {'aggregated': False,
                     'include_files': False,
                     'include_interfaces': False,
                     'include_persistent': False,
                     'include_filter': True,       # included by default
                     'include_bpf_filter': False,
                     'show_entire_msa': True,
                     }

    def post_process_table(self, field_options):
        duration = field_options['duration']
        if isinstance(duration, int):
            duration = "{}m".format(duration)

        fields_add_device_selection(self, keyword='netshark_device',
                                    label='NetShark', module='netshark',
                                    enabled=True)

        func = Function(netshark_msa_file_choices,
                        self.options)
        TableField.create(keyword='netshark_source_name', label='Source',
                          obj=self,
                          field_cls=IDChoiceField,
                          field_kwargs={
                              'widget_attrs': {'class': 'form-control'}
                          },
                          parent_keywords=['netshark_device'],
                          dynamic=True,
                          pre_process_func=func)

        fields_add_time_selection(self,
                                  initial_duration=duration,
                                  durations=field_options['durations'])
        fields_add_resolution(self,
                              initial=field_options['resolution'],
                              resolutions=field_options['resolutions'])

        if self.options.include_filter:
            fields_add_filterexpr(self)

        if self.options.include_bpf_filter:
            fields_add_bpf_filterexpr(self)

        if self.options.show_entire_msa:
            TableField.create(keyword='entire_msa', obj=self,
                              field_cls=forms.BooleanField,
                              label='Entire MSA (ignore start/end times)',
                              initial=True,
                              required=False)


class MSAQuery(NetSharkQuery):

    def run(self):
        """Run MSA Table"""
        criteria = self.job.criteria

        # if `entire_msa` option set, change start/end to null values
        if criteria.entire_msa:
            criteria.starttime = None
            criteria.endtime = None

        return super(MSAQuery, self).run()
