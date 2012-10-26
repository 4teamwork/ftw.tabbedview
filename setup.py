from setuptools import setup, find_packages
import os

version = '3.3.2'
maintainer = 'Jonas Baumann'

tests_require = [
    'plone.app.testing',
    'ftw.testing',
    ]

extras_require = {
    'tests': tests_require,
    'extjs': ['ftw.table[extjs]'],
    'quickupload': ['collective.quickupload'],
    }

setup(name='ftw.tabbedview',
      version=version,
      description='A generic tabbed view for plone content types.',
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.0',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        ],

      keywords='ftw tabbedview table listing',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.tabbedview/',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
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
