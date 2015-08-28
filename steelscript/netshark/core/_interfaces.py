# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import functools
import logging
import time

from steelscript.common.datastructures import DictObject
from steelscript.common.timeutils import datetime_to_seconds
from steelscript.common.exceptions import RvbdHTTPException

logger = logging.getLogger(__name__)


class NetSharkExportException(Exception):
    pass


def loaded(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwds):
        self._ensure_loaded()
        return f(self, *args, **kwds)
    return wrapper


class _InputSource(object):
    def __init__(self, shark, data, api):
        self.shark = shark
        self.id = data['id']
        self.data = data
        self._api = api

    @classmethod
    def get(cls, shark, id, name=None):
        for source in cls.get_all(shark):
            if (id and (source.id == id) or
                    name and (source.data['config']['name'] == name)):
                return source
        return None

    def update(self, data):
        """Update the data of the current object
        with new data from the server
        """
        assert self.id == data['id']
        self.data = DictObject.create_from_dict(data)


class Clip(_InputSource):

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.delete()

    def is_live(self):
        """Can be used to determine if a source object is live or offline.
        The result is always False for a TraceClip."""
        return False

class View(object):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @classmethod
    def _get_all(cls, shark):
        return shark.api.view.get_all()

    def _ensure_output(self):
        if len(self._outputs) == 0:
            # change this since postapply doesn't load
            # the view parameters
            self._postapply()

    @classmethod
    def _process_view(cls, view, source, sync):
        if sync:
            try:
                if not source.is_live():
                    view._poll_completion()
                view._postapply()
            except:
                view.close()
                raise

        return view

    def get_iterdata(self, *args, **kwargs):
        """ Returns an iterator for the data from the output
        in this view.  Shorthand for `all_outputs()[0].get_iterdata()`.

        Raises a LookupError if the view has more than one output.

        For a full description of the function arguments, refer to the
        method Output.get_iterdata()
        """
        outputs = self.all_outputs()
        if len(outputs) != 1:
            raise LookupError('This view has more than one output. You have to call get_iterdata'
                              'on an Output object directly')
        return outputs[0].get_iterdata(*args, **kwargs)

    def get_data(self, *args, **kwargs):
        """ Returns the data from the output in this view.
        Shorthand for `all_outputs()[0].get_data()`.

        Raises a LookupError if the view has more than one output.

        For a full description of the function arguments, refer to the
        method Output.get_data().
        """
        outputs = self.all_outputs()
        if len(outputs) != 1:
            raise LookupError('This view has more than one output. You have to call get_data'
                              'on an Output object directly')

        return outputs[0].get_data(*args, **kwargs)

    def get_legend(self):
        """ Returns the legend from the output in this view.
        Shorthand for `all_outputs()[0].get_legend()`.

        Raises a LookupError if the view has more than one output.
        """
        outputs = self.all_outputs()
        if len(outputs) != 1:
            raise LookupError('This view has more than one output. You have to call get_legend'
                              'on an Output object directly')

        return outputs[0].get_legend()

    def all_outputs(self):
        """ Return a list of Output objects, one for each output
        in this view """
        self._ensure_output()
        return self._outputs.values()

    def get_output(self, id):
        """ Return the Output object corresponding to
        the output ``id``.
        """
        self._ensure_output()
        return self._outputs[id]

class Output(object):
    def get_data(self, start=None, end=None, delta=None,
                 aggregated=False,
                 sortby=None, sorttype="descending",
                 fromentry=0, toentry=0,):
        """
        Get the data for this view. This function downloads the whole
        dataset before returning it, so it's useful when random access to the
        view data is necessary.

        The arguments have the same meanings as corresponding arguments
        to get_iterdata(), see its documentation for a full explanation
        of all arguments and their meanings.
        """
        it = self.get_iterdata(start, end, delta, aggregated,
                               sortby, sorttype, fromentry, toentry)
        data = list()
        for row in it:
            data.append(row)
        return data

class File(_InputSource):
    """A file packet source. A file can be in one of the several
       formats that NetShark supports, e.g. pcap, pcapNG or ERF. Files are
       usually created using the "send to file" feature in Pilot, but they can
       also be uploaded into the appliance using the netshark.upload() method.
       TraceClip objects are normally not instantianted directly, but are
       instead obtained by calling
       :py:func:`steelscript.netshark.core.netshark.NetShark.get_files` or
       :py:func:`CaptureJob.get_file`."""

    def is_live(self):
        """Can be used to determine if a source object is live or offline.
        The result is always False for a File."""
        return False


class Job(_InputSource):
    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        self.delete()


class Export(object):
    """A pcap export object.

    Export objects are not instantiated directly, but are instead
    obtained by calling
    :py:func:`steelscript.netshark.core.netshark.NetShark.create_export`

    """

    def __init__(self, shark, id, source):
        self.shark = shark
        self.id = id
        self.source = source

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.delete()

    @classmethod
    def create(cls, shark, source, timefilter, filters=None,
               wait_for_data=False, wait_duration=10):
        """Create a new pcap export from the given source."""
        config = {
            'output_format': 'PCAP_US',
            'start_time': datetime_to_seconds(timefilter.start),
            'end_time': datetime_to_seconds(timefilter.end)
            }

        if filters:
            config['filters'] = [filt.bind(shark) for filt in filters]

        r = None
        cnt = 0
        while r is None and cnt < 3:
            try:
                r = source._api.create_export(source.id, config=config)
            except RvbdHTTPException, e:
                if 'job is empty' in str(e) and wait_for_data:
                    logger.warning("Data is not available to export,"
                                   " waiting for %s seconds" % wait_duration)
                    time.sleep(wait_duration)
                    cnt += 1
                    continue
                else:
                    raise NetSharkExportException(str(e))

        if r is None:
            raise NetSharkExportException("Data is not available to export,"
                                          " need to wait longer or "
                                          " ensure the job id is correct")

        return cls(shark, r['id'], source)

    def details(self):
        """Return details about an export."""
        return self.source._api.get_export_details(self.source.id, self.id)

    def download(self, filename, overwrite=False):
        """Download the packets as a pcapfile to a local file."""
        if self.details()['status']['state'] != 'RUNNING':
            return False

        self.source._api.get_packets_from_export(self.source.id, self.id,
                                                 filename, overwrite=overwrite)
        return True

    def delete(self):
        """Delete the export on the shark.

        Note that downloading an export automatically deletes the export.
        """
        try:
            self.source._api.delete_export(self.source.id, self.id)
        except:
            # Export probably no longer exists
            pass
