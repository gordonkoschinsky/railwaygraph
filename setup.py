from distutils.core import setup

setup(
    name='RailwayGraph',
    version='0.1.0',
    author='Frank Klein',
    author_email='nospam4gordon@gmail.com',
    packages=['railwaygraph'],
    scripts=[],
    url='http://pypi.python.org/pypi/railwaygraph/',
    license='LICENSE.txt',
    description='A double vertex graph implementation to work with railway networks..',
    long_description=open('README.txt').read(),
    install_requires=[
        "loggingextensions"
    ],
)
