from distutils.core import setup

setup(
    name='predicsis_ml_sdk',
    version='1.1.3',
    author='Michal K. Szczerbak',
    author_email='michal.szczerbak@predicsis.com',
    packages=['predicsis', 'predicsis.tests'],
    scripts=[],
    url='http://predicsis.com',
    license='LICENSE.txt',
    description='PredicSis REST API Python bindings.',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 2.5.0",
    ],
)