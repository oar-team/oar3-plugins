#!/usr/bin/env python

from distutils.core import setup

setup(name='oar-plugin-setup',
      version='1.0',
      description='Example project to create oar plugins',
      author='Adrien Faure',
      author_email='adrien.faure@inria.fr',
      packages=['src'],
      install_requires=["oar"],
      entry_points={
            'oar.assign_func': 'oarp_assign_default = src.custom_scheduling:assign_default',
      },
     )
