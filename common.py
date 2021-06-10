from __future__ import print_function
import os
try:
    import distro
except ImportError:
    import platform as distro

package_path = os.path.dirname(__file__)

if distro.linux_distribution()[0] == 'Ubuntu':
    abq = 'singularity exec --nv ' + os.path.expanduser('~/imgs/sing/abaqus-2018-centos-7.img') + \
          ' vglrun /opt/abaqus/2018/Commands/abq2018'
    abq_viewer = 'singularity exec --nv ' + os.path.expanduser('~/imgs/sing/abaqus-2018-centos-7.img') + \
                 ' vglrun -d :1 /opt/abaqus/2018/Commands/abq2018 viewer'
else:
    abq = '/scratch/users/erik/SIMULIA/CAE/2018/linux_a64/code/bin/ABQLauncher'
    abq_viewer = '/scratch/users/erik/SIMULIA/CAE/2018/linux_a64/code/bin/ABQLauncher viewer'

abaqus_function_dir = os.path.expanduser('~/railway_ballast/python/abaqus_functions')


def create_temp_dir_name(odb_file_name):
    i = 0
    work_directory = os.path.splitext(odb_file_name)[0] + '_tempdir' + str(i)
    while os.path.isdir(work_directory):
        i += 1
        work_directory = os.path.splitext(odb_file_name)[0] + '_tempdir' + str(i)
    return work_directory
