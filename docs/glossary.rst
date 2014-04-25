NetShark Glossary
=================

.. glossary::

   NetShark

      Short for Riverbed SteelCentral NetShark Appliance.  A physical
      appliance or virtual machine that provides continuous, high-speed
      packet capture and includes sophisticated analytics (using the
      concept of a :term:`view` for extracting many different kinds of
      data and statistics from the captured traffic.

   Pilot

      Short for Riverbed Cascade Pilot.  The former name for
      :term:`Packet Analyzer`

   Packet Analyzer

      Short for Riverbed SteelCentral Packet Analyzer.  A desktop
      application for interacting with a :term:`NetShark` appliance.

   view

      The object used within :term:`NetShark` for all packet analysis.
      A view consists of a packet source, optional filters to limit
      which packets are analyzed, and a set of statistics to extract
      along with rules for how to organize those statistics.
      See :doc:`background` for more information.

   extractor

      A software component that can *extract* information (an
      :term:`extractor field`) about some protocol from packets.  Each
      extractor is identified by a short name.  E.g., the ``tcp``
      extractor parses the headers in TCP packets and extracts fields
      such as port numbers, flags, etc.

   extractor field

      An individual piece of information that can be computed by an
      :term:`extractor`.  Each field has a short descriptive
      name and is usually identified by the name of the extractor
      followed by a doubled colon, and the field name.  For example,
      ``tcp::source_port`` or ``http::uri``.

   packet source

      An object used as the input for a :term:`view`.  Can be a
      :term:`capture port`, :term:`capture job`, :term:`trace
      clip`, or trace file.

   capture port

      A physical network interface on a NetShark appliancbe.
      Typically connected to a mirrored (SPAN) port on a switch.

   capture job

      A long-running background task on a NetShark appliance that
      records some or all of the packets arriving on a :term:`capture
      port` to disk.  Recorded packets are stored in an efficient
      indexed structure for efficient retrieval during :term:`view`
      processing.  The term "capture job" is mildly overloaded -- it
      can refer abstractly to the ongoing process of indexing and
      saving packets, or it can refer specifically to the set of
      packets stored on disk as part of a job.

   trace clip

      A filtered subset of the packets that have been stored as part
      of a capture job.  A trace clip typically includes a time-based
      filter to limit the clip to only those packets that fall within
      a specific time interval.  Trace clips may be *locked*, in which
      case the packets in the clip will not be deleted from disk even
      as ongoing capture jobs need to delete old packets to reclaim
      space for new packets.

   filter

      A predicate applied to a stream of packets to select a subset of
      the packets.  Used to limit which packets from a source should
      be processed by a :term:`view` or to limit which packets from a
      :term:`capture job` should be included in a :term:`trace
      clip`.
