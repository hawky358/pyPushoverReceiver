import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pypushoverreceiver',
    version="0.0.1",
    license='Apache Software License 2.0',
    author='hawky358',
    author_email='hawky358@users.github.com',
    description='API to receive pushover messages',
    long_description="API to receive pushover messages. With use with Home assistant",
    url='https://github.com/hawky358/pypushoverreceiver',
    packages=setuptools.find_packages(),
    setup_requires=[
        'setuptools',
        # 'requests'
        
    ],
    install_requires=[
        'requests',
        'websocket-client',
        'rel',
        
    #     'pandas',
    #     'oscrypto',
    #     'protobuf',
    #     'http-ece',
    #     'appdirs'
    ],
    python_requires = '>=3.6'
)
