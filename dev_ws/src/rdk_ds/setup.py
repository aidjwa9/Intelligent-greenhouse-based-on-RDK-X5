import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'rdk_ds'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'audio_node = rdk_ds.audio:main',
            'control_node = rdk_ds.control:main',
            'deepseek_node = rdk_ds.new_ds:main',
            'sensor_node = rdk_ds.read_data:main',
            'mqtt_node = rdk_ds.tingscloud:main'
        ],
    },
)
