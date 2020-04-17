import setuptools
from src.bubot.devices import SerialBridgeToRadio as Device

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bubot_433',
    version=Device.__version__,
    author="Razgovorov Mikhail",
    author_email="1338833@gmail.com",
    description="433 bridge for Bubot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/businka/bubot_Modbus",
    package_dir={'': 'src'},
    package_data={
        '': ['*.md', '*.json'],
    },
    packages=setuptools.find_namespace_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
		"Framework :: AsyncIO"
    ],
    python_requires='>=3.5.3',
    zip_safe=False,
    install_requires=[
        'bubot_Core',
        'serial_asyncio'
    ]
)
