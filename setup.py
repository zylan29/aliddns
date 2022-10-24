
from setuptools import setup, find_packages

setup(
    name="aliddns",
    version="1.0.2",
    description="DDNS by using Aliyun dns service",
    author="Ziyang Li",
    packages=find_packages(),
    entry_points={
        'console_scripts':
            ['aliddns = aliddns.aliddns:main']
    },
)