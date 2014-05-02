SteelScript NetShark
====================

.. currentmodule:: steelscript.netshark.core

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

Documentation available in this module:

* :doc:`background`
* :doc:`tutorial`
* Class Reference

  * :doc:`netshark`
  * :doc:`netshark-api4`
  * :doc:`settings`

* :doc:`glossary`

API Versions
------------

This code base supports multiple API versions.  It can connect
with systems that support either v4.x or v5.x.  The API version is
automatically detected when connecting to a NetShark and the
appropriate underlying API classes are used.  Once establishing a
connection, the detected version can be retrieved by calling
:py:meth:`NetShark.get_protocol_version()`.

The NetShark object will automatically instantiate sub-objects of
the appropriate version:

============= ==================================== ===================================
Object        v4.x                                 v5.x
============= ==================================== ===================================
Capture Job   :py:class:`Job4 <Job4>`              :py:class:`Job5 <Job5>`
Interface     :py:class:`Interface4 <Interface4>`  :py:class:`Interface5 <Interface5>`
Trace Clip    :py:class:`Clip4 <Clip4>`            :py:class:`Clip4 <Clip4>`
View          :py:class:`View4 <View4>`            :py:class:`View4 <View4>`
Output        :py:class:`Output4 <Output4>`        :py:class:`Output4 <Output4>`
============= ==================================== ===================================

Note that in some cases (such as View objects), the underlying class
did not change from v4.x to v5.x and as such the v4.x class is
used even in v5.x
