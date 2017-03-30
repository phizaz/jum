from setuptools import setup

version = '0.1'

setup(
    name='jum',
    packages=['jum'],
    include_package_data=True,
    install_requires=['dill'],
    version=version,
    description='',
    author='Konpat Preechakul',
    author_email='the.akita.ta@gmail.com',
    url='https://github.com/phizaz/jum',  # use the URL to the github repo
    keywords=['cache', 'in-file'],  # arbitrary keywords
    classifiers=[],
)
