import os
import pickle
import pathlib
import subprocess

import numpy as np

from .common import TemporaryDirectory


abaqus_python_directory = pathlib.Path(__file__).parent.absolute() / "abaqus_files"


class ABQInterface:
    def __init__(self, abq_command, shell=None):
        self.abq = abq_command
        if shell is None:
            shell = '/bin/bash'
        self.shell_command = shell

    def run_command(self, command_string, directory=None, output=False):
        current_directory = os.getcwd()
        if directory is not None:
            os.chdir(directory)
        if output:
            job = subprocess.Popen([self.shell_command, '-i', '-c', command_string])
        else:
            f_null = open(os.devnull, 'w')
            job = subprocess.Popen([self.shell_command, '-i', '-c', command_string],
                                   stdout=f_null, stderr=subprocess.STDOUT)
        job.wait()
        os.chdir(current_directory)

    def create_empty_odb(self, new_odb_filename, odb_to_copy):
        self.run_command(self.abq + ' python create_empty_odb.py ' + str(new_odb_filename) + ' '
                         + str(odb_to_copy), directory=abaqus_python_directory)

    def read_data_from_odb(self, field_id, odb_file_name, step_name=None, frame_number=-1, set_name='',
                           instance_name='', get_position_numbers=False, get_frame_value=False,
                           position='INTEGRATION_POINT'):
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
            self.run_command(self.abq + ' python read_data_from_odb.py ' + str(parameter_pickle_name) + ' '
                             + str(results_pickle_name), directory=abaqus_python_directory)
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
                          position='INTEGRATION_POINT', invariants=None):
        with TemporaryDirectory(odb_file_name) as work_directory:
            pickle_filename = work_directory / 'load_field_to_odb_pickle.pkl'
            data_filename = work_directory / 'field_data.npy'
            np.save(str(data_filename), field_data)
            if invariants is None:
                invariants = []
            with open(pickle_filename, 'wb') as pickle_file:
                pickle.dump({'field_id': field_id, 'odb_file': odb_file_name, 'step_name': step_name,
                             'instance_name': instance_name, 'set_name': set_name, 'step_description': step_description,
                             'frame_number': frame_number, 'frame_value': frame_value,
                             'field_description': field_description, 'position': position},
                            pickle_file, protocol=2)

            self.run_command(self.abq + ' python write_data_to_odb.py ' + str(data_filename) + ' '
                             + str(pickle_filename))

    def get_data_from_path(self, path_points, odb_filename, variable, component=None, step_name=None, frame_number=None,
                           output_position='ELEMENT_NODAL'):
        odb_filename = pathlib.Path(odb_filename)
        with TemporaryDirectory(odb_filename) as work_directory:
            parameter_pickle_name = work_directory / 'parameter_pickle.pkl'
            path_points_filename = work_directory / 'path_points.npy'
            data_filename = work_directory / 'path_data.npy'
            parameter_dict = {'odb_filename': str(odb_filename),
                              'variable': variable,
                              'path_points_filename': str(path_points_filename),
                              'data_filename': str(data_filename)}
            if component is not None:
                parameter_dict['component'] = component
            if step_name is not None:
                parameter_dict['step_name'] = step_name
            if frame_number is not None:
                parameter_dict['frame_number'] = frame_number
            parameter_dict['output_position'] = output_position

            with open(parameter_pickle_name, 'wb') as pickle_file:
                pickle.dump(parameter_dict, pickle_file, protocol=2)
            if not isinstance(path_points, np.ndarray):
                path_points = np.array(path_points)
            np.save(path_points_filename, path_points)
            self.run_command(self.abq + ' viewer noGUI=write_data_along_path.py -- ' + str(parameter_pickle_name),
                             directory=abaqus_python_directory)
            data = np.unique(np.load(data_filename), axis=0)
            _, idx = np.unique(data[:, 0], return_index=True)
            return data[idx, 1]

    def get_tensor_from_path(self, odb_file_name, path_points, field_id, step_name=None, frame_number=None,
                             components=('11', '22', '33', '12', '13', '23'), output_position='INTEGRATION_POINT'):
        data = np.zeros((path_points.shape[0], len(components)))
        for i, component in enumerate(components):
            stress = self.get_data_from_path(path_points, odb_file_name, field_id, step_name=step_name,
                                             frame_number=frame_number, output_position=output_position,
                                             component=field_id + component)
            data[:, i] = stress
        return data
