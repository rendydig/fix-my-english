from setuptools import setup, find_packages

setup(
    name='python-do-type',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
    entry_points={
        'console_scripts': [
            'python-do-type=main:main',
        ],
    },
)
