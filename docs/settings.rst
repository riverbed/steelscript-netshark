
System Settings
---------------

This page describes the classes and methods to read, modify and update
the system.

Settings classes are not instantiated directly, but instead are
accessed via a :py:class:`NetShark
<steelscript.netshark.core.NetShark>` instance.  The following
table lists the available settings related classes and the
accessor name:

=================== ============================== ================================ ============
Settings            Class                          Accessor Attribute               API Versions
=================== ============================== ================================ ============
Basic               :py:class:`Basic`              `ns.settings.basic`              v4.x, v5.x
Auth                :py:class:`Auth`               `ns.settings.auth`               v4.x, v5.x
Audit               :py:class:`Audit`              `ns.settings.audit`              v4.x, v5.x
Licenses            :py:class:`Licenses`           `ns.settings.licenses`           v4.x, v5.x
Firewall            :py:class:`Firewall`           `ns.settings.firewall`           v4.x, v5.x
Certificates        :py:class:`Certificates`       `ns.settings.certificates`       v4.x, v5.x
Profiler Export     :py:class:`ProfilerExport`     `ns.settings.profiler_export`    v4.x, v5.x
CORS Domain         :py:class:`CorsDomain`         `ns.settings.cors_domain`        v4.x, v5.x
Users               :py:class:`Users`              `ns.settings.users`              v4.x, v5.x
Groups              :py:class:`Groups`             `ns.settings.groups`             v4.x, v5.x
Update              :py:class:`Update`             `ns.settings.update`             v4.x, v5.x
Storage             :py:class:`Storage`            `ns.settings.storage`            v4.x, v5.x
Port Definitions    :py:class:`Port Definitions`   `ns.settings.port_definitions`   v5.x
Port Groups         :py:class:`Port Groups`        `ns.settings.port_groups`        v5.x
Layer 4 Mappings    :py:class:`L4Mapping`          `ns.settings.l4_mappings`        v5.x
Custom Applications :py:class:`CustomApplications` `ns.settings.custom_application` v5.x
Alerts              :py:class:`Alerts`             `ns.settings.alerts`             v5.x
=================== ============================== ================================ ============

For example, modifying basic settings can be accomplished as follows:

.. code-block:: python

   >>> ns = NetShark(...)
   >>> basic = ns.settings.basic
   >>> basic.get()
   >>> basic.data['primary_dns'] = '10.1.2.3'
   >>> basic.save()

Base Classes
^^^^^^^^^^^^
.. currentmodule:: steelscript.netshark.core._settings4

.. autoclass:: BasicSettingsFunctionality
   :members:

.. autoclass:: NoBulk

Basic Settings
^^^^^^^^^^^^^^

.. autoclass:: Basic
   :members:
   :show-inheritance:


Auth Settings
^^^^^^^^^^^^^

.. autoclass:: Auth
   :members:
   :show-inheritance:

Audit Settings
^^^^^^^^^^^^^^

.. autoclass:: Audit
   :members:
   :show-inheritance:

Licenses
^^^^^^^^

.. autoclass:: Licenses
   :members:
   :show-inheritance:

Firewall
^^^^^^^^

.. autoclass:: Firewall
   :members:
   :show-inheritance:

Certificates Settings
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Certificates
   :members:
   :show-inheritance:

ProfilerExport Settings
^^^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: steelscript.netshark.core._settings5
.. autoclass:: ProfilerExport
   :members:
   :show-inheritance:

CorsDomain Settings
^^^^^^^^^^^^^^^^^^^

.. currentmodule:: steelscript.netshark.core._settings4
.. autoclass:: CorsDomain
   :members:
   :show-inheritance:

Users Settings
^^^^^^^^^^^^^^

.. autoclass:: Users
   :members:
   :show-inheritance:

Groups Settings
^^^^^^^^^^^^^^^

.. autoclass:: Groups
   :members:
   :show-inheritance:

Update Settings
^^^^^^^^^^^^^^^

.. autoclass:: Update
   :members:
   :show-inheritance:

Storage Settings
^^^^^^^^^^^^^^^^

.. autoclass:: Storage
   :members:
   :show-inheritance:

.. currentmodule:: steelscript.netshark.core._settings5

Port Definitions
^^^^^^^^^^^^^^^^

.. versionadded:: API 5.x
.. autoclass:: PortDefinitions
   :members:
   :show-inheritance:

Port Group Definitions
^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: API 5.x
.. autoclass:: PortGroups
   :members:
   :show-inheritance:

Layer 4 Port Mappings
^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: API 5.x
.. autoclass:: L4Mapping
   :members:
   :show-inheritance:

Custom Applications
^^^^^^^^^^^^^^^^^^^

.. versionadded:: API 5.x
.. autoclass:: CustomApplications
   :members:
   :show-inheritance:

Alerts
^^^^^^

.. versionadded:: API 5.x
.. autoclass:: Alerts
   :members:
   :show-inheritance:
