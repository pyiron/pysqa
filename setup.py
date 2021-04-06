"""
Setuptools based setup module
"""
from setuptools import setup, find_packages
import versioneer

setup(
    name='pysqa',
    version=versioneer.get_version(),
    description='pysqa - simple queue adapter',
    long_description='The goal of pysqa is to make submitting to an HPC cluster as easy as starting another subprocess. This is based on the assumption that even though modern queuing systems allow for an wide range of different configuration, most users submit the majority of their jobs with very similar parameters. Therefore pysqa allows the users to store their submission scripts as jinja2 templates for quick access. After the submission pysqa allows the users to track the progress of their jobs, delete them or enable reservations using the built-in functionality of the queuing system. The currently supported queuing systems are: LFS, MOAB, SGE, SLURM, TORQUE.',

    url='https://github.com/pyiron/pysqa',
    author='Jan Janssen',
    author_email='janssen@mpie.de',
    license='BSD',

    classifiers=['Development Status :: 5 - Production/Stable',
                 'Topic :: Scientific/Engineering :: Physics',
                 'License :: OSI Approved :: BSD License',
                 'Intended Audience :: Science/Research',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9'
                ],

    keywords='pysqa',
    packages=find_packages(exclude=["*tests*"]),
    install_requires=['defusedxml==0.7.1',
                      'jinja2==2.11.3',
                      'pandas==1.2.3',
                      'paramiko==2.7.2',
                      'pyyaml==5.4.1',
                      'tqdm==4.60.0'],
    cmdclass=versioneer.get_cmdclass(),
    )
