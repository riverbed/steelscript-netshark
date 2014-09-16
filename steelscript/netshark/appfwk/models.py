# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import datetime
import pytz

from django.db import models

class NetSharkViews(models.Model):

    netsharkname = models.CharField(max_length=300)
    viewname = models.CharField(max_length=300)
    viewid = models.CharField(max_length=12)

    # Timestamp when the view was last used
    lastused = models.DateTimeField(auto_now_add=True)

    @classmethod
    def find_by_name(cls, netshark, viewname):
        # First see if this is already cached
        nvs = NetSharkViews.objects.filter(
            netsharkname=netshark.host, viewname=viewname)

        if len(nvs) > 0:
            try:
                view = netshark.get_open_view_by_handle(nvs[0].viewid)
                nvs[0].lastused = datetime.datetime.now(tz=pytz.utc)
                nvs[0].save()
                return view
            except KeyError:
                # If the view was not found, may need to refresh, so
                # continue on below
                view = None

        # Delete old views for this netshark
        NetSharkViews.objects.filter(netsharkname=netshark.host).delete()

        # No match, ask the shark for the complete list of views
        views = netshark.get_open_views()

        # Insert those views that have a title
        match = None
        for view in views:
            if ('info' in view.config and
                    'title' in view.config['info'] and
                    view.config['info']['title']):

                title = view.config['info']['title']
                nv = NetSharkViews(netsharkname=netshark.host,
                                   viewname=title,
                                   viewid = view.handle)
                nv.save()
                if title == viewname:
                    match = view

        return match
