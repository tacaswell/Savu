# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: tomo_recon
   :platform: Unix
   :synopsis: runner for tests using the MPI framework

.. moduleauthor:: Nicola Wadespm <scientificsoftware@diamond.ac.uk>

"""

import unittest
import tempfile
from savu.test import test_utils as tu

from savu.test.framework_tests.plugin_runner_test \
    import run_protected_plugin_runner
from savu.test.framework_tests.plugin_runner_test \
    import run_protected_plugin_runner_no_process_list


class MultipleDatasetsTest(unittest.TestCase):

    def test_mm(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('mm.nxs'),
            "process_file": tu.get_test_process_path(
                'multiple_mm_inputs_test.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)

    def test_tomo1(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.test_plugin'
        loader_dict = {'data_path': '1-TimeseriesFieldCorrections-tomo/data'}
        data_dict = {'in_datasets': ['tomo', 'tomo'], 'out_datasets': ['test']}
        saver_dict = {}
        all_dicts = [loader_dict, data_dict, saver_dict]
        run_protected_plugin_runner_no_process_list(options, plugin,
                                                    data=all_dicts)

    @unittest.skip("Running locally, breaking remotely: To be investigated")
    def test_tomo2(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.test_plugin'
        preview = ['10:-1:1:1', '10:-1:1:1', '10:-1:1:1']
        loader_dict = {'data_path': '1-TimeseriesFieldCorrections-tomo/data',
                       'preview': preview}
        data_dict = {'in_datasets': ['tomo', 'tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (81, 125, 150))

    @unittest.skip("Running locally, breaking remotely: To be investigated")
    def test_tomo3(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.test_plugin'
        preview = ['10:-1:10:1', '10:-1:10:1', '10:-1:10:1']
        loader_dict = {'data_path': '1-TimeseriesFieldCorrections-tomo/data',
                       'preview': preview}
        data_dict = {'in_datasets': ['tomo', 'tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        exp = self.assertEqual(exp.index['in_data']['test'].get_shape(),
                               (9, 13, 15))

    @unittest.skip("Running locally, breaking remotely: To be investigated")
    def test_tomo4(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.test_plugin'
        preview = ['10:-10:10:1', '10:-10:10:1', '10:-10:10:1']
        loader_dict = {'data_path': '1-TimeseriesFieldCorrections-tomo/data',
                       'preview': preview}
        data_dict = {'in_datasets': ['tomo', 'tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        exp = self.assertEqual(exp.index['in_data']['test'].get_shape(),
                               (8, 12, 15))

if __name__ == "__main__":
    unittest.main()