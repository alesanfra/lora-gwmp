import os

from setuptools import setup

requirements = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "requirements.txt")
)
install_requires = []

if os.path.isfile(requirements):
    with open(requirements) as f:
        install_requires = f.read().splitlines()

setup(
    name="lora-gwmp",
    packages=["gwmp"],
    version="0.0.1",
    description="Parser for GWMP messages used in LoRa networks",
    author="Alessio Sanfratello",
    url="https://github.com/alesanfra/lora-gwmp",
    install_requires=install_requires,
)
