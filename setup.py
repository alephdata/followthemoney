from setuptools import setup, find_packages

setup(
    name='followthemoney',
    version='0.2',
    long_description="Data model and validator for investigative graph data.",
    keywords='',
    author='Organized Crime and Corruption Reporting Project',
    author_email='pudo@occrp.org',
    url='https://occrp.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'normality',
        'pyyaml'
    ],
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [],
    },
    tests_require=['coverage', 'nose']
)
