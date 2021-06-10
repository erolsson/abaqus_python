import os
import pickle
import pathlib
import subprocess

from common import abq, create_temp_dir_name


abaqus_python_directory = pathlib.Path(__file__).parent.absolute() / "abaqus_files"


def create_empty_odb(new_odb_filename, odb_to_copy):
    os.chdir(abaqus_python_directory)
    job = subprocess.Popen(abq + ' python create_empty_odb.py ' + new_odb_filename + ' ' + odb_to_copy,
                           shell=True)
    job.wait()


def read_data_from_odb(field_id, odb_file_name, step_name=None, frame_number=-1, set_name='', instance_name='',
                       get_position_numbers=False, get_frame_value=False, position='INTEGRATION_POINT'):

    work_directory = create_temp_dir_name(odb_file_name)
    os.makedirs(work_directory)
    parameter_pickle_name = work_directory / 'parameter_pickle.pkl'
    results_pickle_name = work_directory / 'results.pkl'
    with open(parameter_pickle_name, 'wb') as pickle_file:
        pickle.dump({'field_id': field_id, 'odb_file_name': odb_file_name, 'step_name': step_name,
                     'frame_number': frame_number, 'set_name': set_name, 'instance_name': instance_name,
                     'get_position_numbers': get_position_numbers, 'get_frame_value': get_frame_value,
                     'position': position},
                    pickle_file, protocol=2)
    os.chdir(abaqus_python_directory)
    job = subprocess.Popen(abq + ' python read_data_from_odb.py ' + parameter_pickle_name + ' ' + results_pickle_name,
                           shell=True)
    job.wait()
    os.chdir('..')
    with open(results_pickle_name, 'rb') as results_pickle:
        data = pickle.load(results_pickle, encoding='latin1')
    work_directory.unlink()
    if not get_position_numbers and not get_frame_value:
        return data['data']
    elif not get_position_numbers:
        return data['data'], data['frame_value']
    elif not get_frame_value:
        return data['data'], data['node_labels'], data['element_labels']
    else:
        return data['data'], data['frame_value'], data['node_labels'], data['element_labels']


def write_data_to_odb(field_data, field_id, odb_file_name, step_name, instance_name='', set_name='',
                      step_description='', frame_number=None, frame_value=None, field_description='',
                      position='INTEGRATION_POINT'):

    work_directory = create_temp_dir_name(odb_file_name)
    os.makedirs(work_directory)
    pickle_filename = work_directory / 'load_field_to_odb_pickle.pkl'
    data_filename = work_directory / 'field_data.npy'
    np.save(data_filename, field_data)

    with open(pickle_filename, 'wb') as pickle_file:
        pickle.dump({'field_id': field_id, 'odb_file': odb_file_name, 'step_name': step_name,
                     'instance_name': instance_name, 'set_name': set_name, 'step_description': step_description,
                     'frame_number': frame_number, 'frame_value': frame_value, 'field_description': field_description,
                     'position': position},
                    pickle_file, protocol=2)

    os.chdir(abaqus_python_directory)
    job = subprocess.Popen(abq + ' python write_data_to_odb.py ' + data_filename + ' ' + pickle_filename, shell=True)
    job.wait()
    os.chdir('..')

    work_directory.unlink()
