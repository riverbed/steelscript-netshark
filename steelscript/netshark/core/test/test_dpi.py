# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import tempfile
import common
import testscenarios

class Dpi(common.SetUpTearDownMixin, testscenarios.TestWithScenarios):
    scenarios = common.config.get('5.0')

    def test_job_dpi(self):
        job = common.setup_capture_job(self.shark)
        columns, filters = common.setup_defaults()
        job.dpi_enabled = True
        job.save()

        job2 = self.shark.get_capture_job_by_name(job.name)
        self.assertEqual(job.dpi_enabled, True)


    def test_port_definitions(self):
        pd = self.shark.settings.port_definitions
        settings = pd.get()
        self.assertNotEqual(pd.data, None)

        try:
            pd.remove('steelscript', 65345)
        except ValueError:
            #it's all good, we don't have the rule in the server
            pass

        pd.add('steelscript', 65345, 'tcp', True)
        pd.save()

        pd.remove('steelscript', 65345)
        pd.save()

        self.assertEqual(settings, pd.get())

    def test_port_groups(self):
        gd = self.shark.settings.port_groups
        settings = gd.get()

        try:
            gd.remove('steelscript')
        except ValueError:
            #it's all good, no rule on server
            pass

        gd.add('steelscript', '1,2,3-80', priority=2)
        gd.save()

        gd.remove('steelscript')
        gd.save()

        self.assertEqual(settings, gd.get())

    def test_custom_applications(self):
        ca = self.shark.settings.custom_applications
        settings = ca.get()

        try:
            ca.remove('steelscript')
        except ValueError:
            #it's all good, no rule on server
            pass

        ca.add('steelscript', 'http://test.com')
        ca.save()

        ca.remove('steelscript')
        ca.save()

        self.assertEqual(settings, ca.get())


    def test_download_upload_port_definitions(self):
        pd = self.shark.settings.port_definitions
        settings = pd.get()
        with tempfile.NamedTemporaryFile() as f:
            pd.download(f.name)
            f.flush()
            f.seek(0)
            pd.load(f.name)
        self.assertEqual(settings, pd.get(force=True))
