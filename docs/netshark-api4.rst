NetShark API v4.0 classes
=========================

.. currentmodule:: steelscript.netshark.core

This page documents the underlying classes that are used
when connecting to a NetShark via API v4.x.

Capture Job Objects (v4)
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Job4
   :members:
   :undoc-members:
   :inherited-members:

   .. automethod:: __init__

Interface Objects (v4)
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Interface4
   :members:
   :undoc-members:

   .. automethod:: __init__

Trace Clip Objects (v4)
~~~~~~~~~~~~~~~~~~~~~~~

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
