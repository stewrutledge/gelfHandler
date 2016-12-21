from distutils.core import setup

setup(
    name='gelfHandler',
    version='1.0.0',
    packages=['gelfHandler'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Log handler that ships in gelf format',
    long_description=open('README.txt').read(),
    author='Stewart Rutledge',
    author_email='stew.rutledge@gmail.com',
    url='https://github.com/stewrutledge/gelfHandler',
    keywords=['gelf', 'graylog', 'loghandler', 'handler']
)
