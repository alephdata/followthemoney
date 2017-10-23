from setuptools import setup, find_packages

setup(
    name='followthemoney',
    version='0.2.2',
    long_description="Data model and validator for investigative graph data.",
    author='Organized Crime and Corruption Reporting Project',
    author_email='pudo@occrp.org',
    url='https://occrp.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=True,
    package_data={
        '': ['followthemoney/schema/*']
    },
    zip_safe=False,
    install_requires=[
        'six',
        'pyyaml',
        'requests[security]',
        'normality',
        'sqlalchemy',
        'backports.csv',
        'dalet>=1.3'
    ],
    test_suite='nose.collector',
    entry_points={},
    tests_require=['coverage', 'nose']
)
