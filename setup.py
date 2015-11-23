import os
import sys

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "gossip", "__version__.py")) as version_file:
    exec(version_file.read())  # pylint: disable=W0122

_INSTALL_REQUIERS = [
    'logbook>=0.12.0',
]

setup(name="gossip",
      classifiers=[
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
      ],
      description="Signaling and hooking library",
      license="BSD3",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=__version__,  # pylint: disable=E0602
      packages=find_packages(exclude=["tests"]),

      url="https://github.com/vmalloc/gossip",

      install_requires=_INSTALL_REQUIERS,
      scripts=[],
      namespace_packages=[]
      )
