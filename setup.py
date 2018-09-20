from setuptools import setup, find_packages

setup(name='symbionic',
      version='0.21',
      description='Code base for the Symbionic project',
      url='https://github.com/matthijscox/symbionic',
      author='Matthijs Cox',
      author_email='matthijs.cox@gmail.com',
      license='GNU General Public License v3 (GPLv3)',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'matplotlib'
      ],
      zip_safe=False,
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          'Topic :: Utilities',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3.6',
      ])