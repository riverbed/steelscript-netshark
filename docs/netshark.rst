NetShark, Packet Sources and Views
==================================

.. automodule:: steelscript.netshark.core

.. currentmodule:: steelscript.netshark.core

:py:class:`NetShark` Objects
----------------------------

.. autoclass:: NetShark
   :members:

   .. automethod:: __init__

   The following methods provide general information about
   the a NetShark:

   * :py:meth:`.get_serverinfo`
   * :py:meth:`.get_protocol_version`
   * :py:meth:`.get_logininfo`
   * :py:meth:`.get_stats`

   The following methods are used to access :term:`view`.  Each of
   these methods returns a :py:class:`View <View4>`.

   * :py:meth:`.get_open_views`
   * :py:meth:`.get_open_view_by_handle`
   * :py:meth:`.create_view`
   * :py:meth:`.create_view_from_template`

   The following methods are used to access packet sources (e.g., to
   obtain an object that can be used as an argument to
   :py:meth:`create_view`, etc.  The objects they return are
   described below in the section :ref:`packet-source-objects`.

   * :py:meth:`.get_interfaces`
   * :py:meth:`.get_interface_by_name`
   * :py:meth:`.get_capture_jobs`
   * :py:meth:`.get_capture_job_by_name`
   * :py:meth:`.create_job`
   * :py:meth:`.get_clips`
   * :py:meth:`.create_clip`
   * :py:meth:`.get_trace_clip_by_description`
   * :py:meth:`.get_files`

   The following methods are used to work directly with trace files
   on the NetShark appliance filesystem:

   * :py:meth:`.get_dir`
   * :py:meth:`.get_file`
   * :py:meth:`.exists`
   * :py:meth:`.create_dir`
   * :py:meth:`.create_multisegment_file`
   * :py:meth:`.create_merged_file`
   * :py:meth:`.upload_trace_file`

   The following methods are used to access :term:`extractor fields
   <extractor field>`.

   * :py:meth:`.get_extractor_fields`
   * :py:meth:`.find_extractor_field_by_name`
   * :py:meth:`.search_extractor_fields`

   The following method is used to create an export from a source:

   * :py:meth:`.create_export`

   Complete method descriptions:

.. _packet-source-objects:

Packet Source Objects
---------------------

The objects described in this section are used to access packet
sources.  None of these objects are directly instantiated from
external code, they are returned by methods on :py:class:`NetShark` or
other routines.  Any of the objects in this section may be used as the
`src` argument to :py:meth:`NetShark.create_view`.

There are three basic data sources:

* Capture Jobs
* Interfaces
* Trace Clips

.. _capture-job-objects:

Capture Job Objects
~~~~~~~~~~~~~~~~~~~

Capture job objects are used to work with capture jobs.  These objects
are not instantiated directly but are returned from :py:meth:`NetShark.get_capture_jobs`
and :py:meth:`NetShark.get_capture_job_by_name`.

.. note::

   See :py:class:`Job4` if connecting to a NetShark using API 4.0

.. autoclass:: Job5
   :members:
   :undoc-members:
   :inherited-members:
   :show-inheritance:

   Capture job objects have the following properties:

   * :py:attr:`.name`
   * :py:attr:`.size_on_disk`
   * :py:attr:`.size_limit`
   * :py:attr:`.packet_start_time`
   * :py:attr:`.packet_end_time`
   * :py:attr:`.interface`
   * :py:attr:`.handle`
   * :py:attr:`.dpi_enabled`

   The following methods access information about a job:

   * :py:meth:`.get_status`
   * :py:meth:`.get_state`
   * :py:meth:`.get_stats`
   * :py:meth:`.get_index_info`

   The following methods are useful for controlling a capture job:

   * :py:meth:`.start`
   * :py:meth:`.stop`
   * :py:meth:`.clear`

   The following methods can be used to create and delete jobs, though
   :py:meth:`.create` does the same thing as
   :py:meth:`NetShark.create_clip`.

   * :py:meth:`.create`
   * :py:meth:`.delete`

   Finally, these methods are useful for creating trace clips and
   for downloading raw packets from a capture job.

   * :py:meth:`.add_clip`
   * :py:meth:`.download`

   Complete method and property descriptions:

Interface Objects
~~~~~~~~~~~~~~~~~

.. note::

   See :py:class:`Interface4` if connecting to a NetShark using API 4.0

.. autoclass:: Interface5
   :members:
   :undoc-members:
   :inherited-members:
   :show-inheritance:

Trace Clip Objects
~~~~~~~~~~~~~~~~~~
.. note::
   See section :ref:`Trace Clip Objects (v4) <Clip4>` for details.

.. _extractor-fields:

Extractor Fields
----------------

Extractor Field objects represent individual extractor fields.
These objects are returned by :py:meth:`NetShark.get_extractor_fields`,
:py:meth:`NetShark.find_extractor_field_by_name`, and :py:meth:`NetShark.search_extractor_fields`.

Each extractor field is a python
`namedtuple <http://docs.python.org/library/collections.html#collections.namedtuple>`_
with the following fields:

* `name`: the name of the field, e.g., `ip.source_ip`
* `desc`: a brief description of the field
* `type`: a string describing the type of the field
  (e.g., integer, string ip address, etc.)

View Objects
------------

View objects are returned from :py:meth:`NetShark.create_view`.

A View object encapsulates everything needed to read data from an
existing view on a NetShark.  Every view has one or more associated
*outputs*.  For example, the standard "Bandwidth over time" view has
separate outputs for "bits over time", "bytes over time", and "packets
over time".  In SteelScript, a View object contains an associated Output
object for each output.  To read data from a view, you must first
locate the appropriate Output object, then use the method
:py:meth:`Output4.get_data()`.

.. autoclass:: View4
   :members:
   :inherited-members:

Export Objects
--------------

.. autoclass:: Export4
   :members:
   :inherited-members:
   :show-inheritance:

.. _output-objects:

Output Objects
--------------

.. autoclass:: Output4
   :members:
   :inherited-members:
   :show-inheritance:

.. _netshark-filters:

Filters
-------

.. automodule:: steelscript.netshark.core.filters

TimeFilter Objects
~~~~~~~~~~~~~~~~~~

.. autoclass:: TimeFilter
   :members:

   .. automethod:: __init__

NetSharkFilter Objects
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: NetSharkFilter
   :members:

   .. automethod:: __init__

BpfFilter Objects
~~~~~~~~~~~~~~~~~

.. autoclass:: BpfFilter
   :members:

   .. automethod:: __init__

WiresharkDisplayFilter Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: WiresharkDisplayFilter
   :members:

   .. automethod:: __init__


Utilities
---------

.. automodule:: steelscript.netshark.core.viewutils

Utilities for writing view data

.. autofunction:: print_data
.. autofunction:: write_csv


.. autoclass:: OutputMixer
   :members:

   Mixing multiple view outputs
