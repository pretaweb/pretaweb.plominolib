from setuptools import setup, find_packages
import os

version = '0.1dev2'

long_description = (
        '\n'.join([
            open('README.md').read(),
            'Contributors',
            '============',
            open('CONTRIBUTORS.txt').read(),
            open('CHANGES.txt').read()
            ])
        )

setup(name='pretaweb.plominolib',
      version=version,
      description="Custom Plomino utilities library.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",

        ],
      keywords='',
      author='Ivan Teoh',
      author_email='ivan.teoh@pretaweb.com',
      url='https://github.com/pretaweb/pretaweb.plominolib',
      license='gpl',
      packages=find_packages('.'),
      namespace_packages=['pretaweb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.CMFPlomino',
          'plone.session',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
