from setuptools import setup, find_packages

setup(
    name='FastSocket',
    version='1.0.0',
    packages=find_packages(),
    description='This library is intended to create fast TCP and UDP server/client with multi connection handling.',
    author="Giuliano Crenna",
    author_email="giulicrenna@gmail.com",
    url="https://github.com/giulicrenna/FastSocket",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries'
    ],
)