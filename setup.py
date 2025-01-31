from setuptools import setup, find_packages

#########
# Setup #
#########

setup(
    name='supercycles',
    version='0.0.1',
    description='',
    url='',
    author='Tirsi Prebibaj',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.23.4',
        'scipy>=1.9.3',
        'matplotlib>=3.8.2',
	'pandas>=2.2.1'
        ]
    )

