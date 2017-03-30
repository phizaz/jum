from setuptools import setup

version = '0.3'

setup(
    name='jum',
    packages=['jum'],
    include_package_data=True,
    install_requires=['dill', 'xxhash'],
    version=version,
    description='An alternative to Joblib\'s Memory to cache python function in-file',
    author='Konpat Preechakul',
    author_email='the.akita.ta@gmail.com',
    url='https://github.com/phizaz/jum',  # use the URL to the github repo
    keywords=['cache', 'in-file'],  # arbitrary keywords
    classifiers=[],
)
