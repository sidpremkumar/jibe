from setuptools import setup

try:
    with open('requirements.txt', 'rb') as f:
        install_requires = f.read().decode('utf-8').split('\n')
except IOError:
    install_requires = []

try:
    with open('test-requirements.txt', 'rb') as f:
        tests_require = f.read().decode('utf-8').split('\n')
except IOError:
    tests_require = []

setup(
    name='jibe',
    version=0,
    description="Displays differences in upstream/downstream issues",
    long_description="Alerts the user if there are differences in tags, assignee, etc between upstream "
                     "sources and downstream JIRA tickets.",
    author='Sid Premkumar',
    author_email='sid.premkumar@gmail.com',
    # url='https://pagure.io/sync-to-jira',
    # license='LGPLv2+',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Lesser General "
            "Public License v2 or later (LGPLv2+)",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    packages=[
        'jibe',
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            "jibe=jibe.main:main",
        ],
    },
)