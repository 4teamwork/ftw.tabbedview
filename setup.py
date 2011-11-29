from setuptools import setup, find_packages
import os

version = open('ftw/tabbedview/version.txt').read().strip()
maintainer = 'Victor Baumann'

setup(name='ftw.tabbedview',
      version=version,
      description="" + \
          ' (Maintainer %s)' % maintainer,
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/ftw-tabbedview/',
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
        # -*- Extra requirements: -*-
        ],
      extras_require = {
        'extjs': ['ftw.table[extjs]',],
        },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
