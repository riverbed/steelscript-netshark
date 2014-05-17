# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.



from steelscript.netshark.core import *
from steelscript.netshark.core.app import NetSharkApp
import time
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-5.5s] %(msg)s")

def test(app):
    t = 60
    while True:
        info = app.shark.get_serverinfo()
        print "%s Success... (sleeping for %s seconds)" % (time.ctime(time.time()), t)
        time.sleep(t)
        t = t * 2

app = NetSharkApp(main_fn = test)
app.run()
