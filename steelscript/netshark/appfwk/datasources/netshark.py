# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import time
import logging
import hashlib
import threading

from django import forms

from steelscript.netshark.core.types import Operation, Value, Key
from steelscript.netshark.core.filters import NetSharkFilter, TimeFilter, \
    BpfFilter
from steelscript.netshark.core._class_mapping import path_to_class
from steelscript.netshark.appfwk.models import NetSharkViews

from steelscript.common.timeutils import (parse_timedelta,
                                          timedelta_total_seconds,
                                          datetime_to_nanoseconds,
                                          datetime_to_microseconds)

from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.apps.datasource.models import \
    Column, TableField, DatasourceTable, TableQueryBase
from steelscript.appfwk.apps.datasource.forms import \
    fields_add_time_selection, fields_add_resolution
from steelscript.appfwk.libs.fields import Function
from steelscript.appfwk.apps.datasource.forms import IDChoiceField
from steelscript.appfwk.apps.jobs import QueryComplete

logger = logging.getLogger(__name__)
lock = threading.Lock()


def setup_capture_job(netshark, name, size=None):
    """ Reference function to initialize new capture job. """
    if size is None:
        size = '10%'

    try:
        job = netshark.get_capture_job_by_name(name)
    except ValueError:
        # create a capture job on the first available interface
        interface = netshark.get_interfaces()[0]
        job = netshark.create_job(interface, name, size,
                                  indexing_size_limit='2GB',
                                  start_immediately=True)
    return job


def netshark_source_name_choices(form, id, field_kwargs, params):
    """ Query netshark for available capture jobs / trace clips. """
    netshark_device = form.get_field_value('netshark_device', id)
    if netshark_device == '':
        choices = [('', '<No netshark device>')]
    else:
        netshark = DeviceManager.get_device(netshark_device)

        choices = []

        for job in netshark.get_capture_jobs():
            choices.append((job.source_path, job.name))

        for clip in netshark.get_clips():
            choices.append((clip.source_path, 'Clip: ' + clip.description))

        if params['include_files']:
            for f in netshark.get_files():
                choices.append((f.source_path, 'File: ' + f.path))

        if params['include_interfaces']:
            for iface in netshark.get_interfaces():
                choices.append((iface.source_path, 'If: ' + iface.description))

    field_kwargs['label'] = 'Source'
    field_kwargs['choices'] = choices


class NetSharkColumn(Column):
    class Meta:
        proxy = True

    COLUMN_OPTIONS = {'extractor': None,
                      'operation': None,
                      'default_value': None}


def fields_add_filterexpr(table, keyword='netshark_filterexpr',
                          initial=None):
    field = TableField(keyword=keyword,
                       label='NetShark Filter Expression',
                       help_text='Traffic expression using '
                                 'NetShark filter syntax',
                       initial=initial,
                       required=False)
    field.save()
    table.fields.add(field)


def fields_add_bpf_filterexpr(table, keyword='netshark_bpf_filterexpr',
                              initial=None):
    field = TableField(keyword=keyword,
                       label='NetShark BPF Filter Expression',
                       help_text='Traffic expression using '
                                 'BPF filter syntax',
                       initial=initial,
                       required=False)
    field.save()
    table.fields.add(field)


class NetSharkTable(DatasourceTable):
    class Meta:
        proxy = True

    _column_class = 'NetSharkColumn'
    _query_class = 'NetSharkQuery'

    TABLE_OPTIONS = {'aggregated': False,
                     'include_files': False,
                     'include_interfaces': False,
                     'include_persistent': False,
                     'include_filter': True,       # included by default
                     'include_bpf_filter': False,
                     }

    FIELD_OPTIONS = {'duration': '1m',
                     'durations': ('1m', '15m'),
                     'resolution': '1s',
                     'resolutions': ('1s', '1m'),
                     }

    def post_process_table(self, field_options):
        duration = field_options['duration']
        if isinstance(duration, int):
            duration = "%dm" % duration

        fields_add_device_selection(self, keyword='netshark_device',
                                    label='NetShark', module='netshark',
                                    enabled=True)

        func = Function(netshark_source_name_choices,
                        self.options)
        TableField.create(keyword='netshark_source_name', label='Source',
                          obj=self,
                          field_cls=IDChoiceField,
                          parent_keywords=['netshark_device'],
                          dynamic=True,
                          pre_process_func=func)

        if self.options.include_persistent:
            TableField.create(keyword='netshark_persistent',
                              label='Persistent View', obj=self,
                              field_cls=forms.BooleanField,
                              initial=False)

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


