from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='FastSocket',
    version='2.1.0',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'pycryptodome>=3.18.0',
    ],
    description='Librería Python para servidores y clientes TCP/UDP con cifrado híbrido, chunks y transferencia de archivos.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Giuliano Crenna',
    author_email='giulicrenna@gmail.com',
    url='https://github.com/giulicrenna/FastSocket',
    project_urls={
        'Documentación': 'https://giulicrenna.github.io/FastSocket/',
        'Issues': 'https://github.com/giulicrenna/FastSocket/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet',
        'Topic :: System :: Networking',
    ],
    keywords='tcp udp socket server client encryption hybrid rsa aes',
)
