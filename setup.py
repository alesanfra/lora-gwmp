from pathlib import Path

from setuptools import setup

project_dir = Path(__file__).parent.absolute()

with open(project_dir / "requirements.txt") as f:
    install_requires = f.read().splitlines()

with open(project_dir / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gwmp",
    packages=["gwmp"],
    scripts=["bin/gwmp"],
    version="0.0.1",
    description="Parser for GWMP messages used in LoRa and LoRaWAN networks",
    author="Alessio Sanfratello",
    url="https://github.com/alesanfra/lora-gwmp",
    install_requires=install_requires,
    python_requires=">=3.6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Intended Audience :: Telecommunications Industry",
        "Intended Audience :: Science/Research",
    ],
)
