from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='ftw.tabbedview',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.js.jquery',
          'plone.app.registry',
          'ftw.table',
          'ftw.js.statusmessages',
          'ftw.js.globals'
          # -*- Extra requirements: -*-
      ],
      extras_require = {
      	            'jqueryui' : ['collective.js.jqueryui'],
      	            'jquerytools' : ['plone.app.jquerytools'],
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
