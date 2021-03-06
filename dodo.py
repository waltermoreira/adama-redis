import os
import subprocess

from doit.tools import result_dep


DOIT_CONFIG = {'default_tasks': ['build']}


def task__check_images():
    """Check dependencies in the form of images"""

    img = 'adama/serfnode'
    return {
        'actions': ["docker inspect -f '{{{{ .Id }}}}' {} "
                    "2>/dev/null".format(img)]
    }


def target_image_exists(img):
    """Check if 'img' exists in local registry"""

    def f():
        try:
            subprocess.check_output(
                'docker inspect {} 1>/dev/null 2>&1'.format(img),
                shell=True)
            return True
        except subprocess.CalledProcessError:
            return False
    return f


def remote_image_exists(img):
    """Check if 'img' exists in remote registry"""

    def f():
        try:
            subprocess.check_output(
                'docker pull {} 1>/dev/null 2>&1'.format(img),
                shell=True)
            return True
        except subprocess.CalledProcessError:
            return False
    return f


def task_build():
    """Build serf-redis image"""

    all_files = ['dodo.py', 'Dockerfile']
    for d, _, fs in os.walk('handler'):
        for f in fs:
            all_files.append(os.path.join(d, f))

    return {
        'actions': ['docker build -t adama/redis .',
                    'docker inspect -f "{{ .Id }}" adama/redis > .build'],
        'targets': ['.build'],
        'file_dep': all_files,
        'task_dep': ['_check_images'],
        'uptodate': [result_dep('_check_images'),
                     target_image_exists('adama/redis')],
        'clean': True,
        'verbosity': 2
    }


def task_push():
    """Push image to docker hub"""

    return {
        'actions': ['docker push adama/redis',
                    'docker inspect -f "{{ .Id }}" adama/redis > .push'],
        'targets': ['.push'],
        'file_dep': ['.build'],
        'task_dep': ['build'],
        'uptodate': [remote_image_exists('adama/redis')],
        'verbosity': 2
    }
