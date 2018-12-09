from setuptools import setup, find_packages

setup(
    name='followthemoney-linker',
    version='1.4.0',
    long_description="FollowTheMoney record linkage UI",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='recordlinkage linker dedupe recon',
    author='Organized Crime and Corruption Reporting Project',
    author_email='data@occrp.org',
    url='https://occrp.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'followthemoney',
        'click',
        'flask',
        'sqlalchemy'
    ],
    test_suite='nose.collector',
    tests_require=['coverage', 'nose'],
    entry_points={
        'console_scripts': [
            'ftmlinker = followthemoney_linker.cli:cli',
        ]
    }
)
