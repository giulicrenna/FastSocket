from setuptools import setup, find_packages

setup(
    name='FastSocket',
    version='1.0.2',
    packages=find_packages(),
    description='This library is intended to create fast TCP and UDP server/client with multi connection handling.',
    long_description="""
    ![](assets/20240219_232307_logo.png)

# FastSocket

![GitHub release (latest by date)](https://img.shields.io/github/v/release/giulicrenna/FastSocket)

The FastSocket library is designed to quickly create TCP and UDP servers and clients with multi-connection handling. The library provides a simple API for setting up and managing network socket connections in Python.

## Installation

You can install FastSocket using pip:

```bash
pip install FastSocket
```

## Usage Examples

### TCP Server Example

```python
from FastSocket import FastSocketServer, SockerConfig

def handle_message(messages):
    while not messages.empty():
        msg, addr = messages.get()
        print(f'Received: {msg} from {addr}')

config = SockerConfig(host='localhost', port=8080)
server = FastSocketServer(config)
server.on_new_message(handle_message)
server.start()

```

## Contributing

If you want to contribute to FastSocket, we welcome pull requests! Before submitting a pull request, please make sure to review the contribution guidelines.

# Contact

If you have any questions, issues, or suggestions related to FastSocket, feel free to open an issue or contact the author:

*Author:* Giuliano Crenna
*Email:* giulicrenna@gmail.com

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the LICENSE file for more details.

    """,
    long_description_content_type='text/markdown',
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