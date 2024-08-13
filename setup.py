from setuptools import setup, find_packages

setup(
    name="syndex",
    version="0.1.2",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'syndex=syndex.main:main',
        ],
    },
    install_requires=[
        # Add any required dependencies here
    ],
)