class NetSharkQuery(TableQueryBase):

    def run(self):
        """ Main execution method
        """
        criteria = self.job.criteria

        self.timeseries = False       # if key column called 'time' is created
        self.column_names = []

        # Resolution comes in as a time_delta
        resolution = timedelta_total_seconds(criteria.resolution)

        default_delta = 1000000000                      # one second
        self.delta = int(default_delta * resolution)    # sample size interval

        if criteria.netshark_device == '':
            logger.debug('%s: No netshark device selected' % self.table)
            self.job.mark_error("No NetShark Device Selected")
            return False

        shark = DeviceManager.get_device(criteria.netshark_device)

        logger.debug("Creating columns for NetShark table %d" % self.table.id)

        # Create Key/Value Columns
        columns = []
        for tc in self.table.get_columns(synthetic=False):
            tc_options = tc.options
            if (tc.iskey and tc.name == 'time' and
                    tc_options.extractor == 'sample_time'):
                # don't create column, use the sample time for timeseries
                self.timeseries = True
                self.column_names.append('time')
                continue
            elif tc.iskey:
                c = Key(tc_options.extractor,
                        description=tc.label,
                        default_value=tc_options.default_value)
            else:
                if tc_options.operation:
                    try:
                        operation = getattr(Operation, tc_options.operation)
                    except AttributeError:
                        operation = Operation.sum
                        print ('ERROR: Unknown operation attribute '
                               '%s for column %s.' %
                               (tc_options.operation, tc.name))
                else:
                    operation = Operation.none

                c = Value(tc_options.extractor,
                          operation,
                          description=tc.label,
                          default_value=tc_options.default_value)

            self.column_names.append(tc.name)
            columns.append(c)

        # Identify Sort Column
        sortidx = None
        if self.table.sortcols is not None:
            sortcol = Column.objects.get(table=self.table,
                                         name=self.table.sortcols[0])
            sort_name = sortcol.options.extractor
            for i, c in enumerate(columns):
                if c.field == sort_name:
                    sortidx = i
                    break

        # Initialize filters
        criteria = self.job.criteria

        filters = []

        if hasattr(criteria, 'netshark_filterexpr'):
            logger.debug('calculating netshark filter expression ...')
            filterexpr = self.job.combine_filterexprs(
                exprs=criteria.netshark_filterexpr,
                joinstr="&"
            )
            if filterexpr:
                logger.debug('applying netshark filter expression: %s'
                             % filterexpr)
                filters.append(NetSharkFilter(filterexpr))

        if hasattr(criteria, 'netshark_bpf_filterexpr'):
            # TODO evaluate how to combine multiple BPF filters
            # this will just apply one at a time
            filterexpr = criteria.netshark_bpf_filterexpr
            logger.debug('applying netshark BPF filter expression: %s'
                         % filterexpr)
            filters.append(BpfFilter(filterexpr))

        resolution = criteria.resolution
        if resolution.seconds == 1:
            sampling_time_msec = 1000
        elif resolution.microseconds == 1000:
            sampling_time_msec = 1
            if criteria.duration > parse_timedelta('1s'):
                msg = ("Cannot run a millisecond report with a duration "
                       "longer than 1 second")
                raise ValueError(msg)
        else:
            sampling_time_msec = 1000

        # Get source type from options
        logger.debug("NetShark Source: %s" %
                     self.job.criteria.netshark_source_name)

        source = path_to_class(
            shark, self.job.criteria.netshark_source_name)
        live = source.is_live()
        persistent = criteria.get('netshark_persistent', False)

        if live and not persistent:
            raise ValueError("Live views must be run with persistent set")

        view = None
        if persistent:
            # First, see a view by this title already exists
            # Title is the table name plus a criteria hash including
            # all criteria *except* the timeframe
            h = hashlib.md5()
            h.update('.'.join([c.name for c in
                               self.table.get_columns()]))
            for k, v in criteria.iteritems():
                if criteria.is_timeframe_key(k):
                    continue
                h.update('%s:%s' % (k, v))

            title = '/'.join(['steelscript-appfwk', str(self.table.id),
                              self.table.namespace, self.table.name,
                              h.hexdigest()])
            view = NetSharkViews.find_by_name(shark, title)
            logger.debug("Persistent view title: %s" % title)
        else:
            # Only assign a title for persistent views
            title = None

        if not view:
            # Not persistent, or not yet created...

            if not live:
                # Cannot attach time filter to a live view,
                # it will be added later at get_data() time
                tf = TimeFilter(start=criteria.starttime,
                                end=criteria.endtime)
                filters.append(tf)

                logger.info("Setting netshark table %d timeframe to %s" %
                            (self.table.id, str(tf)))

            # Create it
            with lock:
                logger.debug("%s: Creating view for table %s" %
                             (str(self), str(self.table)))
                view = shark.create_view(
                    source, columns, filters=filters, sync=False,
                    name=title, sampling_time_msec=sampling_time_msec)

            if not live:
                done = False
                logger.debug("Waiting for netshark table %d to complete" %
                             self.table.id)
                while not done:
                    time.sleep(0.5)
                    with lock:
                        s = view.get_progress()
                        self.job.mark_progress(s)
                        self.job.save()
                        done = view.is_ready()

        logger.debug("Retrieving data for timeframe: %s - %s" %
                     (datetime_to_nanoseconds(criteria.starttime),
                      datetime_to_nanoseconds(criteria.endtime)))

        # Retrieve the data
        with lock:
            getdata_kwargs = {}
            if sortidx:
                getdata_kwargs['sortby'] = sortidx

            if self.table.options.aggregated:
                getdata_kwargs['aggregated'] = self.table.options.aggregated
            else:
                getdata_kwargs['delta'] = self.delta

            if live:
                # For live views, attach the time frame to the get_data()
                getdata_kwargs['start'] = (
                    datetime_to_nanoseconds(criteria.starttime))
                getdata_kwargs['end'] = (
                    datetime_to_nanoseconds(criteria.endtime))

            self.data = view.get_data(**getdata_kwargs)

            if not persistent:
                view.close()

        if self.table.rows > 0:
            self.data = self.data[:self.table.rows]

        self.parse_data()

        logger.info("NetShark Report %s returned %s rows" %
                    (self.job, len(self.data)))

        return QueryComplete(self.data)

    def parse_data(self):
        """Reformat netshark data results to be uniform tabular format."""
        out = []
        if self.timeseries:
            # use sample times for each row
            for d in self.data:
                if d['t'] is not None:
                    t = datetime_to_microseconds(d['t']) / float(10 ** 6)
                    out.extend([t] + x for x in d['vals'])

        else:
            for d in self.data:
                out.extend(x for x in d['vals'])

        self.data = out
