from setuptools import setup, find_packages

setup(
    name='followthemoney-util',
    version='1.5.4',
    long_description="FollowTheMoney command-line tool",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='',
    author='OCCRP',
    author_email='data@occrp.org',
    url='https://occrp.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'click',
        'alephclient',
        'followthemoney',
        'followthemoney-enrich',
    ],
    test_suite='nose.collector',
    tests_require=['coverage', 'nose'],
    entry_points={
        'console_scripts': [
            'ftmutil = followthemoney_util.cli:cli',
            'ftm = followthemoney_util.cli:cli',
        ]
    }
)
