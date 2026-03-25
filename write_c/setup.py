from setuptools import setup, Extension

module = Extension('fastio', sources=['fastio.c'])

setup(
    name='fastio',
    version='1.0',
    description='Fast Mesh I/O Extension',
    ext_modules=[module]
)