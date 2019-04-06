from setuptools import setup, find_packages

setup(
    name='TreeChiPi',
    version='0.1.0',
    packages = find_packages(),
    description='Raspberry Pi Python Library for controlling TreeChiPi LED strips',
    long_description=open('README.md').read(),
    url='',
    author='Richard S. Busby',
    author_email='rsbusby@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    keywords=['RPI', 'GPIO', 'Raspberry Pi', 'LED'],
    install_requires=['RPi.GPIO', 'webcolors', 'rpi_ws281x, asyncio'],
    zip_safe=False
)
