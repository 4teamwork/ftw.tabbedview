from setuptools import setup, find_packages
import os

version = '3.5.4'
maintainer = 'Jonas Baumann'

tests_require = [
    'plone.app.testing',
    'pyquery',
    'ftw.testbrowser',
    'ftw.testing',
    ]

extras_require = {
    'tests': tests_require,
    'extjs': ['ftw.table[extjs]'],
    'quickupload': ['collective.quickupload'],
    'plone4.3': [
        'plone.batching',
        ]
    }

setup(name='ftw.tabbedview',
      version=version,
      description='A generic tabbed view for plone content types.',
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw tabbedview table listing',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.tabbedview',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'Plone',
        'setuptools',
        'ftw.table',
        'collective.js.throttledebounce',
        'plone.app.registry',
        'ftw.dictstorage',
        'ftw.upgrade',
        # -*- Extra requirements: -*-
        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points='''
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      ''',
      )
