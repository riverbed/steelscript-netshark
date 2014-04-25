:py:mod:`steelscript.netshark.core`
===================================

.. currentmodule:: steelscript.netshark.core.netshark

This documentation assumes you are already familiar with the NetShark
Appliance, specifically concepts like Capture Jobs and Views.  If you
are not already familiar with these concepts, see :doc:`background`
and the `NetShark documentation
<https://support.riverbed.com/content/support/software/cascade/shark.html>`_
on the support site.

The primary interface to the NetShark related SteelScript
functionality is the class :py:class:`NetShark`.  An instance of
this object represents a connection to a NetShark server, and can be used
to examine packet sources and existing views on the server, as well as
to configure and create new views, capture jobs, etc.

There are many more classes in the NetShark libraries, representing
things like views, capture jobs, trace clips, etc.  But these should
never be instantiated directly from scripts, they are returned by
methods on NetShark objects.

If you are new to SteelScript for NetShark, see the :doc:`Tutorial <tutorial>`.

The :doc:`glossary` defines terms like View and Capture Job.

:py:class:`NetShark` Objects
----------------------------

.. autoclass:: steelscript.netshark.core.netshark.NetShark
   :members:

   .. automethod:: __init__

   The following methods provide general information about
   the a NetShark:

   * :py:meth:`.get_serverinfo`
   * :py:meth:`.get_protocol_version`
   * :py:meth:`.get_logininfo`
   * :py:meth:`.get_stats`

   The following methods are used to access [views](glossary.html#view).
   Each of these methods returns a [view object](#viewobjects).

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

   Complete method descriptions:

.. _packet-source-objects:

Packet Source Objects
---------------------

The objects described in this section are used to access packet
sources.  None of these objects are directly instantiated from
external code, they are returned by methods on :py:class:`NetShark` or
other routines.  Any of the objects in this section may be used as the
`src` argument to :py:meth:`NetShark.create_view`.

:py:class:`Job4` (Capture Job) Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Capture job objects are used to work with capture jobs.  These objects
are not instantiated directly but are returned from :py:meth:`NetShark.get_capture_jobs`
and :py:meth:`NetShark.get_capture_job_by_name`.

.. autoclass:: steelscript.netshark.core._source4.Job4
   :members:

   Capture job objects have the following properties:

   * :py:attr:`.name`
   * :py:attr:`.size_on_disk`
   * :py:attr:`.size_limit`
   * :py:attr:`.packet_start_time`
   * :py:attr:`.packet_end_time`
   * :py:attr:`.interface`
   * :py:attr:`.handle`

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

.. currentmodule:: steelscript.netshark.core._source4

:py:class:`Job5` (Capture Job) Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: steelscript.netshark.core._source5.Job5
   :members:
   :undoc-members:
   :inherited-members:

   .. automethod:: __init__

:py:class:`Clip4` (Trace Clip) Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Trace clip objects are used to work with trace clips.
These objects are not instantiated directly but are returned from
methods such as :py:meth:`NetShark.get_clips`.

.. autoclass:: Clip4
   :members:

   .. automethod:: __init__

   Trace clip objects have the following properties:

   * :py:meth:`.description`
   * :py:meth:`.size`

   * :py:meth:`.add`
   * :py:meth:`.delete`
   * :py:meth:`.download`

   These methods provide a way to obtain clip objects, though it
   is usually easier to use methods like `NetShark.get_clips`.

   * :py:meth:`.get`
   * :py:meth:`.get_all`

   Complete method and property descriptions:

Extractor Field objects
-----------------------

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

:py:class:`View4` (View) Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

View objects are returned from :py:meth:`NetShark.create_view`.

A View object encapsulates everything needed to read data from an
existing view on a NetShark.  Every view has one or more associated
*outputs*.  For example, the standard "Bandwidth over time" view has
separate outputs for "bits over time", "bytes over time", and "packets
over time".  In flyscript, a View object contains an associated Output
object for each output.  To read data from a view, you must first
locate the appropriate Output object, then use the method
:py:meth:`Output4.get_date `steelscript.netshark.core._view4.Output4.get_data>`.

.. autoclass:: steelscript.netshark.core._view4.View4
   :members:

:py:class:`Output4` (Output) Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: steelscript.netshark.core._view4.Output4
   :members:


.. currentmodule:: steelscript.netshark.core

:py:mod:`steelscript.netshark.viewutils`
----------------------------------------

.. automodule:: steelscript.netshark.core.viewutils

Utilities for writing view data

.. autofunction:: print_data
.. autofunction:: write_csv


.. autoclass:: OutputMixer
   :members:

   Mixing multiple view outputs
