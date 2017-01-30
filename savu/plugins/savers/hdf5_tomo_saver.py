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
.. module:: hdf5_tomo_saver
   :platform: Unix
   :synopsis: A class to save data to a hdf5 output file.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""


import logging
import os
import copy
import h5py

from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils
from savu.plugins.base_saver import BaseSaver
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.data.chunking import Chunking


@register_plugin
class Hdf5TomoSaver(BaseSaver, CpuPlugin):
    """
    A class to save tomography data to a hdf5 file
    """

    def __init__(self, name='Hdf5TomoSaver'):
        super(Hdf5TomoSaver, self).__init__(name)
        self.in_data = None
        self.out_data = None
        self.fdict = {}

    def pre_process(self):
        # Create the hdf5 output file
        self.hdf5 = Hdf5Utils(self.exp)
        self.in_data = self.get_in_datasets()[0]
        name = self.in_data.get_name()
        current_pattern = self.__set_pattern(name)
        pattern_idx = {'current': current_pattern, 'next': []}

        self.__set_file_info(name)
        logging.debug("creating the backing file %s", self.fdict['fname'])
        backing_file = self.hdf5._open_backing_h5(self.fdict['fname'], 'w')
        self.fdict['bfile'] = backing_file

        group = backing_file.create_group(self.fdict['gname'])
        group.attrs['NX_class'] = 'NXdata'
        group.attrs['signal'] = 'data'
        self.exp._barrier()
        shape = self.in_data.get_shape()
        chunking = Chunking(self.exp, pattern_idx)
        dtype = self.in_data.data.dtype
        chunks = chunking._calculate_chunking(shape, dtype)
        self.exp._barrier()
        self.out_data = \
            group.create_dataset("data", shape, dtype, chunks=chunks)

    def process_frames(self, data):
        self.out_data[self.get_current_slice_list()[0]] = data[0]

    def post_process(self):
        self.__link_datafile_to_nexus_file()
        self.fdict['bfile'].close()

    def __set_pattern(self, name):
        pattern = copy.deepcopy(self.in_data._get_plugin_data().get_pattern())
        pattern[pattern.keys()[0]]['max_frames'] = self.get_max_frames()
        return pattern

    def __set_file_info(self, name):
        nPlugin = self.exp.meta_data.get('nPlugin')
        plugin_dict = \
            self.exp._get_experiment_collection()['plugin_dict'][nPlugin]
        fname = name + '_p' + str(nPlugin) + '_' + \
            plugin_dict['id'].split('.')[-1] + '.h5'
        out_path = self.exp.meta_data.get('out_path')
        fname = os.path.join(out_path, fname)
        gname = "%i-%s-%s_%s" % (nPlugin, plugin_dict['name'], fname, name)
        self.fdict = {'fname': fname, 'gname': gname, 'name': name}

    def __link_datafile_to_nexus_file(self):
        nxs_file = self.exp.nxs_file
        nxs_entry = '/entry/final_result_' + self.fdict['name']
        nxs_entry = nxs_file[nxs_entry]
        nxs_entry.attrs['signal'] = 'data'
        data_entry = nxs_entry.name + '/data'
        h5file = self.fdict['fname'].split('/')[-1]
        nxs_file[data_entry] = \
            h5py.ExternalLink(h5file, self.fdict['gname'] + '/data')
