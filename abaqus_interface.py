import os
import pickle
import pathlib
import shutil
import subprocess

import numpy as np

from common import TemporaryDirectory


abaqus_python_directory = pathlib.Path(__file__).parent.absolute() / "abaqus_files"


class ABQInterface:
    def __init__(self, abq_command):
        self.abq = abq_command

    def create_empty_odb(self, new_odb_filename, odb_to_copy):
        os.chdir(abaqus_python_directory)
        job = subprocess.Popen(self.abq + ' python create_empty_odb.py ' + str(new_odb_filename) + ' '
                               + str(odb_to_copy),  shell=True)
        job.wait()

    def read_data_from_odb(self, field_id, odb_file_name, step_name=None, frame_number=-1, set_name='',
                           instance_name='', get_position_numbers=False, get_frame_value=False,
                           position='INTEGRATION_POINT'):
        current_directory = os.getcwd()
        with TemporaryDirectory(odb_file_name) as work_directory:
            parameter_pickle_name = work_directory / 'parameter_pickle.pkl'
            results_pickle_name = work_directory / 'results.pkl'
            if step_name is None:
                step_name = ''
            with open(parameter_pickle_name, 'wb') as pickle_file:
                pickle.dump({'field_id': field_id, 'odb_file_name': str(odb_file_name), 'step_name': step_name,
                             'frame_number': frame_number, 'set_name': set_name, 'instance_name': instance_name,
                             'get_position_numbers': get_position_numbers, 'get_frame_value': get_frame_value,
                             'position': position},
                            pickle_file, protocol=2)
            os.chdir(abaqus_python_directory)
            job = subprocess.Popen(self.abq + ' python read_data_from_odb.py ' + str(parameter_pickle_name) + ' '
                                   + str(results_pickle_name), shell=True)
            job.wait()
            os.chdir(current_directory)
            with open(results_pickle_name, 'rb') as results_pickle:
                data = pickle.load(results_pickle, encoding='latin1')

        if not get_position_numbers and not get_frame_value:
            return data['data']
        elif not get_position_numbers:
            return data['data'], data['frame_value']
        elif not get_frame_value:
            return data['data'], data['node_labels'], data['element_labels']
        else:
            return data['data'], data['frame_value'], data['node_labels'], data['element_labels']

    def write_data_to_odb(self, field_data, field_id, odb_file_name, step_name, instance_name='', set_name='',
                          step_description='', frame_number=None, frame_value=None, field_description='',
                          position='INTEGRATION_POINT'):
        current_directory = os.getcwd()
        with TemporaryDirectory(odb_file_name) as work_directory:
            pickle_filename = work_directory / 'load_field_to_odb_pickle.pkl'
            data_filename = work_directory / 'field_data.npy'
            np.save(str(data_filename), field_data)

            with open(pickle_filename, 'wb') as pickle_file:
                pickle.dump({'field_id': field_id, 'odb_file': odb_file_name, 'step_name': step_name,
                             'instance_name': instance_name, 'set_name': set_name, 'step_description': step_description,
                             'frame_number': frame_number, 'frame_value': frame_value,
                             'field_description': field_description, 'position': position},
                            pickle_file, protocol=2)

            os.chdir(abaqus_python_directory)
            job = subprocess.Popen(self.abq + ' python write_data_to_odb.py ' + str(data_filename) + ' '
                                   + str(pickle_filename),
                                   shell=True)
            job.wait()
            os.chdir(current_directory)
            shutil.rmtree(work_directory)


if __name__ == '__main__':
    pass